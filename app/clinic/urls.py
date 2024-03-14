from clinic.views import DoctorApi, RequestAcceptApi, TreatmentRequestApi
from clinic.viewsets import (
    BusinessHourViewSet,
    DepartmentViewSet,
    DoctorDetailViewSet,
    HospitalViewSet,
    PatientViewSet,
    UninsuredTreatmentViewSet,
)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = "clinic"
router = DefaultRouter()

router.register(r"hospitals", HospitalViewSet)
router.register(r"patients", PatientViewSet)
router.register(r"departments", DepartmentViewSet)
router.register(r"business-hours", BusinessHourViewSet)
router.register(r"uninsured-treatments", UninsuredTreatmentViewSet)
router.register(r"doctors/doctor", DoctorDetailViewSet, basename="doctor-detail")

urlpatterns = [
    path(r"doctors/", DoctorApi.as_view(), name="doctor-list"),
    path(
        r"treatment-requests/",
        include(
            [
                path("", TreatmentRequestApi.as_view(), name="treatment-request-list"),
                path(
                    r"<int:id>/accept/",
                    RequestAcceptApi.as_view(),
                    name="treatment-request-accept",
                ),
            ]
        ),
    ),
    path("", include(router.urls)),
]
