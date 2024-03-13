from clinic.models import (
    BusinessHours,
    Department,
    Doctor,
    Hospital,
    TreatmentRequest,
    UninsuredTreatment,
)
from rest_framework import serializers


class TreatmentRequestSerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(write_only=True)
    doctor_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = TreatmentRequest
        fields = [
            "id",
            "patient",
            "doctor",
            "desired_datetime",
            "created_datetime",
            "expired_datetime",
            "status",
            "patient_id",
            "doctor_id",
        ]


class BusinessHoursSerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessHours
        fields = [
            "id",
            "day",
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
    department_ids = serializers.ListField(write_only=True, required=False)
    treatment_ids = serializers.ListField(write_only=True, required=False)

    hospital = HospitalSerializer(read_only=True)
    departments = DepartmentSerializer(read_only=True, many=True)
    treatments = UninsuredTreatmentSerializer(read_only=True, many=True)
    business_hours = BusinessHoursSerializer(read_only=True, many=True, source="hours")

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
