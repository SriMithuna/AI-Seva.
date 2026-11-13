"""Service-specific intake and SLPS factor fields for the department."""

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

from .schemes import VISHWAKARMA_TRADES


def validate_upload(upload):
    if upload.size > 5 * 1024 * 1024:
        raise ValidationError("Each file must be 5 MB or smaller.")


class LabourApplicationForm(forms.Form):
    full_name = forms.CharField(max_length=150, label="Applicant name")
    mobile_number = forms.CharField(max_length=10, min_length=10, label="10-digit mobile number", widget=forms.TextInput(attrs={"inputmode": "numeric", "maxlength": "10"}))
    address = forms.CharField(max_length=500, widget=forms.Textarea(attrs={"rows": 2}))

    annual_income = forms.IntegerField(min_value=0, label="Annual family income (₹)", help_text="Used for the Economic Vulnerability factor in this application.")
    livelihood_situation = forms.ChoiceField(label="Livelihood / employment urgency", choices=[("lost", "Livelihood lost / business severely disrupted"), ("reduced", "Major income reduction"), ("unemployed", "Unemployed / irregular employment"), ("underemployed", "Underemployed"), ("stable", "Stable employment / business")])
    worker_vulnerability = forms.ChoiceField(label="Worker vulnerability", choices=[("multiple", "Multiple vulnerabilities (officer verification required)"), ("barriers", "Migrant / daily-wage / gig worker facing major barriers"), ("other", "Other vulnerable unorganised worker"), ("none", "No additional identified barriers")])
    dependents = forms.IntegerField(min_value=0, max_value=30, label="Number of family dependents")
    support_gap = forms.ChoiceField(label="Skill / financial support gap", choices=[("very_high", "Very high"), ("moderate", "Moderate"), ("low", "Low"), ("none", "No identified gap")])
    deadline_window = forms.ChoiceField(label="Time-sensitive deadline", choices=[("7", "Within 7 days"), ("15", "Within 15 days"), ("30", "Within 30 days"), ("none", "No immediate deadline")])
    service_details = forms.CharField(max_length=1500, label="Request details", widget=forms.Textarea(attrs={"rows": 4}))
    statutory_deadline_date = forms.DateField(required=False, label="Known official / statutory deadline (if applicable)", widget=forms.DateInput(attrs={"type": "date"}), help_text="Enter a date shown on an official notice or record. An officer must verify it.")
    critical_exception_reason = forms.CharField(required=False, max_length=500, label="Exceptional urgency reason (if applicable)", widget=forms.Textarea(attrs={"rows": 2}), help_text="A Critical score is provisional. An officer must verify exceptional urgency and record the confirmation.")

    vishwakarma_trade = forms.ChoiceField(label="Traditional trade", choices=[("", "Select a covered trade")] + [(trade, trade) for trade in VISHWAKARMA_TRADES])
    traditional_trade_confirm = forms.BooleanField(label="I currently practise this trade on a self-employment basis", required=False)
    applicant_age = forms.IntegerField(min_value=18, max_value=120, label="Age (years)")
    years_in_trade = forms.IntegerField(min_value=0, max_value=100, label="Years practising this trade")

    vending_activity = forms.CharField(max_length=200, label="Street-vending activity")
    vending_location = forms.CharField(max_length=200, label="Town / ULB and vending location")
    vendor_document_type = forms.ChoiceField(label="Vendor identification available", choices=[("cov", "Certificate of Vending"), ("vendor_id", "Vendor identity card"), ("lor", "Letter of Recommendation"), ("none", "None / need guidance on the applicable route")])
    vendor_document_reference = forms.CharField(max_length=100, required=False, label="Document reference (optional; do not enter Aadhaar or bank details)")

    pmkvy_pathway = forms.ChoiceField(label="PMKVY pathway", choices=[("stt", "Short-Term Training"), ("rpl", "Recognition of Prior Learning"), ("special_project", "Special Project"), ("unsure", "Not sure; request counselling")])
    job_role = forms.CharField(max_length=160, label="Preferred course / job role")
    sector = forms.CharField(max_length=120, label="Preferred sector")
    training_district = forms.CharField(max_length=120, label="Preferred district")
    training_centre = forms.CharField(max_length=180, required=False, label="Preferred training centre (if known)")
    batch_ids = forms.CharField(max_length=500, required=False, label="Preferred batch IDs (up to five, one per line)", widget=forms.Textarea(attrs={"rows": 3}))

    labour_complaint_type = forms.ChoiceField(label="SAMADHAN matter type", choices=[("claim", "Claim under a labour law"), ("industrial_dispute", "Industrial dispute"), ("termination", "Termination / dismissal"), ("general", "General employment grievance")])
    samadhan_action = forms.ChoiceField(label="SAMADHAN help needed", choices=[("new", "Prepare a new filing"), ("track", "Track an existing matter")])
    samadhan_state = forms.CharField(max_length=100, required=False, label="State / UT")
    samadhan_district = forms.CharField(max_length=100, required=False, label="District")
    samadhan_reference = forms.CharField(max_length=100, required=False, label="Existing SAMADHAN reference (for tracking)")
    employer_name = forms.CharField(max_length=200, required=False, label="Employer / establishment name")
    employer_address = forms.CharField(max_length=400, required=False, label="Employer address", widget=forms.Textarea(attrs={"rows": 2}))
    employment_start_date = forms.DateField(required=False, label="Employment start date (if known)", widget=forms.DateInput(attrs={"type": "date"}))
    employment_end_date = forms.DateField(required=False, label="Employment end date (if applicable)", widget=forms.DateInput(attrs={"type": "date"}))
    claim_amount = forms.DecimalField(required=False, min_value=0, max_digits=12, decimal_places=2, label="Claim amount (₹, if applicable)")
    relief_sought = forms.CharField(max_length=700, label="Relief requested", widget=forms.Textarea(attrs={"rows": 3}))

    enterprise_name = forms.CharField(max_length=200, label="Micro / small enterprise name")
    udyam_number = forms.CharField(max_length=30, label="Udyam Registration Number", help_text="Do not enter Aadhaar, PAN, bank credentials or OTPs.")
    msme_action = forms.ChoiceField(label="MSME Samadhaan help needed", choices=[("new", "Prepare a new delayed-payment filing"), ("track", "Track an existing filing / case")])
    msme_reference = forms.CharField(max_length=100, required=False, label="Existing Samadhaan / MSEFC reference (for tracking)")
    buyer_name = forms.CharField(max_length=200, required=False, label="Buyer name")
    buyer_address = forms.CharField(max_length=400, required=False, label="Buyer address", widget=forms.Textarea(attrs={"rows": 2}))
    purchase_order_reference = forms.CharField(max_length=100, required=False, label="Purchase / work order reference")
    invoice_number = forms.CharField(max_length=100, required=False, label="Invoice number")
    invoice_date = forms.DateField(required=False, label="Invoice date", widget=forms.DateInput(attrs={"type": "date"}))
    payment_due_date = forms.DateField(required=False, label="Contractual / payment due date (if known)", widget=forms.DateInput(attrs={"type": "date"}))
    outstanding_amount = forms.DecimalField(required=False, min_value=0, max_digits=14, decimal_places=2, label="Outstanding amount (₹)")
    economic_impact = forms.ChoiceField(label="Impact of the unpaid amount on the enterprise", choices=[("severe", "Severe — business continuity or workers at risk"), ("major", "Major cash-flow disruption"), ("significant", "Significant financial pressure"), ("manageable", "Manageable impact"), ("limited", "Limited current impact")])

    supporting_document_1 = forms.FileField(required=False, label="Supporting document (invoice / notice / employment record)", validators=[FileExtensionValidator(["pdf", "png", "jpg", "jpeg"]), validate_upload])
    supporting_document_2 = forms.FileField(required=False, label="Additional supporting document", validators=[FileExtensionValidator(["pdf", "png", "jpg", "jpeg"]), validate_upload])
    FILE_FIELDS = {"supporting_document_1": "Supporting document", "supporting_document_2": "Additional supporting document"}

    SLPS_FIELDS = {"annual_income", "economic_impact", "livelihood_situation", "worker_vulnerability", "dependents", "support_gap", "deadline_window", "statutory_deadline_date", "critical_exception_reason"}
    SERVICE_FIELDS = {
        "PM-VISHWAKARMA": {"vishwakarma_trade", "traditional_trade_confirm", "applicant_age", "years_in_trade"},
        "PM-SVANIDHI": {"vending_activity", "vending_location", "vendor_document_type", "vendor_document_reference"},
        "PMKVY": {"pmkvy_pathway", "job_role", "sector", "training_district", "training_centre", "batch_ids"},
        "PMKVY-TRAINING": {"pmkvy_pathway", "job_role", "sector", "training_district", "training_centre", "batch_ids"},
        "SAMADHAN": {"labour_complaint_type", "samadhan_action", "samadhan_state", "samadhan_district", "samadhan_reference", "employer_name", "employer_address", "employment_start_date", "employment_end_date", "claim_amount", "relief_sought", "supporting_document_1", "supporting_document_2"},
        "MSME-DELAYED-PAYMENT": {"enterprise_name", "udyam_number", "msme_action", "msme_reference", "buyer_name", "buyer_address", "purchase_order_reference", "invoice_number", "invoice_date", "payment_due_date", "outstanding_amount", "economic_impact", "supporting_document_1", "supporting_document_2"},
    }

    def __init__(self, *args, item, **kwargs):
        super().__init__(*args, **kwargs)
        self.item = item
        service_fields = self.SERVICE_FIELDS[item["code"]]
        fields_to_keep = {"full_name", "mobile_number", "address", "service_details"} | service_fields | self.SLPS_FIELDS
        if item["code"] == "MSME-DELAYED-PAYMENT":
            fields_to_keep.discard("annual_income")
        else:
            fields_to_keep.discard("economic_impact")
        fields_to_keep |= {name for name in self.FILE_FIELDS if name in service_fields}
        self.fields = {name: field for name, field in self.fields.items() if name in fields_to_keep}
        self.fields["mobile_number"].required = True
        for name in self.SLPS_FIELDS & self.fields.keys():
            self.fields[name].required = name not in {"statutory_deadline_date", "critical_exception_reason"}
        if item["code"] in {"PMKVY", "PMKVY-TRAINING"}:
            self.fields["batch_ids"].help_text = "Enter up to five live batch IDs from Skill India Digital, one per line. Leave blank if you are still exploring courses."
        if item["code"] == "SAMADHAN":
            self.fields["samadhan_action"].widget.attrs["data-samadhan-action"] = "1"
            for name in ("labour_complaint_type", "employer_name", "employer_address", "employment_start_date", "employment_end_date", "claim_amount", "relief_sought"):
                self.fields[name].required = False
            self.fields["samadhan_reference"].required = False
        if item["code"] == "MSME-DELAYED-PAYMENT":
            for name in ("buyer_name", "buyer_address", "purchase_order_reference", "invoice_number", "invoice_date", "payment_due_date", "outstanding_amount", "economic_impact"):
                self.fields[name].required = False
        if item["code"] == "PM-VISHWAKARMA":
            self.fields["traditional_trade_confirm"].required = True

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("samadhan_action") == "track" and not cleaned.get("samadhan_reference", "").strip():
            self.add_error("samadhan_reference", "Enter the official reference number to prepare a tracking request.")
        if cleaned.get("samadhan_action") == "new":
            for name in ("labour_complaint_type", "employer_name", "employer_address", "relief_sought"):
                if not cleaned.get(name):
                    self.add_error(name, "This information is needed to prepare a new grievance filing.")
        if cleaned.get("msme_action") == "track" and not cleaned.get("msme_reference", "").strip():
            self.add_error("msme_reference", "Enter the official reference number to prepare a tracking request.")
        if cleaned.get("msme_action") == "new":
            for name in ("buyer_name", "invoice_number", "invoice_date", "outstanding_amount"):
                if not cleaned.get(name):
                    self.add_error(name, "This information is needed to prepare a new delayed-payment filing.")
        return cleaned

    def clean_mobile_number(self):
        value = self.cleaned_data["mobile_number"].strip()
        if not value.isdigit() or len(value) != 10:
            raise forms.ValidationError("Enter a valid 10-digit mobile number.")
        return value

    def clean_batch_ids(self):
        value = self.cleaned_data.get("batch_ids", "")
        batches = [line.strip() for line in value.splitlines() if line.strip()]
        if len(batches) > 5:
            raise forms.ValidationError("Select no more than five batches, as permitted in the Skill India Digital process.")
        return "\n".join(batches)
