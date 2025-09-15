from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Employee, Attendance, BiometricData


# ----------------- LOGIN -----------------
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()  # mobile = username
    password = serializers.CharField()


# ----------------- USER -----------------
class UserSerializer(serializers.ModelSerializer):
    """Serializer for Django's default User model"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']


# ----------------- EMPLOYEE PROFILE -----------------
class EmployeeProfileSerializer(serializers.ModelSerializer):
    """Employee profile serializer including user info"""
    user = UserSerializer()

    class Meta:
        model = Employee
        fields = [
            'user',
            'mobile',
            'employee_id',
            'aadhaar_number', 'aadhaar_photo',
            'bank_name', 'account_number', 'ifsc_code'
        ]
        read_only_fields = ['employee_id', 'mobile']


# ----------------- ATTENDANCE -----------------
class AttendanceCheckInSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = [
            'check_in_latitude', 'check_in_longitude',
            'scan_type', 'device_id', 'status'
        ]


class AttendanceCheckOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = [
            'check_out_latitude', 'check_out_longitude',
            'scan_type', 'device_id', 'status'
        ]

# ----------------- BIOMETRIC -----------------
class BiometricRegisterSerializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(write_only=True)
    face_encoding = serializers.CharField(allow_null=True, required=False, write_only=True)

    class Meta:
        model = BiometricData
        fields = [
            'employee_id',
            'face_encoding',
            'face_registered',
            'fingerprint_registered',
            'face_registered_at',
            'fingerprint_registered_at',
            'device_id',
            'public_key',
            'status',
            'created_at',
            'last_used_at',
        ]
        read_only_fields = [
            'face_registered_at',
            'fingerprint_registered_at',
            'created_at',
            'last_used_at',
        ]

    def create(self, validated_data):
        employee_id = validated_data.pop('employee_id')
        face_encoding = validated_data.pop('face_encoding', None)

        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            raise serializers.ValidationError({"employee_id": "Invalid employee ID"})

        biometric, created = BiometricData.objects.update_or_create(
            employee=employee,
            defaults=validated_data
        )

        # TODO: Handle face_encoding storage (if required in another model/table)

        return biometric
