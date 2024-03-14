from datetime import datetime, time, timedelta

import pytest
from clinic.enums import Days, RequestStatus
from clinic.models import BusinessHour, Doctor, Patient, TreatmentRequest
from clinic.views import TreatmentRequestApi
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from pytest_django import DjangoAssertNumQueries
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_post_treatment_requests(next_weekday, doctor_with_hours, patients):
    # given
    doctor, _ = doctor_with_hours
    patient = patients[0]
    desired_datetime = datetime.combine(
        next_weekday(Days.monday.value, datetime.now()), time(10, 0)
    )

    # when
    client = APIClient()
    url = reverse("clinic:treatment-request-list")
    data = {
        "patient_id": patient.id,
        "doctor_id": doctor.id,
        "desired_datetime": desired_datetime,
    }
    res = client.post(url, data)

    # then

    assert res.status_code == 201
    assert res.data["patient"] == patient.name
    assert res.data["desired_datetime"] == desired_datetime.strftime(
        "%Y-%m-%dT%H:%M:%S"
    )


@pytest.mark.django_db
def test_accept_treatment_request(next_weekday, doctor_with_hours, patients):
    # given
    doctor, _ = doctor_with_hours
    patient = patients[0]
    desired_datetime = datetime.combine(
        next_weekday(Days.monday.value, datetime.now()), time(10, 0)
    )

    # when
    treatment_request = TreatmentRequest.objects.create(
        patient=patient, doctor=doctor, desired_datetime=desired_datetime
    )
    assert treatment_request.is_available == True
    client = APIClient()
    url = reverse("clinic:treatment-request-accept", args=[treatment_request.id])
    res = client.patch(url)

    # then
    treatment_request.refresh_from_db()
    assert res.status_code == 200
    assert treatment_request.status == RequestStatus.ACCEPTED


@pytest.mark.django_db
def test_expired_treatment_request_accept_not_allowed(
    doctor_with_hours, patients, next_weekday
):
    # given
    doctor, doctor2 = doctor_with_hours
    patient = patients[0]
    desired_datetime = datetime.combine(
        next_weekday(Days.monday.value, datetime.now()), time(10, 0)
    )

    # when
    treatment_request = TreatmentRequest.objects.create(
        patient=patient, doctor=doctor, desired_datetime=desired_datetime
    )
    treatment_request2 = TreatmentRequest.objects.create(
        patient=patient, doctor=doctor2, desired_datetime=desired_datetime
    )
    treatment_request.status = RequestStatus.EXPIRED
    treatment_request.save()
    client = APIClient()
    url = reverse("clinic:treatment-request-accept", args=[treatment_request.id])
    res = client.patch(url)

    # then
    assert res.status_code == 400
    assert treatment_request.status == RequestStatus.EXPIRED

    # when
    url = reverse("clinic:treatment-request-accept", args=[treatment_request2.id])
    res = client.patch(url)

    # then
    assert treatment_request2.is_available == False
    assert res.status_code == 400
    assert treatment_request2.status == RequestStatus.REFUSED


@pytest.mark.django_db
def test_get_treatment_requests(treatment_requests, django_assert_max_num_queries):
    # given

    # when
    client = APIClient()
    url = reverse("clinic:treatment-request-list")
    with django_assert_max_num_queries(1):
        res = client.get(url)

    serializer = TreatmentRequestApi.OutputSerializer(treatment_requests, many=True)
    # then
    assert res.status_code == 200
    assert res.data == serializer.data


@pytest.mark.django_db
def test_get_treatment_requests_by_doctor_id(
    treatment_requests, doctors, django_assert_max_num_queries
):
    # given
    doctor, _ = doctors
    treatment_requests = TreatmentRequest.objects.filter(doctor=doctor)
    half = treatment_requests.count() // 2
    for request in treatment_requests[:half]:
        request.status = RequestStatus.ACCEPTED
        request.save()
    # when
    client = APIClient()
    url = reverse("clinic:treatment-request-list")
    params = {"doctor_id": doctor.id}
    with django_assert_max_num_queries(2):
        res = client.get(url, params)

    serializer = TreatmentRequestApi.OutputSerializer(
        treatment_requests[half:], many=True
    )
    # then
    assert res.status_code == 200
    assert res.data == serializer.data


@pytest.mark.django_db
def test_request_treatment_at_closed_time():
    # given
    patient = Patient.objects.create(name="환자")
    doctor = Doctor.objects.create(name="의사")
    opening_time = time(9, 0)
    closing_time = time(18, 0)
    hours = BusinessHour.objects.create(
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
def test_request_treatment(next_weekday):
    # given
    patient = Patient.objects.create(name="환자")
    doctor = Doctor.objects.create(name="의사")
    opening_time = time(9, 0)
    closing_time = time(18, 0)
    hours = BusinessHour.objects.create(
        doctor=doctor,
        day=Days.monday.value,
        opening_time=opening_time,
        closing_time=closing_time,
    )
    desired_datetime = datetime.combine(
        next_weekday(Days.monday.value, datetime.now()).date(), opening_time
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
