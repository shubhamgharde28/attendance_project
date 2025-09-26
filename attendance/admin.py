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
    list_display = ('employee', 'face_registered', 'fingerprint_status')

    def fingerprint_status(self, obj):
        return "Yes" if obj.fingerprint_registered else "No"
    fingerprint_status.short_description = 'Fingerprint Registered'


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



from django.contrib import admin
from .models import ProjectDetail


@admin.register(ProjectDetail)
class ProjectDetailAdmin(admin.ModelAdmin):
    list_display = (
        "project_name",
        "builder_name",
        "project_type",
        "city",
        "state",
        "zipcode",
        "number_of_units",
        "launch_date",
        "possession_date",
        "created_at",
    )
    list_filter = (
        "project_type",
        "city",
        "state",
        "launch_date",
        "possession_date",
    )
    search_fields = (
        "project_name",
        "builder_name",
        "city",
        "state",
        "zipcode",
        "khasra_number",
    )
    ordering = ("-created_at",)
    date_hierarchy = "launch_date"


from django.contrib import admin
from .models import SiteVisit


@admin.register(SiteVisit)
class SiteVisitAdmin(admin.ModelAdmin):
    list_display = (
        "visitor_name",
        "visitor_mobile",
        "employee",
        "project",
        "visit_date_display",
        "visitor_status",
        "status",
        "created_at",
    )
    list_filter = ("status", "visitor_status", "project", "employee", "visit_date")
    search_fields = (
        "visitor_name",
        "visitor_mobile",
        "visitor_address",
        "employee__user__first_name",
        "employee__user__last_name",
        "project__project_name",
        "plot_number",
    )
    ordering = ("-created_at",)

    def visit_date_display(self, obj):
        return obj.visit_date if obj.visit_date else "Not Scheduled"
    visit_date_display.short_description = "Visit Date"

from django.contrib import admin
from .models import PropertyBooking


@admin.register(PropertyBooking)
class PropertyBookingAdmin(admin.ModelAdmin):
    list_display = (
        "visitor_name",
        "visitor_mobile",
        "project",
        "plot_number",
        "plot_area",
        "booking_date",
        "total_amount",
        "advance_amount",
        "remaining_amount",
        "payment_status",
        "booking_status",
    )
    list_filter = ("project", "booking_status", "payment_status", "booking_date")
    search_fields = ("visitor_name", "visitor_mobile", "plot_number")
    ordering = ("-booking_date",)


from django.contrib import admin
from .models import Service, EmployeeServiceStatus


from django.contrib import admin
from .models import Service, EmployeeServiceStatus, EmployeeReport

# ----------------- SERVICE -----------------
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")   # show these in list view
    list_filter = ("is_active",)                         # filter by active/inactive
    search_fields = ("name", "description")              # search by name/desc
    ordering = ("name",)

# ----------------- EMPLOYEE SERVICE STATUS -----------------
@admin.register(EmployeeServiceStatus)
class EmployeeServiceStatusAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "service",
        "project",
        "property_name",
        "property_area",
        "property_khasra_number",
        "status",
        "service_date",
        "updated_at",
    )
    list_filter = ("status", "service_date", "updated_at", "project")  # filter sidebar
    search_fields = (
        "employee__user__first_name",
        "employee__user__last_name",
        "employee__employee_id",
        "service__name",
        "project__project_name",
        "property_name",
        "property_khasra_number",
    )
    ordering = ("-updated_at",)
    autocomplete_fields = ("employee", "project", "service")  # dropdown with search

# ----------------- EMPLOYEE REPORT -----------------
@admin.register(EmployeeReport)
class EmployeeReportAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "attendance",
        "report_text",
        "latitude",
        "longitude",
        "created_at",
    )
    list_filter = ("created_at", "employee")  # filter sidebar
    search_fields = (
        "employee__user__first_name",
        "employee__user__last_name",
        "employee__employee_id",
        "attendance__id",
        "report_text",
    )
    ordering = ("-created_at",)
    autocomplete_fields = ("employee", "attendance")  # dropdown with search



from django.contrib import admin
from .models import WorkPlan, WorkDetail


class WorkDetailInline(admin.TabularInline):
    model = WorkDetail
    extra = 1
    fields = ("title", "target_quantity", "achieved_quantity", "status")
    readonly_fields = ("achieved_quantity", "status")  
    # ✅ employee update करेगा ये fields via API, admin सिर्फ देख सके


from django.contrib import admin
from .models import WorkPlan, WorkDetail


# ----------------- Inline for WorkDetail -----------------
class WorkDetailInline(admin.TabularInline):
    model = WorkDetail
    extra = 0
    show_change_link = True
    readonly_fields = ("achieved_quantity", "status")  # optional


# ----------------- WorkPlan Admin -----------------
@admin.register(WorkPlan)
class WorkPlanAdmin(admin.ModelAdmin):
    list_display = ("employee", "plan_type", "start_date", "end_date", "overall_progress", "created_at")
    list_filter = ("plan_type", "start_date", "end_date", "employee")
    search_fields = ("employee__employee_id", "employee__user__first_name", "employee__user__last_name")
    ordering = ("-created_at",)
    inlines = [WorkDetailInline]

# ----------------- WorkDetail Admin -----------------
@admin.register(WorkDetail)
class WorkDetailAdmin(admin.ModelAdmin):
    list_display = ("work_plan", "title", "target_quantity", "achieved_quantity", "status", "updated_at")
    list_filter = ("status", "work_plan__plan_type")
    search_fields = ("title", "work_plan__employee__employee_id", "work_plan__employee__user__first_name")
    ordering = ("-updated_at",)


