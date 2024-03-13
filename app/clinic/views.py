from clinic.selectors import get_doctors
from clinic.serializers import DoctorSerializer, TreatmentRequestSerializer
from clinic.services import create_doctor, create_request
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView


class DoctorApi(APIView):
    serializer_class = DoctorSerializer

    class FilterSerializer(serializers.Serializer):
        search = serializers.CharField(default="")
        time = serializers.DateTimeField(required=False)

    @extend_schema(
        request=FilterSerializer,
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
        doctor_id = serializers.IntegerField()

    @extend_schema(
        request=FilterSerializer,
        responses={200: TreatmentRequestSerializer(many=True)},
        tags=["Treatment Requests"],
    )
    def get(self, request):
        pass

    @extend_schema(
        request=TreatmentRequestSerializer,
        responses={200: TreatmentRequestSerializer(many=True)},
        tags=["Treatment Requests"],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        treatment_request = create_request(serializer.validated_data)

        output_serializer = self.serializer_class(treatment_request)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
