from clinic.enums import RequestStatus
from clinic.models import Doctor, TreatmentRequest
from rest_framework.exceptions import ValidationError


def create_doctor(validated_data):
    department_ids = validated_data.pop("department_ids", [])
    treatment_ids = validated_data.pop("treatment_ids", [])

    doctor = Doctor.objects.create(**validated_data)

    doctor.departments.add(*department_ids)
    doctor.treatments.add(*treatment_ids)
    return doctor


def create_request(validated_data):
    treatment_request = TreatmentRequest(**validated_data)
    if not treatment_request.is_available:
        raise ValidationError({"detail": "영업 시간이 아닙니다."})
    treatment_request.save()
    return treatment_request


def accept_request(request_id):
    try:
        treatment_request = TreatmentRequest.objects.get(request_id)
    except TreatmentRequest.DoesNotExist:
        raise ValidationError({"detail": "존재하지 않는 진료 요청입니다."})

    if treatment_request.is_expired:
        raise ValidationError({"detail": "만료된 요청입니다."})
    treatment_request.status = RequestStatus.ACCEPETED
    treatment_request.save()
    return treatment_request
