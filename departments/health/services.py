from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils import timezone


def validate_health_upload(upload):
    if upload.size > 5 * 1024 * 1024:
        raise ValidationError("Each file must be 5 MB or smaller.")


class HealthApplicationForm(forms.Form):
    full_name = forms.CharField(max_length=150, label="Applicant / patient name")
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    gender = forms.ChoiceField(label="Gender", choices=[("F", "Female"), ("M", "Male"), ("O", "Other")])
    mobile_number = forms.CharField(max_length=10, min_length=10, label="10-digit mobile number", widget=forms.TextInput(attrs={"inputmode": "numeric", "maxlength": "10"}))
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}), max_length=500)

    category = forms.ChoiceField(required=False, choices=[
        ("disabled", "Person with disability"), ("widow", "Widow"),
        ("orphan", "Orphan"), ("destitute", "Destitute"),
        ("sc_st", "SC / ST"), ("eligible", "Other eligible category"),
        ("general", "General / none of these"),
    ], help_text="Self-reported information is for experimental officer-side queue support; it does not decide eligibility.")
    income = forms.DecimalField(required=False, min_value=0, max_digits=12, decimal_places=2, label="Annual household income (₹)")
    dependents = forms.IntegerField(required=False, min_value=0, max_value=30, label="Number of dependents")
    has_prior_benefit = forms.ChoiceField(required=False, label="Have you received a related benefit before?", choices=[("No", "No"), ("Yes", "Yes")])
    is_urgent = forms.BooleanField(required=False, label="I am requesting urgent administrative review")
    urgent_reason = forms.CharField(required=False, max_length=300, label="Reason for urgent administrative review", help_text="Do not include diagnosis, treatment details or emergency information.", widget=forms.Textarea(attrs={"rows": 2}))
    is_rural = forms.ChoiceField(required=False, label="Residence background", choices=[("yes", "Rural"), ("no", "Urban or semi-urban")])

    state = forms.CharField(required=False, max_length=100)
    district = forms.CharField(required=False, max_length=100)
    family_reference = forms.CharField(required=False, max_length=100, label="Family / ration-card reference (do not enter Aadhaar)")
    beneficiary_reference = forms.CharField(required=False, max_length=80, label="Non-sensitive beneficiary reference")
    identity_consent = forms.BooleanField(required=False, label="I understand identity verification happens on the official portal or at an authorised facility; AI Seva will not collect Aadhaar numbers or OTPs.")
    identity_method = forms.ChoiceField(required=False, choices=[("", "Select"), ("Aadhaar on official portal", "Aadhaar authentication on official portal"), ("Facility-supported method", "Another method supported by a participating facility")])
    preferred_abha_address = forms.CharField(required=False, max_length=80, label="Preferred ABHA address (optional)")

    application_stage = forms.ChoiceField(required=False, choices=[("", "Select application stage")])
    pregnancy_registration_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    lmp_date = forms.DateField(required=False, label="Last menstrual period (LMP) date", widget=forms.DateInput(attrs={"type": "date"}))
    anc_first_date = forms.DateField(required=False, label="ANC check-up date (optional)", widget=forms.DateInput(attrs={"type": "date"}))
    anc_second_date = forms.DateField(required=False, label="Additional ANC check-up date (optional)", widget=forms.DateInput(attrs={"type": "date"}))
    expected_delivery_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    delivery_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    child_birth_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    child_order = forms.ChoiceField(required=False, choices=[("", "Select"), ("first", "First child"), ("second", "Second child"), ("later", "Another child"), ("unsure", "Not sure")])
    child_gender = forms.ChoiceField(required=False, choices=[("", "Select"), ("F", "Girl"), ("M", "Boy"), ("unknown", "Not recorded")])
    eligibility_basis = forms.ChoiceField(required=False, choices=[
        ("", "Select applicable basis"), ("income", "Income-based category"),
        ("sc_st", "SC / ST category"), ("mgnrega", "MGNREGA job card"),
        ("e_shram", "e-Shram card"), ("bpl", "BPL ration card"),
        ("other", "Other current official category"), ("unsure", "Not sure; ask an authorised worker"),
    ])
    jsy_eligibility_category = forms.ChoiceField(required=False, choices=[
        ("", "Select applicable category"), ("bpl", "BPL"), ("sc", "SC"),
        ("st", "ST"), ("not_sure", "Not sure; ask a health worker"),
    ])
    health_facility = forms.CharField(required=False, max_length=160, label="Health facility")
    facility_type = forms.ChoiceField(required=False, choices=[
        ("", "Select facility type"), ("government", "Government health facility"),
        ("accredited_private", "Accredited private facility"), ("not_sure", "Not sure; confirm with a health worker"),
    ])
    bank_name = forms.CharField(required=False, max_length=120)
    bank_account_last4 = forms.CharField(required=False, max_length=4, min_length=4, label="Last 4 digits of account")
    ifsc_code = forms.CharField(required=False, max_length=11, label="IFSC code")

    consultation_type = forms.ChoiceField(required=False, choices=[("", "Select"), ("patient", "Patient consultation"), ("provider", "Health worker consultation")])
    preferred_language = forms.ChoiceField(required=False, choices=[("", "Select"), ("English", "English"), ("Tamil", "Tamil"), ("Other", "Other")])
    health_concern = forms.CharField(required=False, max_length=500, label="Brief health concern", help_text="Share only what you want to discuss with a clinician. AI Seva does not assess symptoms.", widget=forms.Textarea(attrs={"rows": 3}))

    PROFILE_FIELDS = {"full_name", "date_of_birth", "gender", "mobile_number", "address"}
    SLPS_FIELDS = {"category", "income", "dependents", "has_prior_benefit", "is_urgent", "urgent_reason", "is_rural"}

    def __init__(self, *args, item, initial=None, **kwargs):
        super().__init__(*args, initial=initial, **kwargs)
        self.item = item
        initial = initial or {}
        step_fields = {
            name
            for step in item["steps"]
            for name in step.get("fields", [])
        }
        keep = step_fields
        if item["slps_enabled"]:
            keep |= self.SLPS_FIELDS
        self.fields = {name: field for name, field in self.fields.items() if name in keep}
        if "address" in step_fields:
            self.fields["address"].required = True

        if item.get("stage_choices"):
            self.fields["application_stage"].choices = item["stage_choices"]
            if not (self.data or {}).get("application_stage"):
                self.fields["application_stage"].initial = item.get("default_stage", "")

        posted_stage = (self.data or {}).get("application_stage") or initial.get("application_stage") or item.get("default_stage", "")
        self.stage = posted_stage
        conditional_documents = item.get("conditional_documents", {})
        self.document_labels = list(item.get("documents", []))
        all_conditional_labels = [label for labels in conditional_documents.values() for label in labels]
        self.document_labels.extend(label for label in all_conditional_labels if label not in self.document_labels)
        self.required_document_labels = list(item.get("documents", [])) + list(conditional_documents.get(posted_stage, []))

        required_fields = set(item.get("fields", [])) - set(item.get("optional_fields", []))
        if item.get("stage_required_fields"):
            required_fields |= set(item["stage_required_fields"].get(posted_stage, []))
        for field_name in item.get("fields", []):
            if field_name in self.fields:
                self.fields[field_name].required = field_name in required_fields
        for field_name in self.fields:
            if field_name in self.SLPS_FIELDS:
                self.fields[field_name].required = field_name not in {"is_urgent", "urgent_reason"}
        for index, label in enumerate(self.document_labels, start=1):
            self.fields[f"document_{index}"] = forms.FileField(
                label=label,
                required=label in self.required_document_labels,
                validators=[FileExtensionValidator(["pdf", "png", "jpg", "jpeg"]), validate_health_upload],
            )
        self.fields["mobile_number"].widget.attrs.update({"autocomplete": "tel", "inputmode": "numeric", "maxlength": "10"})

    def clean_mobile_number(self):
        value = self.cleaned_data["mobile_number"].strip()
        if not value.isdigit():
            raise ValidationError("Enter a valid 10-digit mobile number.")
        return value

    def clean_date_of_birth(self):
        value = self.cleaned_data["date_of_birth"]
        if value > timezone.localdate():
            raise ValidationError("Date of birth cannot be in the future.")
        return value

    def clean_bank_account_last4(self):
        value = self.cleaned_data.get("bank_account_last4", "").strip()
        if value and not value.isdigit():
            raise ValidationError("Enter only the last four digits.")
        return value

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("is_urgent") and not cleaned.get("urgent_reason", "").strip():
            self.add_error("urgent_reason", "Add a short administrative reason for officer review.")
        return cleaned
