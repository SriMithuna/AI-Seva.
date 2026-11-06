from pathlib import Path
import re

path = Path("departments/education/views.py")
content = path.read_text(encoding="utf-8")

content = content.replace(
    "from portal.forms import EducationApplicationForm",
    "from portal.forms import EducationApplicationForm, PostMatricScholarshipDetailsForm"
)

new_function = '''
@login_required
def education_apply(request, item_id):
    department = Department.objects.get(name="Education")
    item = get_object_or_404(
        Scheme, id=item_id, department=department, is_active=True
    )

    is_post_matric = "post-matric" in item.name.lower()

    if request.method == "POST":
        form = EducationApplicationForm(request.POST)
        details_form = (
            PostMatricScholarshipDetailsForm(request.POST)
            if is_post_matric else None
        )

        if form.is_valid() and (
            details_form is None or details_form.is_valid()
        ):
            application = form.save(commit=False)
            application.citizen = request.user
            application.scheme = item

            if details_form:
                application.extra_data = details_form.cleaned_data

            application.save()
            return redirect(
                "application_confirmation",
                tracking_id=application.tracking_id
            )
    else:
        form = EducationApplicationForm()
        details_form = (
            PostMatricScholarshipDetailsForm()
            if is_post_matric else None
        )

    return render(request, "education/apply.html", {
        "form": form,
        "details_form": details_form,
        "item": item,
    })
'''

content, count = re.subn(
    r'@login_required\s+def education_apply\(request, item_id\):.*\Z',
    new_function,
    content,
    flags=re.S
)

if count != 1:
    raise SystemExit("Update failed: existing function was not found.")

path.write_text(content, encoding="utf-8")
print("Education application view updated successfully!")