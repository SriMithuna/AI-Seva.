
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from portal.models import Application


def validate_education_upload(upload):
    if upload.size > 5 * 1024 * 1024:
        raise ValidationError("Each file must be 5 MB or smaller.")

class CitizenRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150,
        label="Full Name",
        widget=forms.TextInput(attrs={
            "placeholder": "Enter your full name"
        })
    )

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "placeholder": "Choose a username"
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "placeholder": "Enter your email address"
        })
    )

    phone = forms.CharField(
        max_length=15,
        label="Phone number",
        widget=forms.TextInput(attrs={
            "placeholder": "10-digit mobile number",
            "inputmode": "numeric",
            "autocomplete": "tel",
        }),
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Create a password"
        })
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Re-enter your password"
        })
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "username",
            "email",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if not phone.isdigit() or len(phone) != 10:
            raise ValidationError("Enter a valid 10-digit mobile number.")
        return phone


class EmailOTPForm(forms.Form):
    code = forms.CharField(
        label="6-digit email code",
        min_length=6,
        max_length=6,
        widget=forms.TextInput(attrs={
            "placeholder": "Enter 6-digit code",
            "inputmode": "numeric",
            "autocomplete": "one-time-code",
        }),
    )

    def clean_code(self):
        code = self.cleaned_data["code"].strip()
        if not code.isdigit():
            raise ValidationError("Enter the six digits from your email.")
        return code

class EducationApplicationForm(forms.ModelForm):
    priority_group = forms.ChoiceField(
        required=False,
        label="Priority category (self-reported)",
        help_text="Choose the closest applicable category. An officer must verify supporting evidence.",
        choices=[
            ("", "Select if applicable"),
            ("orphan_or_pwd", "Orphan or person with disability"),
            ("sc_st", "SC or ST"),
            ("minority_obc", "Minority or OBC"),
            ("girl_student", "Girl student"),
            ("general", "General / none of the above"),
        ],
    )
    supporting_document = forms.FileField(
        required=False,
        label="Supporting document (optional)",
        help_text="An officer must verify uploaded documents before they affect the SLPS document factor.",
        validators=[FileExtensionValidator(["pdf", "png", "jpg", "jpeg"]), validate_education_upload],
    )

    def __init__(self, *args, require_slps_profile=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["full_name"].required = True
        if require_slps_profile:
            # Education SLPS uses date of birth for its age factor and gender
            # can distinguish the girl-student category after verification.
            self.fields["date_of_birth"].required = True
            self.fields["gender"].required = True
        self.fields["mobile_number"].required = True

    class Meta:
        model = Application
        fields = [
            "full_name",
            "date_of_birth",
            "gender",
            "mobile_number",
            "address",
            "purpose",
        ]

        widgets = {
            "full_name": forms.TextInput(attrs={
                "placeholder": "Enter your full name"
            }),
            "date_of_birth": forms.DateInput(attrs={
                "type": "date"
            }),
            "gender": forms.Select(choices=[
                ("Male", "Male"),
                ("Female", "Female"),
                ("Other", "Other"),
            ]),
            "mobile_number": forms.TextInput(attrs={
                "placeholder": "10-digit mobile number",
                "maxlength": "10"
            }),
            "address": forms.Textarea(attrs={
                "placeholder": "Enter your address",
                "rows": 3
            }),
            "purpose": forms.TextInput(attrs={
                "placeholder": "Purpose of application"
            }),
        }

    def clean_mobile_number(self):
        value = self.cleaned_data["mobile_number"].strip()
        if not value.isdigit() or len(value) != 10:
            raise forms.ValidationError("Enter a 10-digit mobile number.")
        return value

class PostMatricScholarshipDetailsForm(forms.Form):

    CATEGORY_CHOICES = [
        ("SC", "SC"),
        ("ST", "ST"),
        ("OBC", "OBC"),
        ("GENERAL", "General"),
    ]

    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        label="Community Category"
    )

    annual_income = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        label="Annual Family Income (₹)",
        min_value=0,
    )

    course_name = forms.CharField(
        max_length=150,
        label="Course Name",
        widget=forms.TextInput(attrs={
            "placeholder": "Example: B.E Computer Science"
        })
    )

    current_year = forms.ChoiceField(
        choices=[
            ("1", "First Year"),
            ("2", "Second Year"),
            ("3", "Third Year"),
            ("4", "Fourth Year"),
        ],
        label="Current Academic Year"
    )

    institution_name = forms.CharField(
        max_length=200,
        label="College / Institution Name"
    )

    previous_percentage = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        label="Previous Academic Percentage",
        min_value=0,
        max_value=100
    )


# ==========================================
# 2. CENTRAL SECTOR SCHOLARSHIP FORM
# ==========================================

