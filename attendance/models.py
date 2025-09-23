from django.db import models
from django.contrib.auth.models import User
import random
import string
from django.db import models
from django.db import models
from django.db import models
from django.utils import timezone
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
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


class ProjectDetail(models.Model):
    PROJECT_TYPE_CHOICES = [
        ("residential", "Residential"),
        ("commercial", "Commercial"),
        ("mixed_use", "Mixed Use"),
        ("plots", "Plots"),
        ("township", "Township"),
        ("apartment", "Apartment"),
        ("other", "Other"),
    ]

    project_name = models.CharField(max_length=255)
    builder_name = models.CharField(max_length=255, verbose_name="Builder/Developer Name")
    project_type = models.CharField(max_length=50, choices=PROJECT_TYPE_CHOICES)

    # Location
    city = models.CharField(max_length=100)
    address = models.TextField()
    khasra_number = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20)

    # Project details
    number_of_units = models.PositiveIntegerField()
    launch_date = models.DateField(blank=True, null=True)
    possession_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Project Detail"
        verbose_name_plural = "Project Details"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.project_name} ({self.city}, {self.state})"



class SiteVisit(models.Model):
    VISIT_STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    VISITOR_INTEREST_CHOICES = [
        ("interested", "Interested"),
        ("not_interested", "Not Interested"),
    ]

    # Relations
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="site_visits"
    )
    project = models.ForeignKey(
        ProjectDetail, on_delete=models.CASCADE, related_name="site_visits"
    )

    # Visit info
    visit_date = models.DateField(blank=True, null=True)   # ✅ made optional
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=VISIT_STATUS_CHOICES, default="scheduled"
    )

    # Visitor info
    visitor_name = models.CharField(max_length=255)
    plot_number = models.CharField(max_length=50, blank=True, null=True)
    visitor_mobile = models.CharField(max_length=15)
    visitor_address = models.TextField(blank=True, null=True)
    visitor_status = models.CharField(
        max_length=20, choices=VISITOR_INTEREST_CHOICES, default="interested"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Visit"
        verbose_name_plural = "Site Visits"
        ordering = ["-visit_date", "-created_at"]

    def __str__(self):
        return f"{self.visitor_name} - {self.project.project_name} ({self.visit_date})"


class PropertyBooking(models.Model):
    BOOKING_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("partial", "Partial"),
        ("paid", "Paid"),
    ]

    # Relations
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="bookings"
    )
    project = models.ForeignKey(
        ProjectDetail, on_delete=models.CASCADE, related_name="bookings"
    )

    # Visitor Info
    visitor_name = models.CharField(max_length=255)
    visitor_mobile = models.CharField(max_length=15)
    visitor_address = models.TextField(blank=True, null=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    # Booking Info
    plot_number = models.CharField(max_length=50, blank=True, null=True)
    plot_area = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # in sqft/m²

    booking_date = models.DateField(default=timezone.localdate)

    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    advance_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    remaining_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending"
    )
    booking_status = models.CharField(
        max_length=20, choices=BOOKING_STATUS_CHOICES, default="pending"
    )

    remarks = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Property Booking"
        verbose_name_plural = "Property Bookings"
        ordering = ["-booking_date", "-created_at"]

    def __str__(self):
        return f"{self.visitor_name} - {self.project.project_name} ({self.plot_number or 'N/A'})"

    def save(self, *args, **kwargs):
        # Auto-calculate remaining amount
        self.remaining_amount = self.total_amount - self.advance_amount
        super().save(*args, **kwargs)


class Service(models.Model):
    """Services defined by admin (like 7/12, Sale Deed, Registry, etc.)"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)  # admin can deactivate old services
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ["name"]

    def __str__(self):
        return self.name


class EmployeeServiceStatus(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("delayed", "Delayed"),
        ("completed", "Completed"),
    ]

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="service_statuses"
    )
    project = models.ForeignKey(
        ProjectDetail, on_delete=models.CASCADE, related_name="service_statuses"
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="statuses"
    )

    # 🔹 Property Details
    property_name = models.CharField(max_length=255)  # e.g., "Flat A-101", "Shop No. 12"
    property_area = models.FloatField(blank=True, null=True)  # sqft/m²
    property_khasra_number = models.CharField(max_length=100, blank=True, null=True)

    # 🔹 Service Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    reason = models.TextField(blank=True, null=True)  # mandatory if pending/delayed
    remarks = models.TextField(blank=True, null=True)  # optional

    # 🔹 Meta Info
    service_date = models.DateField(default=timezone.localdate)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Employee Service Status"
        verbose_name_plural = "Employee Service Statuses"
        unique_together = ("employee", "service", "project", "property_name")

    def __str__(self):
        return f"{self.employee.employee_id} - {self.service.name} ({self.project.project_name} - {self.property_name})"

    def clean(self):
        """Ensure reason is mandatory if not completed"""
        if self.status in ["pending", "delayed"] and not self.reason:
            raise ValidationError("Reason is required for pending or delayed services.")
