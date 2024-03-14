from datetime import datetime, timedelta

from clinic.enums import Days, RequestStatus
from django.db import models

DAYS_IN_WEEK = 7


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


class BusinessHour(models.Model):
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
    def 요일(self):
        return Days.choices()[self.day][1]

    @property
    def has_lunch_time(self):
        if self.lunch_start_time is not None:
            return True
        return False

    @property
    def 점심시간(self):
        if self.has_lunch_time:
            return f"{self.lunch_start_time.strftime('%H:%M')}~{self.lunch_end_time.strftime('%H:%M')}"
        return None

    @property
    def 영업시간(self):
        return f"{self.opening_time.strftime('%H:%M')}~{self.closing_time.strftime('%H:%M')}"

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

    @property
    def is_expired(self):
        if self.status == RequestStatus.EXPIRED or not self.is_available:
            return True
        if self.expired_datetime is None:
            # created_datetime 요일
            day = self.created_datetime.weekday()

            # self.doctor.hours에서 해당 요일의 영업시간 가져오기
            hours = self.doctor.hours.filter(day=day).first()

            # 해당 영업 시간과 요청 시간이 일치하는지 확인하고 만료 시간 설정
            if hours:
                self._check_business_hours(hours)

            # 일치하는 영업시간이 없다면 가장 가까운 요일의 영업시간 가져오기
            if self.expired_datetime is None:
                hours = self._find_next_business_hours(day)
                day_diff = (hours.day - day) % DAYS_IN_WEEK
                duration = timedelta(minutes=15)
                start_date = datetime.combine(
                    self.created_datetime.date() + timedelta(days=day_diff),
                    hours.opening_time,
                )
                self._set_expired_datetime(start_date, duration)

        if self.expired_datetime <= datetime.now():
            self._set_status(RequestStatus.EXPIRED)
            return True

        return False

    @property
    def is_available(self):
        # 과거의 시간으로 예약 금지
        if self.desired_datetime <= datetime.now():
            self._set_status(RequestStatus.REFUSED)
            return False
        day = self.desired_datetime.weekday()

        # self.doctor.hours 에서 해당 요일의 영업시간 가져오기
        try:
            hours = self.doctor.hours.get(day=day)
        except BusinessHour.DoesNotExist:
            self._set_status(RequestStatus.REFUSED)
            return False

        desired_time = self.desired_datetime.time()

        if self._in_range(desired_time, hours.first_session) or self._in_range(
            desired_time, hours.second_session
        ):
            return True
        self._set_status(RequestStatus.REFUSED)
        return False

    def _in_range(self, time, time_range):
        if time_range[0] <= time <= time_range[1]:
            return True
        return False

    def _find_next_business_hours(self, day):
        next_day = (day + 1) % DAYS_IN_WEEK
        hours = self.doctor.hours.filter(day__gte=next_day).order_by("day")
        if not hours.exists():
            hours = self.doctor.hours.filter(day__lte=next_day).order_by("-day")
        hours = hours.first()
        return hours

    def _set_expired_datetime(self, start_datetime, duration):
        self.expired_datetime = start_datetime + duration
        self.save()

    def _check_business_hours(self, hours):
        created_time = self.created_datetime.time()

        if self._in_range(created_time, hours.first_session) or self._in_range(
            created_time, hours.second_session
        ):
            duration = timedelta(minutes=20)
            self._set_expired_datetime(self.created_time, duration)

        elif hours.has_lunch_time and self._in_range(
            created_time, hours.lunch_time_range
        ):
            duration = timedelta(minutes=15)
            self._set_expired_datetime(self.created_time, duration)

    def _set_status(self, status):
        self.status = status
        self.save()
