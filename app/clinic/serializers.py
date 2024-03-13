from clinic.models import (
    BusinessHour,
    Department,
    Doctor,
    Hospital,
    Patient,
    TreatmentRequest,
    UninsuredTreatment,
)
from rest_framework import serializers


class BusinessHourSerializer(serializers.ModelSerializer):
    doctor_id = serializers.IntegerField()

    class Meta:
        model = BusinessHour
        fields = [
            "id",
            "day",
            "요일",
            "영업시간",
            "점심시간",
            "doctor_id",
            "opening_time",
            "closing_time",
            "lunch_start_time",
            "lunch_end_time",
        ]


class UninsuredTreatmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = UninsuredTreatment
        fields = ["id", "name"]


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ["id", "name"]


class HospitalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hospital
        fields = ["id", "name"]


class DoctorSerializer(serializers.ModelSerializer):
    hospital_id = serializers.IntegerField(write_only=True, required=False)
    department_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    treatment_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    hospital = HospitalSerializer(read_only=True)
    departments = DepartmentSerializer(read_only=True, many=True)
    treatments = UninsuredTreatmentSerializer(read_only=True, many=True)
    business_hours = BusinessHourSerializer(read_only=True, many=True, source="hours")

    class Meta:
        model = Doctor
        fields = [
            "id",
            "name",
            "hospital",
            "departments",
            "treatments",
            "business_hours",
            "hospital_id",
            "department_ids",
            "treatment_ids",
        ]

    def update(self, instance, validated_data):
        department_ids = validated_data.pop("department_ids", [])
        treatment_ids = validated_data.pop("treatment_ids", [])
        instance.departments.add(*department_ids)
        instance.treatments.add(*treatment_ids)
        return super().update(instance, validated_data)


class PatientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Patient
        fields = ["id", "name"]


class TreatmentRequestSerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(write_only=True)
    doctor_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = TreatmentRequest
        fields = [
            "id",
            "desired_datetime",
            "patient_id",
            "doctor_id",
        ]
