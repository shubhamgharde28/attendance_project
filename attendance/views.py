from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json

from django.contrib.auth import authenticate
from .models import Employee, Attendance, BiometricData
from .serializers import (
    LoginSerializer,
    EmployeeProfileSerializer,
    AttendanceCheckInSerializer,
    AttendanceCheckOutSerializer
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from .serializers import LoginSerializer
# ----------------- LOGIN -----------------
class EmployeeLoginView(APIView):
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mobile = serializer.validated_data['username']  # serializer uses username field for login
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

# ----------------- ATTENDANCE CHECK-IN -----------------
class AttendanceCheckInView(generics.CreateAPIView):
    serializer_class = AttendanceCheckInSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # If using default User + Employee
        employee = getattr(request.user, 'employee', request.user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        scan_type = serializer.validated_data['scan_type']
        biometric = BiometricData.objects.filter(employee=employee).first()

        if not biometric:
            return Response({"detail": "Biometric registration not found."}, status=status.HTTP_400_BAD_REQUEST)

        if scan_type == 'face' and not biometric.face_registered:
            return Response({"detail": "Face not registered."}, status=status.HTTP_400_BAD_REQUEST)
        elif scan_type == 'finger' and not biometric.fingerprint_registered:
            return Response({"detail": "Fingerprint not registered."}, status=status.HTTP_400_BAD_REQUEST)

        today = timezone.localdate()
        if Attendance.objects.filter(employee=employee, date=today).exists():
            return Response({"detail": "Already checked in today."}, status=status.HTTP_400_BAD_REQUEST)

        Attendance.objects.create(
            employee=employee,
            date=today,  # ✅ explicitly set date
            check_in_time=timezone.now(),
            scan_type=scan_type,
            check_in_latitude=serializer.validated_data['check_in_latitude'],
            check_in_longitude=serializer.validated_data['check_in_longitude'],
        )

        return Response({"detail": "Check-in successful."}, status=status.HTTP_201_CREATED)


class AttendanceCheckOutView(generics.UpdateAPIView):
    serializer_class = AttendanceCheckOutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        employee = getattr(self.request.user, 'employee', self.request.user)
        today = timezone.localdate()  # ✅ match check-in date
        return Attendance.objects.filter(
            employee=employee,
            date=today,
            check_out_time__isnull=True
        )

    def update(self, request, *args, **kwargs):
        employee = getattr(request.user, 'employee', request.user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        scan_type = serializer.validated_data['scan_type']
        biometric = BiometricData.objects.filter(employee=employee).first()

        if not biometric:
            return Response({"detail": "Biometric registration not found."}, status=status.HTTP_400_BAD_REQUEST)

        if scan_type == 'face' and not biometric.face_registered:
            return Response({"detail": "Face not registered."}, status=status.HTTP_400_BAD_REQUEST)
        elif scan_type == 'finger' and not biometric.fingerprint_registered:
            return Response({"detail": "Fingerprint not registered."}, status=status.HTTP_400_BAD_REQUEST)

        attendance_qs = self.get_queryset()
        if not attendance_qs.exists():
            return Response({"detail": "No active check-in found for today."}, status=status.HTTP_400_BAD_REQUEST)

        attendance = attendance_qs.first()
        attendance.check_out_time = timezone.now()
        attendance.scan_type = scan_type
        attendance.check_out_latitude = serializer.validated_data['check_out_latitude']
        attendance.check_out_longitude = serializer.validated_data['check_out_longitude']
        attendance.save()

        return Response({"detail": "Check-out successful."}, status=status.HTTP_200_OK)


# ----------------- BIOMETRIC REGISTER -----------------
@method_decorator(csrf_exempt, name='dispatch')
class BiometricRegisterView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            employee_id = data.get('employee_id')
            face_registered = data.get('face_registered', False)
            fingerprint_registered = data.get('fingerprint_registered', False)

            if not employee_id:
                return JsonResponse({"error": "Employee ID is required"}, status=400)

            try:
                employee = Employee.objects.get(employee_id=employee_id)
            except Employee.DoesNotExist:
                return JsonResponse({"error": "Employee not found"}, status=404)

            biometric, created = BiometricData.objects.get_or_create(employee=employee)

            if face_registered:
                biometric.face_registered = True
                biometric.face_registered_at = timezone.now()

            if fingerprint_registered:
                biometric.fingerprint_registered = True
                biometric.fingerprint_registered_at = timezone.now()

            biometric.save()

            return JsonResponse({
                "message": "Biometric status updated successfully.",
                "face_registered": biometric.face_registered,
                "fingerprint_registered": biometric.fingerprint_registered,
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
