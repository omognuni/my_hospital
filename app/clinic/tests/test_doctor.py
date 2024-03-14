from datetime import datetime, time, timedelta

import pytest
from clinic.models import BusinessHour, Doctor, UninsuredTreatment
from clinic.serializers import DoctorSerializer
from django.urls import reverse
from pytest_django import DjangoAssertNumQueries
from rest_framework.test import APIClient

DOCTOR_URL = reverse("clinic:doctor-list")


@pytest.mark.django_db
def test_create_doctor(hospital, departments):
    # given
    treatment = UninsuredTreatment.objects.create(name="다이어트약")
    data = {
        "name": "테스트",
        "hospital_id": hospital.id,
        "department_ids": [departments[0].id, departments[1].id],
        "treatment_ids": [treatment.id],
    }
    # when
    client = APIClient()
    res = client.post(DOCTOR_URL, data)

    # then
    doctor = Doctor.objects.get(name=data["name"])
    serializer = DoctorSerializer(doctor)
    assert res.status_code == 201
    assert res.data == serializer.data


@pytest.mark.django_db
def test_query_doctor_list(doctor_with_hours, django_assert_max_num_queries):
    client = APIClient()
    url = reverse("clinic:doctor-list")

    with django_assert_max_num_queries(4):
        res = client.get(url)
    serializer = DoctorSerializer(doctor_with_hours, many=True)
    assert res.status_code == 200
    assert res.data == serializer.data


@pytest.mark.django_db
def test_search_doctor_with_string(doctors, django_assert_max_num_queries):
    """
    의사 검색 로직 테스트
    """
    # given
    doctor, doctor2 = doctors
    treatment = UninsuredTreatment.objects.create(name="다이어트약")
    doctor2.treatments.add(treatment)

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
        [doctor_serializer.data],
        [doctor2_serializer.data],
        [],
    ]
    for i, params in enumerate(params_list):
        with django_assert_max_num_queries(4):
            res = client.get(DOCTOR_URL, {"search": params})
        assert res.status_code == 200
        assert res.data == answers[i]


@pytest.mark.django_db
def test_search_doctor_with_hours(doctors):
    # given
    doctor, doctor2 = doctors
    now = datetime.now()
    after = now + timedelta(days=3)

    doctor_hours = BusinessHour.objects.create(
        doctor=doctor,
        day=now.weekday(),
        opening_time=time(9, 0),
        closing_time=time(18, 0),
    )
    doctor2_hours = BusinessHour.objects.create(
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
    assert res.data == [serializer.data]

    # when
    params = {"time": datetime.combine(after.date(), time(hour=9, minute=0))}
    res = client.get(DOCTOR_URL, params)

    # then
    serializer = DoctorSerializer(doctor2)
    assert res.status_code == 200
    assert res.data == [serializer.data]
