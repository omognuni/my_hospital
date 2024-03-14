from clinic.selectors import get_doctors, get_requests
from clinic.serializers import DoctorSerializer, TreatmentRequestSerializer
from clinic.services import accept_request, create_doctor, create_request
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView


class DoctorApi(APIView):
    serializer_class = DoctorSerializer

    class FilterSerializer(serializers.Serializer):
        search = serializers.CharField(default="", required=False)
        time = serializers.DateTimeField(required=False)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="search",
                description="검색어",
                required=False,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="time",
                description="시간 필터",
                required=False,
                type=OpenApiTypes.DATETIME,
            ),
        ],
        responses={200: DoctorSerializer(many=True)},
        tags=["Doctors"],
    )
    def get(self, request):
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        doctors = get_doctors(filter_serializer.validated_data)

        output_serializer = self.serializer_class(doctors, many=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=DoctorSerializer, responses={201: DoctorSerializer}, tags=["Doctors"]
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        doctor = create_doctor(serializer.validated_data)

        output_serializer = self.serializer_class(doctor)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class TreatmentRequestApi(APIView):
    serializer_class = TreatmentRequestSerializer

    class FilterSerializer(serializers.Serializer):
        doctor_id = serializers.IntegerField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        patient = serializers.CharField(source="patient.name")
        desired_datetime = serializers.DateTimeField()
        expired_datetime = serializers.DateTimeField()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="doctor_id",
                description="의사 id",
                required=False,
                type=OpenApiTypes.INT,
            ),
        ],
        responses={200: OutputSerializer(many=True)},
        tags=["Treatment Requests"],
    )
    def get(self, request):
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        treatment_requests = get_requests(filter_serializer.validated_data)

        output_serializer = self.OutputSerializer(treatment_requests, many=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=TreatmentRequestSerializer,
        responses={201: OutputSerializer},
        tags=["Treatment Requests"],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        treatment_request = create_request(serializer.validated_data)

        output_serializer = self.OutputSerializer(treatment_request)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class RequestAcceptApi(APIView):

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        patient = serializers.CharField(source="patient.name")
        desired_datetime = serializers.DateTimeField()
        expired_datetime = serializers.DateTimeField()

    @extend_schema(
        responses={201: OutputSerializer},
        tags=["Treatment Requests"],
    )
    def patch(self, request, id):
        treatment_request = accept_request(id)

        output_serializer = self.OutputSerializer(treatment_request)
        return Response(output_serializer.data, status=status.HTTP_200_OK)
