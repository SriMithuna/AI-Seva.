from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    LEVELS = [('Central', 'Central'), ('State', 'State')]
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)   # e.g. EDU, AGR
    description = models.TextField(blank=True)
    level = models.CharField(max_length=10, choices=LEVELS, default='Central')

    def __str__(self):
        return self.name


class Scheme(models.Model):
    """Holds both schemes and services."""
    TYPES = [('Scheme', 'Scheme'), ('Service', 'Service')]
    ACCESS = [
        ('Online', 'Fully online'),
        ('Partial', 'Online plus one visit'),
        ('Visit', 'Office visit needed'),
    ]
    name = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=10, choices=TYPES)
    description = models.TextField()
    official_link = models.URLField(blank=True)
    access_level = models.CharField(max_length=10, choices=ACCESS, default='Online')
    required_documents = models.TextField(blank=True)   # one per line
    level = models.CharField(max_length=10, default='Central')
    state = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    # Eligibility (used for schemes; leave empty for services)
    min_age = models.PositiveIntegerField(null=True, blank=True)
    max_age = models.PositiveIntegerField(null=True, blank=True)
    max_income = models.PositiveIntegerField(null=True, blank=True)
    allowed_categories = models.CharField(max_length=100, blank=True)   # e.g. "SC,ST,OBC"
    allowed_occupations = models.CharField(max_length=200, blank=True)  # e.g. "Farmer,Student"

    def __str__(self):
        return f"{self.name} ({self.item_type})"


class CategoryWeights(models.Model):
    """SLPS weights for each department. The four weights should add up to 100."""
    department = models.OneToOneField(Department, on_delete=models.CASCADE)
    income_w = models.PositiveIntegerField(default=30)
    vulnerability_w = models.PositiveIntegerField(default=30)
    waiting_w = models.PositiveIntegerField(default=20)
    documents_w = models.PositiveIntegerField(default=20)
    extra = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Weights: {self.department.name}"

class CitizenProfile(models.Model):
    CATEGORIES = [('General', 'General'), ('OBC', 'OBC'), ('SC', 'SC'), ('ST', 'ST')]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    annual_income = models.PositiveIntegerField(null=True, blank=True)
    occupation = models.CharField(max_length=50, blank=True)
    category = models.CharField(max_length=10, choices=CATEGORIES, default='General')
    state = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.user.username


class OfficerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.user.username} - {self.department.name}"    

class Application(models.Model):
    STATUSES = [
        ('Pending', 'Pending'),
        ('Under Review', 'Under Review'),
        ('More Documents', 'More documents needed'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    tracking_id = models.CharField(max_length=20, unique=True, null=True, blank=True, editable=False)
    citizen = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUSES, default='Pending')
    slps_score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.tracking_id:
            self.tracking_id = f"APP-{self.created_at.year}-{self.pk:06d}"
            super().save(update_fields=['tracking_id'])

    def __str__(self):
        return self.tracking_id or f"Application {self.pk}"


class Document(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class StatusRemark(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='remarks')
    officer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20)
    remark = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)    