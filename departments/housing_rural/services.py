from django import forms
from django.core.validators import FileExtensionValidator

from portal.forms import EducationApplicationForm, validate_education_upload


class RuralApplicantForm(EducationApplicationForm):
    """Shared contact details for rural scheme guidance requests."""

    def __init__(self, *args, item=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("priority_group", None)
        self.fields.pop("supporting_document", None)
        self.fields.pop("purpose", None)
        self.fields["full_name"].required = True
        self.fields["mobile_number"].required = True
        self.fields["mobile_number"].widget.attrs["inputmode"] = "numeric"
        if item and item.get("code") == "NSAP":
            self.fields["date_of_birth"].required = True

    def clean_mobile_number(self):
        number = self.cleaned_data["mobile_number"].strip()
        if not number.isdigit() or len(number) != 10:
            raise forms.ValidationError("Enter a 10-digit mobile number.")
        return number


class HousingDetailsForm(forms.Form):
    village = forms.CharField(max_length=120, label="Village")
    block = forms.CharField(max_length=120, label="Block / taluk")
    district = forms.CharField(max_length=120, label="District")
    state = forms.CharField(max_length=120, label="State")
    request_details = forms.CharField(
        max_length=500, label="What guidance do you need?",
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    pmay_vertical = forms.ChoiceField(
        required=False,
        label="PMAY-U 2.0 vertical",
        choices=[
            ("", "Select a vertical"),
            ("BLC", "Beneficiary Led Construction (BLC)"),
            ("AHP", "Affordable Housing in Partnership (AHP)"),
            ("ARH", "Affordable Rental Housing (ARH)"),
            ("ISS", "Interest Subsidy Scheme (ISS)"),
        ],
    )
    nsap_pension_type = forms.ChoiceField(
        required=False,
        label="NSAP pension enquiry type",
        choices=[
            ("", "Select pension type"),
            ("old_age", "Old age pension"),
            ("widow", "Widow pension"),
            ("disability", "Disability pension"),
            ("family_benefit", "National Family Benefit Scheme"),
            ("other", "Other / unsure"),
        ],
    )
    household_members = forms.CharField(
        required=False, max_length=1200,
        label="Household members: names and ages (VB-G RAM G card registration)",
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    job_card_reference = forms.CharField(
        required=False, max_length=100,
        label="Gramin Rozgar Guarantee Card / job-card reference",
    )
    annual_income = forms.IntegerField(min_value=0, label="Approximate annual household income (₹)")
    dependents = forms.IntegerField(min_value=0, max_value=30, label="Number of dependent household members")
    vulnerability = forms.ChoiceField(
        label="Vulnerability factor (self-reported)",
        choices=[
            ("none", "None reported"),
            ("disability", "Person with disability"),
            ("older_adult", "Older adult (60+)"),
            ("widow", "Widow / widowed applicant"),
            ("other", "Other significant vulnerability"),
        ],
    )
    housing_condition = forms.ChoiceField(
        required=False,
        label="Current housing condition (PMAY requests)",
        choices=[
            ("", "Select if relevant"),
            ("adequate", "No major damage reported"),
            ("repair", "Needs significant repair"),
            ("unsafe", "Unsafe / structurally damaged"),
            ("disaster_damage", "Flood or other disaster damage"),
        ],
    )
    livelihood_hardship = forms.BooleanField(
        required=False,
        label="Significant livelihood hardship (DAY-NRLM requests)",
    )
    livelihood_details = forms.CharField(
        required=False, max_length=300, label="Brief livelihood hardship details",
    )
    employment_demand_date = forms.DateField(
        required=False,
        label="Date the official employment demand was submitted",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    nsap_application_number = forms.CharField(
        required=False, max_length=80,
        label="NSAP application number (do not enter Aadhaar or a CAPTCHA)",
    )
    is_urgent = forms.BooleanField(
        required=False,
        label="Request urgent review (officer verification required)",
    )
    urgent_reason = forms.CharField(
        required=False, max_length=500, label="Urgency details",
        widget=forms.Textarea(attrs={"rows": 2}),
    )
    income_document = forms.FileField(
        required=False, label="Income supporting document (optional)",
        validators=[FileExtensionValidator(["pdf", "png", "jpg", "jpeg"]), validate_education_upload],
    )
    vulnerability_document = forms.FileField(
        required=False, label="Vulnerability supporting document (optional)",
        validators=[FileExtensionValidator(["pdf", "png", "jpg", "jpeg"]), validate_education_upload],
    )
    household_document = forms.FileField(
        required=False, label="Household / scheme supporting document (optional)",
        validators=[FileExtensionValidator(["pdf", "png", "jpg", "jpeg"]), validate_education_upload],
    )

    DOCUMENT_FIELDS = {
        "income_document": "Income support",
        "vulnerability_document": "Vulnerability support",
        "household_document": "Household / scheme support",
    }

    def __init__(self, *args, item=None, **kwargs):
        super().__init__(*args, **kwargs)
        if item and not item.get("slps_enabled"):
            for field_name in (
                "annual_income", "dependents", "vulnerability", "is_urgent", "urgent_reason",
                "housing_condition", "livelihood_hardship", "livelihood_details",
                *self.DOCUMENT_FIELDS.keys(),
            ):
                self.fields.pop(field_name, None)
        elif item:
            if item.get("code") not in {"PMAY-G", "PMAY-U2"}:
                self.fields.pop("housing_condition", None)
            if item.get("code") != "DAY-NRLM":
                self.fields.pop("livelihood_hardship", None)
                self.fields.pop("livelihood_details", None)
        if item:
            if item.get("code") != "PMAY-U2":
                self.fields.pop("pmay_vertical", None)
            else:
                self.fields["pmay_vertical"].required = True
            if item.get("code") != "NSAP":
                self.fields.pop("nsap_pension_type", None)
            else:
                self.fields["nsap_pension_type"].required = True
            if item.get("code") != "VB-G-RAM-G":
                self.fields.pop("household_members", None)
            else:
                self.fields["household_members"].required = True
            if item.get("code") != "VB-G-EMPLOYMENT":
                self.fields.pop("job_card_reference", None)
            else:
                self.fields["job_card_reference"].required = True
            if item.get("code") != "VB-G-EMPLOYMENT":
                self.fields.pop("employment_demand_date", None)
            else:
                self.fields["employment_demand_date"].required = True
            if item.get("code") != "NSAP-STATUS":
                self.fields.pop("nsap_application_number", None)
            else:
                self.fields["nsap_application_number"].required = True

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("is_urgent") and not cleaned.get("urgent_reason", "").strip():
            self.add_error("urgent_reason", "Describe the urgent situation for officer review.")
        return cleaned
