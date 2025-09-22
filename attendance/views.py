from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.contrib.auth import authenticate
from .models import Employee, Attendance, BiometricData
from .serializers import (
    LoginSerializer,
    EmployeeProfileSerializer,
    AttendanceCheckInSerializer,
    AttendanceCheckOutSerializer,
    BiometricRegisterSerializer,
)
from drf_yasg.utils import swagger_auto_schema


# ----------------- LOGIN -----------------
class EmployeeLoginView(APIView):
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mobile = serializer.validated_data['username']
        password = serializer.validated_data['password']

        try:
            employee = Employee.objects.get(mobile=mobile)
        except Employee.DoesNotExist:
            return Response({'error': 'Invalid mobile'}, status=400)

        user = authenticate(username=employee.user.username, password=password)
        if user is None:
            return Response({'error': 'Invalid password'}, status=400)

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'employee_id': employee.employee_id,
            'name': f"{user.first_name} {user.last_name}"
        })


# ----------------- PROFILE -----------------
class EmployeeProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        employee = request.user.employee
        serializer = EmployeeProfileSerializer(employee)
        return Response(serializer.data)

    def post(self, request):
        employee = request.user.employee
        serializer = EmployeeProfileSerializer(employee, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Profile updated successfully'})


# ----------------- ATTENDANCE -----------------
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Employee, Attendance
from .serializers import AttendanceCheckInSerializer, AttendanceCheckOutSerializer
from datetime import datetime


class AttendanceCheckInView(APIView):
    def post(self, request):
        serializer = AttendanceCheckInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        employee_id = request.data.get("employee_id")
        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Invalid employee_id"}, status=400)

        # create attendance
        Attendance.objects.create(
            employee=employee,
            check_in_time=timezone.now(),
            check_in_latitude=serializer.validated_data["check_in_latitude"],
            check_in_longitude=serializer.validated_data["check_in_longitude"],
            scan_type=serializer.validated_data["scan_type"],
            device_id=serializer.validated_data["device_id"],
            status=serializer.validated_data.get("status", "pending"),
        )

        return Response({"message": "Check-in successful"}, status=201)



class AttendanceCheckOutView(APIView):
    def post(self, request):
        serializer = AttendanceCheckOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        employee_id = request.data.get("employee_id")
        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Invalid employee_id"}, status=400)

        try:
            attendance = Attendance.objects.get(
                employee=employee,
                date=timezone.localdate(),
                check_out_time__isnull=True
            )
        except Attendance.DoesNotExist:
            return Response({"error": "No active check-in found"}, status=400)

        attendance.check_out_time = timezone.now()
        attendance.check_out_latitude = serializer.validated_data["check_out_latitude"]
        attendance.check_out_longitude = serializer.validated_data["check_out_longitude"]
        attendance.scan_type = serializer.validated_data["scan_type"]
        attendance.device_id = serializer.validated_data["device_id"]
        attendance.status = serializer.validated_data.get("status", "pending")
        attendance.save()

        return Response({"message": "Check-out successful"}, status=200)




# ----------------- BIOMETRIC REGISTER -----------------
class BiometricRegisterView(APIView):
    @swagger_auto_schema(request_body=BiometricRegisterSerializer)
    def post(self, request):
        serializer = BiometricRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        biometric = serializer.save()

        return Response({
            "message": "Biometric registration successful.",
            "face_registered": biometric.face_registered,
            "fingerprint_registered": biometric.fingerprint_registered,
            "status": biometric.status,
            "device_id": biometric.device_id,
        }, status=201)


from rest_framework import generics, permissions
from .models import Employee
from .serializers import EmployeeFullDataSerializer

class EmployeeFullDataAPIView(generics.RetrieveAPIView):
    """
    Fetch all data of an employee including profile, attendance, and biometric.
    """
    serializer_class = EmployeeFullDataSerializer
    permission_classes = [permissions.IsAuthenticated]  # optional

    def get_queryset(self):
        return Employee.objects.all()

    def get_object(self):
        employee_id = self.kwargs.get('employee_id')
        return Employee.objects.get(employee_id=employee_id)




from rest_framework import viewsets
from .models import SiteVisit
from .serializers import SiteVisitSerializer


from rest_framework import viewsets, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import SiteVisit
from .serializers import SiteVisitSerializer
from rest_framework import viewsets, permissions
from .models import ProjectDetail
from .serializers import ProjectDetailSerializer


class ProjectDetailViewSet(viewsets.ModelViewSet):
    queryset = ProjectDetail.objects.all().order_by("-created_at")
    serializer_class = ProjectDetailSerializer
    permission_classes = [permissions.IsAuthenticated]  # ✅ JWT required


class SiteVisitViewSet(viewsets.ModelViewSet):
    queryset = SiteVisit.objects.all().order_by("-created_at")
    serializer_class = SiteVisitSerializer
    authentication_classes = [JWTAuthentication]   # 👈 Require JWT
    permission_classes = [permissions.IsAuthenticated]  # 👈 Only logged in users

    # Optional: filtering
    def get_queryset(self):
        queryset = super().get_queryset()
        employee_id = self.request.query_params.get("employee")
        project_id = self.request.query_params.get("project")
        visitor_status = self.request.query_params.get("visitor_status")

        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if visitor_status:
            queryset = queryset.filter(visitor_status=visitor_status)

        return queryset



from rest_framework import viewsets, permissions
from .models import PropertyBooking
from .serializers import PropertyBookingSerializer


class PropertyBookingViewSet(viewsets.ModelViewSet):
    queryset = PropertyBooking.objects.all().order_by("-booking_date")
    serializer_class = PropertyBookingSerializer
    permission_classes = [permissions.IsAuthenticated]  # ✅ JWT required

    def get_queryset(self):
        queryset = super().get_queryset()
        employee_id = self.request.query_params.get("employee")
        project_id = self.request.query_params.get("project")
        booking_status = self.request.query_params.get("booking_status")

        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if booking_status:
            queryset = queryset.filter(booking_status=booking_status)

        return queryset

