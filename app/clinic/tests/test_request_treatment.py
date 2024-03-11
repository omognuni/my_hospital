from datetime import datetime, time, timedelta

import pytest
from clinic.enums import Days, RequestStatus
from clinic.models import BusinessHours, Doctor, Patient, TreatmentRequest


def get_next_weekday(weekday, date):
    day_diff = weekday - date.weekday()
    if day_diff < 0:
        day_diff = day_diff + 7
    next_weekday = date + timedelta(days=day_diff)
    return next_weekday


@pytest.mark.django_db
def test_request_treatment_at_closed_time():
    # given
    patient = Patient.objects.create(name="환자")
    doctor = Doctor.objects.create(name="의사")
    opening_time = time(9, 0)
    closing_time = time(18, 0)
    hours = BusinessHours.objects.create(
        doctor=doctor,
        day=Days.monday.value,
        opening_time=opening_time,
        closing_time=closing_time,
    )
    desired_datetime = datetime(2024, 3, 11, 8, 0)

    # when
    treatment_request = TreatmentRequest.objects.create(
        patient=patient, doctor=doctor, desired_datetime=desired_datetime
    )

    # then
    assert treatment_request.is_available == False


@pytest.mark.django_db
def test_request_treatment():
    # given
    patient = Patient.objects.create(name="환자")
    doctor = Doctor.objects.create(name="의사")
    opening_time = time(9, 0)
    closing_time = time(18, 0)
    hours = BusinessHours.objects.create(
        doctor=doctor,
        day=Days.monday.value,
        opening_time=opening_time,
        closing_time=closing_time,
    )
    desired_datetime = datetime.combine(
        get_next_weekday(hours.day, datetime.now()).date(), opening_time
    )

    # when
    treatment_request = TreatmentRequest.objects.create(
        patient=patient, doctor=doctor, desired_datetime=desired_datetime
    )

    # then
    assert treatment_request.is_expired == False
    assert treatment_request.expired_datetime == desired_datetime + timedelta(
        minutes=15
    )
    assert treatment_request.status == RequestStatus.PENDING
