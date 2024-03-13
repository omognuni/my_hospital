from datetime import datetime, timedelta

from clinic.enums import Days, RequestStatus
from django.db import models


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
    day = models.IntegerField(choices=Days.choices())
    opening_time = models.TimeField(null=True)
    lunch_start_time = models.TimeField(null=True)
    lunch_end_time = models.TimeField(null=True)
    closing_time = models.TimeField(null=True)

    class Meta:
        unique_together = (("doctor", "day"),)

    @property
    def has_lunch_time(self):
        if self.lunch_start_time is not None:
            return True
        return False

    @property
    def first_session(self):
        if self.has_lunch_time:
            return (self.opening_time, self.lunch_start_time)
        return (self.opening_time, self.closing_time)

    @property
    def lunch_time_range(self):
        if self.has_lunch_time:
            return (self.lunch_start_time, self.lunch_end_time)
        return

    @property
    def second_session(self):
        if self.has_lunch_time:
            return (self.lunch_end_time, self.closing_time)
        return self.first_session


class TreatmentRequest(models.Model):
    """
    진료 요청
    """

    patient = models.ForeignKey("Patient", on_delete=models.SET_NULL, null=True)
    doctor = models.ForeignKey("Doctor", on_delete=models.SET_NULL, null=True)
    desired_datetime = models.DateTimeField()
    created_datetime = models.DateTimeField(auto_now_add=True)
    expired_datetime = models.DateTimeField(null=True)
    status = models.CharField(
        max_length=100, choices=RequestStatus.choices(), default=RequestStatus.PENDING
    )

    def _in_range(self, time, time_range):
        if time_range[0] <= time <= time_range[1]:
            return True
        return False

    def _get_next_hours(self, day):
        day = (day + 1) % 7
        hours = self.doctor.hours.filter(day__gte=day).order_by("day")
        if not hours.exists():
            hours = self.doctor.hours.filter(day__lte=day).order_by("-day")
        hours = hours.first()
        return hours

    @property
    def is_expired(self):
        if self.status == RequestStatus.EXPIRED:
            return True
        if self.expired_datetime is None:
            # created_datetime 요일
            day = self.created_datetime.weekday()
            created_time = self.created_datetime.time()

            # self.doctor.hours에서 해당 요일의 영업시간 가져오기
            hours = self.doctor.hours.filter(day=day)
            if hours.exists():
                hours = hours.first()
                if self._in_range(created_time, hours.first_session) or self._in_range(
                    created_time, hours.second_session
                ):
                    duration = timedelta(minutes=20)
                    self.expired_datetime = self.created_datetime + duration
                elif hours.has_lunch_time and self._in_range(
                    created_time, hours.lunch_time_range
                ):
                    duration = timedelta(minutes=15)
                    self.expired_datetime = (
                        datetime.combine(
                            self.created_datetime.date(), hours.lunch_end_time
                        )
                        + duration
                    )
            # 영업시간이 없다면 가장 가까운 요일의 영업시간 가져오기
            if self.expired_datetime is None:
                hours = self._get_next_hours(day)
                day_diff = hours.day - day
                if day_diff <= 0:
                    day_diff = day_diff + 7
                duration = timedelta(minutes=15)
                expired_date = self.created_datetime.date() + timedelta(days=day_diff)
                self.expired_datetime = (
                    datetime.combine(expired_date, hours.opening_time) + duration
                )

        if self.expired_datetime <= datetime.now():
            self.status = RequestStatus.EXPIRED
            return True
        self.save()
        return False

    @property
    def is_available(self):
        # desired_datetime을 요일로 분리
        day = self.desired_datetime.weekday()

        # self.doctor.hours 에서 해당 요일의 영업시간 가져오기
        try:
            hours = self.doctor.hours.get(day=day)
        except BusinessHours.DoesNotExist:
            return False

        desired_time = self.desired_datetime.time()

        if self._in_range(desired_time, hours.first_session) or self._in_range(
            desired_time, hours.second_session
        ):
            return True

        return False
