from django.contrib import admin
from django.contrib.auth.models import User
from .models import Employee, BiometricData, Attendance

# ----------------- EMPLOYEE ADMIN -----------------
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'get_first_name', 'get_last_name', 'mobile', 'employee_id',
        'get_email', 'aadhaar_number', 'bank_name'
    )
    list_filter = ('bank_name',)
    search_fields = (
        'mobile', 'employee_id',
        'user__first_name', 'user__last_name', 'user__email'
    )
    ordering = ('employee_id',)
    readonly_fields = ('employee_id',)

    fieldsets = (
        ('User Info', {'fields': ('user', 'mobile', 'employee_id')}),
        ('Aadhaar Info', {'fields': ('aadhaar_number', 'aadhaar_photo')}),
        ('Bank Info', {'fields': ('bank_name', 'account_number', 'ifsc_code')}),
    )

    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'Last Name'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

# ----------------- BIOMETRIC DATA ADMIN -----------------


@admin.register(BiometricData)
class BiometricDataAdmin(admin.ModelAdmin):
    list_display = ('employee', 'face_registered', 'fingerprint_count')

    def fingerprint_count(self, obj):
        return obj.fingerprints.count()
    fingerprint_count.short_description = 'Fingerprint Count'

# ----------------- ATTENDANCE ADMIN -----------------
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'employee', 'date', 'check_in_time', 'check_out_time',
        'scan_type', 'check_in_latitude', 'check_in_longitude'
    )
    list_filter = ('scan_type', 'date')
    search_fields = (
        'employee__employee_id',
        'employee__user__first_name',
        'employee__user__last_name'
    )
