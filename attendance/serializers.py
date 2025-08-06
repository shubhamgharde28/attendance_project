from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Employee, Attendance, BiometricData, Fingerprint

# ----------------- LOGIN -----------------
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()  # default User model uses 'username'
    password = serializers.CharField()

# ----------------- EMPLOYEE PROFILE -----------------
class UserSerializer(serializers.ModelSerializer):
    """Serializer for Django's default User model"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']

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
class AttendanceCheckInSerializer(serializers.Serializer):
    check_in_latitude = serializers.FloatField()
    check_in_longitude = serializers.FloatField()
    scan_type = serializers.ChoiceField(choices=[('face', 'Face'), ('finger', 'Fingerprint')])

class AttendanceCheckOutSerializer(serializers.Serializer):
    check_out_latitude = serializers.FloatField()
    check_out_longitude = serializers.FloatField()
    scan_type = serializers.ChoiceField(choices=[('face', 'Face'), ('finger', 'Fingerprint')])

# ----------------- BIOMETRIC -----------------
class FingerprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fingerprint
        fields = ['index']  # Removed Base64 here because we store actual file or hash in DB

class BiometricRegisterSerializer(serializers.Serializer):
    employee_id = serializers.CharField()
    face_encoding = serializers.CharField(allow_null=True, required=False)
    fingerprints = FingerprintSerializer(many=True)
