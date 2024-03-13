from clinic.views import DoctorApi, TreatmentRequestApi
from clinic.viewsets import (
    BusinessHoursViewSet,
    DepartmentViewSet,
    DoctorDetailViewSet,
    HospitalViewSet,
    UninsuredTreatmentViewSet,
)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = "clinic"
router = DefaultRouter()

router.register(r"hospital", HospitalViewSet)
router.register(r"department", DepartmentViewSet)
router.register(r"business-hours", BusinessHoursViewSet)
router.register(r"uninsured-treatment", UninsuredTreatmentViewSet)
router.register(r"doctors/doctor", DoctorDetailViewSet, basename="doctor-detail")

urlpatterns = [
    path(r"doctors/", DoctorApi.as_view(), name="doctor-list"),
    path(
        r"treatment-requests/",
        TreatmentRequestApi.as_view(),
        name="treatment-request-list",
    ),
    path("", include(router.urls)),
]
