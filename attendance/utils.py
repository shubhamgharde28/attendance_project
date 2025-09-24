# attendance/utils.py
from django.utils import timezone
from datetime import timedelta
from .models import Attendance, EmployeeReport

def check_missing_reports():
    now = timezone.now()
    active_attendances = Attendance.objects.filter(
        check_in_time__isnull=False,
        check_out_time__isnull=True
    )

    for attendance in active_attendances:
        last_report = EmployeeReport.objects.filter(attendance=attendance).order_by("-created_at").first()

        if not last_report:
            # No report at all since check-in
            last_time = attendance.check_in_time
        else:
            last_time = last_report.created_at

        if now - last_time > timedelta(minutes=30):
            # 🔔 Trigger alert (Email/SMS/Push Notification)
            print(f"ALERT: Employee {attendance.employee.employee_id} missed half-hourly report.")
