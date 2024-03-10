from enum import Enum


class Days(Enum):
    monday = 0  # 월요일
    tuesday = 1  # 화요일
    wednesday = 2  # 수요일
    thursday = 3  # 목요일
    friday = 4  # 금요일
    saturday = 5  # 토요일
    sunday = 6  # 일요일

    @classmethod
    def choices(cls):
        return tuple((x.value, x.name) for x in cls)

    @classmethod
    def values(cls):
        return tuple(x.value for x in cls)

    def __str__(self):
        return self.name


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
