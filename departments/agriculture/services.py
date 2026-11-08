from django import forms

from portal.forms import EducationApplicationForm


class AgricultureApplicantForm(EducationApplicationForm):
    """Contact fields shared by the department's separate workflows."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["full_name"].required = True
        self.fields["mobile_number"].required = True
        self.fields["mobile_number"].widget.attrs["inputmode"] = "numeric"
        self.fields["address"].required = True
        self.fields.pop("purpose")
        # Education-only fields are inherited from the shared applicant form.
        # Agriculture requests do not collect priority categories or uploads.
        self.fields.pop("priority_group", None)
        self.fields.pop("supporting_document", None)

    def clean_mobile_number(self):
        number = self.cleaned_data["mobile_number"].strip()
        if not number.isdigit() or len(number) != 10:
            raise forms.ValidationError("Enter a 10-digit mobile number.")
        return number


class FarmLocationForm(forms.Form):
    state = forms.CharField(max_length=100)
    district = forms.CharField(max_length=100)
    village = forms.CharField(max_length=100)
    survey_number = forms.CharField(max_length=60, label="Survey / plot number")
    land_area_acres = forms.DecimalField(
        max_digits=8, decimal_places=2, min_value=0.01,
        label="Cultivated land area (acres)",
    )


class PMKisanDetailsForm(FarmLocationForm):
    farmer_category = forms.ChoiceField(
        label="Landholding / farmer category",
        choices=[
            ("", "Select category"),
            ("Individual owner", "Individual owner cultivator"),
            ("Joint owner", "Joint landholder"),
            ("Other landholding", "Other landholding details (verify official rules)"),
        ],
    )
    eligibility_declaration = forms.BooleanField(
        label="I understand that land records and official exclusion rules determine eligibility.",
    )


class PMFBYDetailsForm(FarmLocationForm):
    crop_name = forms.CharField(max_length=100, label="Insured crop")
    season = forms.ChoiceField(choices=[("Kharif", "Kharif"), ("Rabi", "Rabi")])
    sowing_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    cultivator_type = forms.ChoiceField(
        label="Cultivation type",
        choices=[
            ("Owner", "Land-owning farmer"),
            ("Tenant", "Tenant farmer"),
            ("Sharecropper", "Sharecropper"),
        ],
    )
    notified_crop_check = forms.BooleanField(
        label="I will confirm the crop, area and enrollment window are notified for this season.",
    )


class KCCDetailsForm(FarmLocationForm):
    applicant_type = forms.ChoiceField(
        label="Farmer / applicant type",
        choices=[
            ("Owner cultivator", "Owner cultivator"),
            ("Tenant farmer", "Tenant farmer"),
            ("Sharecropper", "Sharecropper"),
            ("SHG", "Self-Help Group (SHG)"),
            ("JLG", "Joint Liability Group (JLG)"),
        ],
    )
    farming_type = forms.ChoiceField(
        choices=[("Crop", "Crop cultivation"), ("Dairy", "Dairy"), ("Fisheries", "Fisheries"), ("Other", "Other allied activity")],
    )
    crops_cultivated = forms.CharField(max_length=200, label="Crops / allied activity")
    credit_purpose = forms.CharField(
        max_length=250,
        label="Purpose of credit",
        widget=forms.TextInput(attrs={"placeholder": "Seeds, fertilizer, cultivation, harvesting…"}),
    )
    has_existing_agri_loan = forms.ChoiceField(
        label="Do you have an existing agricultural loan?",
        choices=[("No", "No"), ("Yes", "Yes")],
    )
    existing_loan_details = forms.CharField(
        required=False, max_length=250, label="Existing loan details (optional)",
    )
    preferred_bank = forms.CharField(max_length=120)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["survey_number"].required = False
        self.fields["land_area_acres"].required = False


class SoilHealthDetailsForm(FarmLocationForm):
    soil_type = forms.CharField(required=False, max_length=100, label="Soil type (if known)")
    current_crop = forms.CharField(max_length=100)
    sample_location = forms.CharField(
        max_length=250,
        label="Soil sample location",
        widget=forms.TextInput(attrs={"placeholder": "Field location or landmark"}),
    )


class ENAMDetailsForm(forms.Form):
    state = forms.CharField(max_length=100)
    district = forms.CharField(max_length=100)
    village = forms.CharField(max_length=100)
    email = forms.EmailField(required=True)
    preferred_apmc = forms.CharField(max_length=150, label="Preferred mandi / APMC")
    produce = forms.CharField(max_length=150, label="Produce to trade")
    bank_name = forms.CharField(
        max_length=120,
        label="Bank name (do not enter an account number)",
    )


class ENAMApplicantForm(AgricultureApplicantForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    gender = forms.ChoiceField(choices=[
        ("Male", "Male"), ("Female", "Female"), ("Other", "Other"),
    ])


DETAILS_FORMS = {
    "pm-kisan": PMKisanDetailsForm,
    "pmfby": PMFBYDetailsForm,
    "kisan-credit-card": KCCDetailsForm,
    "soil-health-card": SoilHealthDetailsForm,
    "enam-registration": ENAMDetailsForm,
}

APPLICANT_FORMS = {
    "enam-registration": ENAMApplicantForm,
}
