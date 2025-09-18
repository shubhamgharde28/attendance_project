from django.urls import path, include
from .views import (
    EmployeeLoginView,
    EmployeeProfileView,
    AttendanceCheckInView,
    AttendanceCheckOutView,
    BiometricRegisterView,
    EmployeeFullDataAPIView,
    SiteVisitViewSet,
    PropertyBookingViewSet,
)
from rest_framework.routers import DefaultRouter

# Router for ViewSets
router = DefaultRouter()
router.register(r'site-visits', SiteVisitViewSet, basename='site-visit')
router.register(r'property-bookings', PropertyBookingViewSet, basename='property-booking')

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

    # Employee full data
    path('employee/<str:employee_id>/full-data/', EmployeeFullDataAPIView.as_view(), name='employee-full-data'),

    # Router URLs
    path('', include(router.urls)),
]
