from django import forms

from portal.forms import EducationApplicationForm


class RuralApplicantForm(EducationApplicationForm):
    """Shared contact details for rural scheme guidance requests."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("priority_group", None)
        self.fields.pop("supporting_document", None)
        self.fields["full_name"].required = True
        self.fields["mobile_number"].required = True
        self.fields["mobile_number"].widget.attrs["inputmode"] = "numeric"

    def clean_mobile_number(self):
        number = self.cleaned_data["mobile_number"].strip()
        if not number.isdigit() or len(number) != 10:
            raise forms.ValidationError("Enter a 10-digit mobile number.")
        return number


class RuralDetailsForm(forms.Form):
    village = forms.CharField(max_length=120, label="Village")
    block = forms.CharField(max_length=120, label="Block / taluk")
    district = forms.CharField(max_length=120, label="District")
    state = forms.CharField(max_length=120, label="State")
    request_details = forms.CharField(
        max_length=500, label="What guidance do you need?",
        widget=forms.Textarea(attrs={"rows": 3}),
    )
