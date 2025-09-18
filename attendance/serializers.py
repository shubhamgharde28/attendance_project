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

# ----------------- EMPLOYEE FULL DATA -----------------
from datetime import date

class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = [
            'date',
            'check_in_time', 'check_in_latitude', 'check_in_longitude',
            'check_out_time', 'check_out_latitude', 'check_out_longitude',
            'scan_type', 'device_id', 'status'
        ]


class EmployeeFullDataSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    attendance_records = AttendanceRecordSerializer(many=True, source='attendance_set')
    biometric_data = BiometricRegisterSerializer(read_only=True)
    present_days_in_month = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            'user',
            'mobile',
            'employee_id',
            'aadhaar_number', 'aadhaar_photo',
            'bank_name', 'account_number', 'ifsc_code',
            'attendance_records',
            'biometric_data',
            'present_days_in_month',
        ]

    def get_present_days_in_month(self, obj):
        """Count attendance days with at least a check-in in the current month"""
        today = date.today()
        return Attendance.objects.filter(
            employee=obj,
            date__year=today.year,
            date__month=today.month,
            check_in_time__isnull=False
        ).count()



from rest_framework import serializers
from .models import SiteVisit


class SiteVisitSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(
        source="employee.user.get_full_name", read_only=True
    )
    project_name = serializers.CharField(
        source="project.project_name", read_only=True
    )

    class Meta:
        model = SiteVisit
        fields = [
            "id",
            "employee",
            "employee_name",
            "project",
            "project_name",
            "visit_date",
            "latitude",
            "longitude",
            "remarks",
            "status",
            "visitor_name",
            "plot_number",
            "visitor_mobile",
            "visitor_address",
            "visitor_status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("created_at", "updated_at")



from rest_framework import serializers
from .models import PropertyBooking


class PropertyBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyBooking
        fields = "__all__"   # include all fields
        read_only_fields = ("id", "created_at", "updated_at", "remaining_amount")

    def validate(self, data):
        total = data.get("total_amount", 0)
        advance = data.get("advance_amount", 0)
        if advance > total:
            raise serializers.ValidationError("Advance amount cannot be greater than total amount.")
        return data
