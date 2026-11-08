
from django.db import models
from django.contrib.auth.models import User


# ==========================================
# 1. DEPARTMENT MODEL
# ==========================================

class Department(models.Model):

    LEVELS = [
        ('Central', 'Central'),
        ('State', 'State')
    ]

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    level = models.CharField(
        max_length=10,
        choices=LEVELS,
        default='Central'
    )

    def __str__(self):
        return self.name


# ==========================================
# 2. SCHEME AND SERVICE MODEL
# ==========================================

class Scheme(models.Model):

    TYPES = [
        ('Scheme', 'Scheme'),
        ('Service', 'Service')
    ]

    ACCESS = [
        ('Online', 'Fully online'),
        ('Partial', 'Online plus one visit'),
        ('Visit', 'Office visit needed')
    ]

    name = models.CharField(max_length=200)

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='items'
    )

    item_type = models.CharField(
        max_length=10,
        choices=TYPES
    )

    description = models.TextField()
    official_link = models.URLField(blank=True)

    access_level = models.CharField(
        max_length=10,
        choices=ACCESS,
        default='Online'
    )

    required_documents = models.TextField(blank=True)
    level = models.CharField(max_length=10, default='Central')
    state = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    # Eligibility information
    min_age = models.PositiveIntegerField(null=True, blank=True)
    max_age = models.PositiveIntegerField(null=True, blank=True)
    max_income = models.PositiveIntegerField(null=True, blank=True)

    allowed_categories = models.CharField(max_length=100, blank=True)
    allowed_occupations = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.name} ({self.item_type})"


# ==========================================
# 3. CATEGORY WEIGHTS MODEL
# Retained for existing department logic
# ==========================================

class CategoryWeights(models.Model):

    department = models.OneToOneField(
        Department,
        on_delete=models.CASCADE
    )

    income_w = models.PositiveIntegerField(default=30)
    vulnerability_w = models.PositiveIntegerField(default=30)
    waiting_w = models.PositiveIntegerField(default=20)
    documents_w = models.PositiveIntegerField(default=20)

    extra = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Weights: {self.department.name}"


# ==========================================
# 4. CITIZEN PROFILE MODEL
# ==========================================

class CitizenProfile(models.Model):

    CATEGORIES = [
        ('General', 'General'),
        ('BPL', 'BPL'),
        ('OBC', 'OBC'),
        ('SC', 'SC'),
        ('ST', 'ST')
    ]

    BACKGROUNDS = [
        ('RURAL', 'Rural'),
        ('SEMI-URBAN', 'Semi-Urban'),
        ('URBAN', 'Urban')
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    phone = models.CharField(max_length=15, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    annual_income = models.PositiveIntegerField(null=True, blank=True)

    occupation = models.CharField(max_length=50, blank=True)

    category = models.CharField(
        max_length=10,
        choices=CATEGORIES,
        default='General'
    )

    state = models.CharField(max_length=50, blank=True)

    # Added for Education SLPS
    background = models.CharField(
        max_length=20,
        choices=BACKGROUNDS,
        default='URBAN'
    )

    def __str__(self):
        return self.user.username


class EmailOTP(models.Model):
    """Short-lived, hashed email verification code for a new citizen account."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="email_otp")
    code_hash = models.CharField(max_length=128)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Email verification for {self.user.username}"


# ==========================================
# 5. OFFICER PROFILE MODEL
# ==========================================

class OfficerProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT
    )

    def __str__(self):
        return f"{self.user.username} - {self.department.name}"


# ==========================================
# 6. APPLICATION MODEL
# ==========================================

class Application(models.Model):

    STATUSES = [
        ('Pending', 'Pending'),
        ('Under Review', 'Under Review'),
        ('More Documents', 'More documents needed'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ]

    PRIORITIES = [
        ('Documents Pending', 'Documents Pending'),
        ('Critical', 'Critical'),
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low')
    ]

    tracking_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        editable=False
    )

    citizen = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='applications'
    )

    scheme = models.ForeignKey(
        Scheme,
        on_delete=models.CASCADE
    )

    # Applicant details
    full_name = models.CharField(max_length=150, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=30, blank=True)
    mobile_number = models.CharField(max_length=10, blank=True)
    address = models.TextField(blank=True)
    purpose = models.CharField(max_length=300, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)

    # Application status
    status = models.CharField(
        max_length=20,
        choices=STATUSES,
        default='Pending'
    )

    # SLPS information
    slps_score = models.FloatField(default=0)
    priority_group_verified = models.BooleanField(default=False)

    priority = models.CharField(
        max_length=20,
        choices=PRIORITIES,
        default='Low'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        if not self.tracking_id:
            self.tracking_id = (
                f"APP-{self.created_at.year}-{self.pk:06d}"
            )

            super().save(update_fields=['tracking_id'])

    def __str__(self):
        return self.tracking_id or f"Application {self.pk}"


# ==========================================
# 7. DOCUMENT MODEL
# ==========================================

class Document(models.Model):

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='documents'
    )

    name = models.CharField(max_length=100)

    file = models.FileField(
        upload_to='documents/'
    )

    is_verified = models.BooleanField(default=False)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.application.tracking_id}"


# ==========================================
# 8. STATUS REMARK MODEL
# ==========================================

class StatusRemark(models.Model):

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='remarks'
    )

    officer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    status = models.CharField(max_length=20)
    remark = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.application.tracking_id} - {self.status}"
