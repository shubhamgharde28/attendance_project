from django.urls import path
from .views import (
    EmployeeLoginView,
    EmployeeProfileView,
    AttendanceCheckInView,
    AttendanceCheckOutView,
    BiometricRegisterView,
    EmployeeFullDataAPIView,
)

urlpatterns = [
    # Authentication
    path('login/', EmployeeLoginView.as_view(), name='employee-login'),

    # Profile
    path('profile/', EmployeeProfileView.as_view(), name='employee-profile'),

    # Attendance
    path('attendance/check-in/', AttendanceCheckInView.as_view(), name='attendance-checkin'),
    path('attendance/check-out/', AttendanceCheckOutView.as_view(), name='attendance-checkout'),

    # Biometric
    path('biometric/register/', BiometricRegisterView.as_view(), name='biometric-register'),

    path('employee/<str:employee_id>/full-data/', EmployeeFullDataAPIView.as_view(), name='employee-full-data'),
]
