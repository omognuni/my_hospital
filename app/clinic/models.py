from __future__ import annotations

from collections.abc import Iterable

from clinic.enums import Days, RequestStatus
from django.db import models


# Create your models here.
class Hospital(models.Model):
    name = models.CharField(max_length=200, blank=True)


class Patient(models.Model):
    name = models.CharField(max_length=200, blank=True)


class Doctor(models.Model):
    name = models.CharField(max_length=200)
    hospital = models.ForeignKey(
        "Hospital", on_delete=models.SET_NULL, related_name="doctors", null=True
    )
    departments = models.ManyToManyField(
        "Department", through="DoctorDepartment", related_name="doctors"
    )
    treatments = models.ManyToManyField(
        "UninsuredTreatment", through="DoctorTreatment", related_name="doctors"
    )


class Department(models.Model):
    """
    진료과
    """

    name = models.CharField(max_length=200, unique=True)

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        return super().save(*args, **kwargs)


class DoctorDepartment(models.Model):
    """
    의사 - 진료과 간의 중간 테이블
    """

    doctor = models.ForeignKey("Doctor", on_delete=models.CASCADE)
    department = models.ForeignKey("Department", on_delete=models.CASCADE)


class DoctorTreatment(models.Model):
    """
    의사 - 비급여진료과목 간의 중간 테이블
    """

    doctor = models.ForeignKey("Doctor", on_delete=models.CASCADE)
    treatment = models.ForeignKey("UninsuredTreatment", on_delete=models.CASCADE)


class UninsuredTreatment(models.Model):
    """
    비급여진료과목
    """

    name = models.CharField(max_length=200, unique=True)

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        return super().save(*args, **kwargs)


class BusinessHours(models.Model):
    """
    영업시간
    """

    doctor = models.ForeignKey("Doctor", on_delete=models.CASCADE, related_name="hours")
    day = models.CharField(max_length=100, choices=Days.choices())
    opening_time = models.TimeField(null=True)
    lunch_time = models.TimeField(null=True)
    closing_time = models.TimeField(null=True)


class TreatmentRequest(models.Model):
    """
    진료 요청
    """

    patient = models.ForeignKey("Patient", on_delete=models.SET_NULL, null=True)
    doctor = models.ForeignKey("Doctor", on_delete=models.SET_NULL, null=True)
    desired_datetime = models.DateTimeField()
    expired_datetime = models.DateTimeField(null=True)
    status = models.CharField(
        max_length=100, choices=RequestStatus.choices(), default=RequestStatus.PENDING
    )

    def is_expired(self):
        return
