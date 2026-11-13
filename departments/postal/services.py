from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils import timezone


def validate_upload(upload):
    if upload.size > 5 * 1024 * 1024:
        raise ValidationError("Each file must be 5 MB or smaller.")


class PostalApplicationForm(forms.Form):
    full_name = forms.CharField(max_length=150, label="Applicant / claimant name")
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    mobile_number = forms.CharField(max_length=10, min_length=10, label="10-digit mobile number")
    address = forms.CharField(required=False, max_length=500, widget=forms.Textarea(attrs={"rows": 2}))
    child_name = forms.CharField(required=False, max_length=150, label="Girl child's name")
    child_dob = forms.DateField(required=False, label="Girl child's date of birth", widget=forms.DateInput(attrs={"type": "date"}))
    relationship = forms.CharField(required=False, max_length=60, label="Relationship to child")
    initial_deposit = forms.DecimalField(required=False, min_value=0, max_digits=12, decimal_places=2, label="Planned initial deposit (₹)")
    account_count = forms.IntegerField(required=False, min_value=1, max_value=10, label="Number of accounts already opened for this child")
    retirement_status = forms.ChoiceField(required=False, choices=[("", "Select"), ("retired", "Retired"), ("not_retired", "Not retired"), ("other", "Other / unsure")])
    retirement_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    deposit_amount = forms.DecimalField(required=False, min_value=0, max_digits=12, decimal_places=2, label="Planned deposit amount (₹)")
    account_holder_type = forms.ChoiceField(required=False, label="Account holder", choices=[("", "Select"), ("self", "Myself"), ("minor", "Minor child (guardian applies)")])
    post_office = forms.CharField(required=False, max_length=150, label="Concerned post office")
    transaction_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    tracking_number = forms.CharField(required=False, max_length=100, label="Article tracking / transaction reference")
    complaint_category = forms.ChoiceField(required=False, label="Complaint category", choices=[("", "Select"), ("delay", "Delayed delivery"), ("lost", "Lost article"), ("damage", "Damaged article"), ("conduct", "Staff behaviour"), ("other", "Other postal issue")])
    complaint_description = forms.CharField(required=False, max_length=2000, widget=forms.Textarea(attrs={"rows": 4}))
    policy_number = forms.CharField(required=False, max_length=100, label="Policy number")
    claim_type = forms.ChoiceField(required=False, label="Claim type", choices=[("", "Select"), ("maturity", "Maturity"), ("survival", "Survival benefit"), ("death", "Death claim")])
    policyholder_name = forms.CharField(required=False, max_length=150)
    event_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    claim_description = forms.CharField(required=False, max_length=2000, label="Claim / account details", widget=forms.Textarea(attrs={"rows": 4}))
    deceased_name = forms.CharField(required=False, max_length=150, label="Deceased account holder's name")
    account_number = forms.CharField(required=False, max_length=100, label="Account reference (avoid sharing passwords or PINs)")
    claimant_relationship = forms.CharField(required=False, max_length=100, label="Relationship to account holder")
    nomination_status = forms.ChoiceField(required=False, label="Nomination status", choices=[("", "Select"), ("nominee", "Valid nominee recorded"), ("no_nominee", "No nominee recorded"), ("unsure", "Unsure")])

    def __init__(self, *args, item, **kwargs):
        super().__init__(*args, **kwargs)
        self.item = item
        keep = set(item.get("fields", [])) | {"full_name", "mobile_number", "address"}
        self.fields = {name: field for name, field in self.fields.items() if name in keep}
        required = (set(item.get("fields", [])) - set(item.get("optional_fields", []))) | {"full_name", "mobile_number"}
        docs = list(item.get("documents", []))
        extra_docs = [label for labels in item.get("conditional_documents", {}).values() for label in labels]
        self.document_labels = docs + [label for label in extra_docs if label not in docs]
        optional_docs = set(item.get("documents_optional", []))
        self.required_document_labels = [label for label in docs if label not in optional_docs]
        for name in self.fields:
            self.fields[name].required = name in required
        for index, label in enumerate(self.document_labels, 1):
            self.fields[f"document_{index}"] = forms.FileField(
                label=label, required=label in self.required_document_labels,
                validators=[FileExtensionValidator(["pdf", "png", "jpg", "jpeg"]), validate_upload],
            )

    def clean_mobile_number(self):
        value = self.cleaned_data["mobile_number"].strip()
        if not value.isdigit():
            raise ValidationError("Enter a valid 10-digit mobile number.")
        return value

    def clean(self):
        cleaned = super().clean()
        dob = cleaned.get("child_dob") or cleaned.get("date_of_birth")
        if dob and dob > timezone.localdate():
            self.add_error("child_dob" if cleaned.get("child_dob") else "date_of_birth", "Date of birth cannot be in the future.")
        return cleaned