class CentralSectorScholarshipForm(forms.Form):
    category = forms.ChoiceField(choices=[
        ("GENERAL", "General"),
        ("SC", "SC"),
        ("ST", "ST"),
        ("OBC", "OBC"),
    ])
    board_name = forms.CharField(max_length=150, label="Class 12 Board")
    passing_year = forms.IntegerField(min_value=2000, max_value=2035)
    class_12_percentage = forms.DecimalField(
        max_digits=5, decimal_places=2, min_value=0, max_value=100
    )
    board_merit_details = forms.CharField(
        max_length=200,
        label="Board merit-list / percentile details",
        help_text="Enter the information available on your Class 12 board result.",
    )
    institution_name = forms.CharField(max_length=200)
    course_name = forms.CharField(max_length=150)
    current_year = forms.ChoiceField(choices=[
        ("1", "First Year"), ("2", "Second Year"),
        ("3", "Third Year"), ("4", "Fourth Year"),
    ])
    annual_income = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    bank_name = forms.CharField(max_length=150)
    bank_account_last4 = forms.CharField(
        max_length=4, min_length=4, label="Last 4 digits of bank account"
    )
    ifsc_code = forms.CharField(max_length=11)
    application_type = forms.ChoiceField(
        label="Application type",
        choices=[("Fresh", "Fresh"), ("Renewal", "Renewal")],
    )
    other_scholarship = forms.ChoiceField(
        label="Other scholarship or fee reimbursement received?",
        choices=[("No", "No"), ("Yes", "Yes"), ("Not sure", "Not sure")],
    )
    class_12_marksheet = forms.FileField(
        label="Class 12 marksheet",
        validators=[FileExtensionValidator(["pdf", "png", "jpg", "jpeg"]), validate_education_upload],
    )
    admission_proof = forms.FileField(
        label="Bonafide, college ID or admission proof",
        validators=[FileExtensionValidator(["pdf", "png", "jpg", "jpeg"]), validate_education_upload],
    )
    income_certificate = forms.FileField(
        required=False,
        label="Income certificate (if required)",
        validators=[FileExtensionValidator(["pdf", "png", "jpg", "jpeg"]), validate_education_upload],
    )
    previous_year_marksheet = forms.FileField(
        required=False,
        label="Previous-year marksheet (for renewal)",
        validators=[FileExtensionValidator(["pdf", "png", "jpg", "jpeg"]), validate_education_upload],
    )


# ==========================================
# 3. PM VIDYALAXMI FORM
# ==========================================

class PMVidyalaxmiForm(forms.Form):
    institution_name = forms.CharField(max_length=200)
    course_name = forms.CharField(max_length=150)
    admission_year = forms.IntegerField(min_value=2000, max_value=2035)
    course_duration = forms.IntegerField(min_value=1, max_value=10)
    annual_course_fee = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    loan_amount_required = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    annual_family_income = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    bank_name = forms.CharField(max_length=150)
    admission_letter = forms.FileField(
        required=False,
        label="Admission Letter (Demo Upload)",
        validators=[FileExtensionValidator(["pdf", "png", "jpg", "jpeg"]), validate_education_upload],
    )
    fee_structure = forms.FileField(
        required=False,
        label="Fee Structure (Demo Upload)",
        validators=[FileExtensionValidator(["pdf", "png", "jpg", "jpeg"]), validate_education_upload],
    )


# ==========================================
# 4. NSP STUDENT REGISTRATION FORM
# ==========================================

class NSPStudentRegistrationForm(forms.Form):
    domicile_state = forms.CharField(max_length=100)
    institution_name = forms.CharField(max_length=200)
    course_name = forms.CharField(max_length=150)
    academic_year = forms.CharField(max_length=20)
    category = forms.ChoiceField(choices=[
        ("GENERAL", "General"), ("SC", "SC"),
        ("ST", "ST"), ("OBC", "OBC")
    ])
    annual_family_income = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    bank_name = forms.CharField(max_length=150)
    bank_account_last4 = forms.CharField(
        max_length=4, min_length=4, label="Last 4 digits of bank account"
    )
    ifsc_code = forms.CharField(max_length=11)


# ==========================================
# 5. ABC ID CREATION FORM
# ==========================================

class ABCCreationForm(forms.Form):
    institution_name = forms.CharField(max_length=200)
    admission_number = forms.CharField(max_length=50)
    course_name = forms.CharField(max_length=150)
    admission_year = forms.IntegerField(min_value=2000, max_value=2035)
    registration_number = forms.CharField(max_length=50)
    identity_reference = forms.CharField(
        max_length=50,
        label="Identity verification reference (do not enter Aadhaar number)"
    )


# ==========================================
# 6. SCHOLARSHIP STATUS & DOCUMENT
#    VERIFICATION FORM
# ==========================================

class ScholarshipDocumentVerificationForm(forms.Form):
    scholarship_application_id = forms.CharField(max_length=50)
    scholarship_name = forms.CharField(max_length=150)
    academic_year = forms.CharField(max_length=20)
    document_type = forms.ChoiceField(choices=[
        ("Income Certificate", "Income Certificate"),
        ("Community Certificate", "Community Certificate"),
        ("Mark Sheet", "Mark Sheet"),
        ("Bonafide Certificate", "Bonafide Certificate"),
        ("Bank Passbook", "Bank Passbook"),
        ("Other", "Other"),
    ])
    document = forms.FileField(
        required=False,
        label="Upload Document (Demo)",
        validators=[FileExtensionValidator(["pdf", "png", "jpg", "jpeg"]), validate_education_upload],
    )
    applicant_remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Additional Remarks"
    )

