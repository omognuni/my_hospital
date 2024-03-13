from clinic.models import (
    BusinessHours,
    Department,
    Doctor,
    Hospital,
    UninsuredTreatment,
)
from clinic.serializers import (
    BusinessHoursSerializer,
    DepartmentSerializer,
    DoctorSerializer,
    HospitalSerializer,
    UninsuredTreatmentSerializer,
)
from rest_framework import mixins, viewsets


class DoctorDetailViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer


class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class UninsuredTreatmentViewSet(viewsets.ModelViewSet):
    queryset = UninsuredTreatment.objects.all()
    serializer_class = UninsuredTreatmentSerializer


class BusinessHoursViewSet(viewsets.ModelViewSet):
    queryset = BusinessHours.objects.all()
    serializer_class = BusinessHoursSerializer
