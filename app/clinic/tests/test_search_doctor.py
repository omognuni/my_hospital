import pytest
from clinic.enums import Days, RequestStatus
from clinic.models import (
    BusinessHours,
    Department,
    Doctor,
    Hospital,
    Patient,
    TreatmentRequest,
    UninsuredTreatment,
)
from django.urls import reverse
from rest_framework.test import APIClient

DOCTOR_URL = reverse("clinic:doctor-list")


@pytest.fixture
def hospital():
    return Hospital.objects.create(name="메라키병원")


@pytest.fixture
def doctors_and_departments(hospital):
    doctor = Doctor.objects.create(name="손웅래", hospital=hospital)
    doctor2 = Doctor.objects.create(name="선재원", hospital=hospital)
    department_names = ["정형외과", "내과", "일반의", "한의사"]
    departments = [Department.objects.create(name=name) for name in department_names]
    doctor.departments.add(*departments[:3])
    doctor2.departments.add(*departments[2:])
    return doctor, doctor2, departments


@pytest.mark.django_db
def test_search_doctor_with_string(doctors_and_departments):
    # given
    doctor, doctor2, departments = doctors_and_departments

    # when
    client = APIClient()
    params_list = [
        "일반의",
        "메라키",
        "메라키 손웅래",
        "한의사 선재원",
        "다이어트 손웅래",
    ]
    answers = [2, 2, doctor.name, doctor2.name, None]
    # params = {
    #     'search': '일반의'
    # }
    for i, params in enumerate(params_list):
        res = client.get(DOCTOR_URL, params)
        assert res.status_code == 200
