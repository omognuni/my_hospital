from datetime import datetime, time, timedelta

import pytest
from clinic.enums import Days
from clinic.models import (
    BusinessHour,
    Department,
    Doctor,
    Hospital,
    Patient,
    TreatmentRequest,
)


def get_next_weekday(weekday, date):
    day_diff = weekday - date.weekday()
    if day_diff < 0:
        day_diff = day_diff + 7
    next_weekday = date + timedelta(days=day_diff)
    return next_weekday


@pytest.fixture
def next_weekday():
    return get_next_weekday


@pytest.fixture
def hospital():
    return Hospital.objects.create(name="메라키병원")


@pytest.fixture
def departments():
    department_names = ["정형외과", "내과", "일반의", "한의사"]
    departments = [Department.objects.create(name=name) for name in department_names]
    return departments


@pytest.fixture
def doctors(hospital, departments):
    doctor = Doctor.objects.create(name="손웅래", hospital=hospital)
    doctor2 = Doctor.objects.create(name="선재원", hospital=hospital)
    doctor.departments.add(*departments[:3])
    doctor2.departments.add(*departments[2:])
    return doctor, doctor2


@pytest.fixture
def patients():
    patients = [
        Patient.objects.create(name="김환자"),
        Patient.objects.create(name="이환자"),
        Patient.objects.create(name="박환자"),
        Patient.objects.create(name="최환자"),
        Patient.objects.create(name="유환자"),
    ]
    return patients


@pytest.fixture
def doctor_with_hours(doctors):
    doctor, doctor2 = doctors
    opening_time = time(9, 0)
    closing_time = time(19, 0)
    # 평일만 넣기
    for day in Days.values()[:5]:
        BusinessHour.objects.create(
            doctor=doctor,
            day=day,
            opening_time=opening_time,
            closing_time=closing_time,
        )
    opening_time = time(9, 0)
    closing_time = time(19, 0)
    # 주말만 넣기
    for day in Days.values()[5:]:
        BusinessHour.objects.create(
            doctor=doctor2,
            day=day,
            opening_time=opening_time,
            closing_time=closing_time,
        )
    return doctor, doctor2


@pytest.fixture
def treatment_requests(doctor_with_hours, patients):
    doctor, doctor2 = doctor_with_hours
    desired_datetime = datetime.combine(
        get_next_weekday(Days.monday.value, datetime.now()), time(10, 0)
    )
    requests = []
    for patient in patients:
        requests.append(
            TreatmentRequest.objects.create(
                doctor=doctor, patient=patient, desired_datetime=desired_datetime
            )
        )
        requests.append(
            TreatmentRequest.objects.create(
                doctor=doctor2, patient=patient, desired_datetime=desired_datetime
            )
        )
    return requests
