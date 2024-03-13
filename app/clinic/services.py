from clinic.models import Department, Doctor, Hospital, UninsuredTreatment
from django.http import Http404


def create_doctor(validated_data):
    department_ids = validated_data.pop("department_ids", [])
    treatment_ids = validated_data.pop("treatment_ids", [])

    doctor = Doctor.objects.create(**validated_data)
    # try:
    #     hospital = Hospital.objects.get(id=hospital_id)
    # except Hospital.ObjectDoesNotExist:
    #     raise Http404('존재하지 않는 병원입니다.')
    # departments = Department.objects.filter(id__in=department_ids)
    # treatments = UninsuredTreatment.objects.filter(id__in=treatment_ids)
    doctor.departments.add(*department_ids)
    doctor.treatments.add(*treatment_ids)
    return doctor


def create_request(validated_data):
    return
