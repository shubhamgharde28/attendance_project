from django.db import models
from django.contrib.auth.models import User
import random
import string

# ----------------- UTILITY -----------------

def generate_employee_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

NATIONALIZED_BANKS = [
    ("SBI", "State Bank of India"),
    ("PNB", "Punjab National Bank"),
    ("BOI", "Bank of India"),
    ("CBI", "Central Bank of India"),
    ("BOB", "Bank of Baroda"),
    ("UBI", "Union Bank of India"),
    ("CANARA", "Canara Bank"),
    ("IOB", "Indian Overseas Bank"),
    ("IDBI", "IDBI Bank"),
    ("INDIAN", "Indian Bank"),
]

# ----------------- EMPLOYEE MODEL -----------------


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee")
    mobile = models.CharField(max_length=10, unique=True)
    employee_id = models.CharField(max_length=8, unique=True, default=generate_employee_id, editable=False)

    aadhaar_number = models.CharField(max_length=12, blank=True, null=True)
    aadhaar_photo = models.ImageField(upload_to='aadhaar_photos/', blank=True, null=True)

    bank_name = models.CharField(max_length=50, blank=True, null=True)
    account_number = models.CharField(max_length=20, blank=True, null=True)
    ifsc_code = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.employee_id}"


# ----------------- BIOMETRIC DATA -----------------

from django.db import models

class BiometricData(models.Model):
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name="biometric_data"   # 👈 add this
    )
    face_registered = models.BooleanField(default=False)
    fingerprint_registered = models.BooleanField(default=False)
    face_registered_at = models.DateTimeField(null=True, blank=True)
    fingerprint_registered_at = models.DateTimeField(null=True, blank=True)
    device_id = models.CharField(max_length=255)
    public_key = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee.employee_id} Biometric"




# ----------------- ATTENDANCE MODEL -----------------

class Attendance(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_in_latitude = models.FloatField(null=True, blank=True)
    check_in_longitude = models.FloatField(null=True, blank=True)

    check_out_time = models.DateTimeField(null=True, blank=True)
    check_out_latitude = models.FloatField(null=True, blank=True)
    check_out_longitude = models.FloatField(null=True, blank=True)

    scan_type = models.CharField(max_length=10, choices=[('face', 'Face'), ('finger', 'Fingerprint')])
    date = models.DateField(auto_now_add=True)

    # 🔹 New fields
    device_id = models.CharField(max_length=255)  # Must match registered device (BiometricData.device_id)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"{self.employee.employee_id} - {self.date} ({self.status})"

    class Meta:
        ordering = ['-date']
        unique_together = ('employee', 'date')
