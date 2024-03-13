from clinic.models import (
    BusinessHour,
    Department,
    Doctor,
    Hospital,
    Patient,
    UninsuredTreatment,
)
from clinic.serializers import (
    BusinessHourSerializer,
    DepartmentSerializer,
    DoctorSerializer,
    HospitalSerializer,
    PatientSerializer,
    UninsuredTreatmentSerializer,
)
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, viewsets


@extend_schema(tags=["Doctors"])
class DoctorDetailViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer


@extend_schema(tags=["Patients"])
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


@extend_schema(tags=["Hospitals"])
class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer


@extend_schema(tags=["Departments"])
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


@extend_schema(tags=["Uninsured Treatments"])
class UninsuredTreatmentViewSet(viewsets.ModelViewSet):
    queryset = UninsuredTreatment.objects.all()
    serializer_class = UninsuredTreatmentSerializer


@extend_schema(tags=["Business Hours"])
class BusinessHourViewSet(viewsets.ModelViewSet):
    queryset = BusinessHour.objects.all()
    serializer_class = BusinessHourSerializer
