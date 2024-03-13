from datetime import datetime, time, timedelta

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
from clinic.serializers import DoctorSerializer
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

    doctor_serializer = DoctorSerializer(doctor)
    doctor2_serializer = DoctorSerializer(doctor2)
    list_serializer = DoctorSerializer([doctor, doctor2], many=True)

    answers = [
        list_serializer.data,
        list_serializer.data,
        doctor_serializer.data,
        doctor2_serializer.data,
        None,
    ]
    for i, params in enumerate(params_list):
        res = client.get(DOCTOR_URL, params)
        assert res.status_code == 200
        assert res.data == answers[i]


@pytest.mark.django_db
def test_search_doctor_with_hours(doctors_and_departments):
    # given
    doctor, doctor2, departments = doctors_and_departments
    now = datetime.now()
    after = now + timedelta(days=3)

    doctor_hours = BusinessHours.objects.create(
        doctor=doctor,
        day=now.weekday(),
        opening_time=time(9, 0),
        closing_time=time(18, 0),
    )
    doctor2_hours = BusinessHours.objects.create(
        doctor=doctor,
        day=after.weekday(),
        opening_time=time(9, 0),
        closing_time=time(18, 0),
    )

    doctor.hours.add(doctor_hours)
    doctor2.hours.add(doctor2_hours)

    # when
    client = APIClient()
    params = {"time": datetime.combine(now.date(), time(hour=15, minute=0))}
    res = client.get(DOCTOR_URL, params)

    # then
    serializer = DoctorSerializer(doctor)
    assert res.status_code == 200
    assert res.data == serializer.data

    # when
    params = {"time": datetime.combine(after.date(), time(hour=9, minute=0))}

    # then
    serializer = DoctorSerializer(doctor2)
    assert res.status_code == 200
    assert res.data == serializer.data
