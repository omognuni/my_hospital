from __future__ import annotations

from enum import Enum


class Days(str, Enum):
    MON = "monday"
    TUE = "tuesday"
    WED = "wednesday"
    THU = "thursday"
    FRI = "friday"
    SAT = "saturday"
    SUN = "sunday"

    @classmethod
    def choices(cls):
        return tuple((x.value, x.name) for x in cls)

    @classmethod
    def values(cls):
        return (x.value for x in cls)

    def __str__(self):
        return self.value


class RequestStatus(str, Enum):
    PENDING = "대기중"
    ACCEPETED = "수락됨"
    REFUSED = "거절됨"
    EXPIRED = "만료됨"

    @classmethod
    def choices(cls):
        return tuple((x.value, x.name) for x in cls)

    @classmethod
    def values(cls):
        return (x.value for x in cls)

    def __str__(self):
        return self.value
