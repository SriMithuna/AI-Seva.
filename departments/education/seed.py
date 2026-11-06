from portal.models import Department, Scheme

from .schemes import EDUCATION_SCHEMES
from .services import EDUCATION_SERVICES


def seed_education_catalog():
    department, _ = Department.objects.update_or_create(
        code="EDU",
        defaults={
            "name": "Education",
            "description": "Scholarships, student services and higher education guidance.",
            "level": "Central",
        },
    )

    items = EDUCATION_SCHEMES + EDUCATION_SERVICES
    for item in items:
        description_sections = [
            item["summary"],
            item["description"],
            "Eligibility guidance: " + item["eligibility"],
            "Benefits: " + "; ".join(item["benefits"]),
            "Application process: " + "; ".join(item["workflow"]),
            "Expected result: " + item["final_output"],
        ]
        Scheme.objects.update_or_create(
            name=item["name"],
            department=department,
            defaults={
                "item_type": item["item_type"],
                "description": "\n\n".join(description_sections),
                "official_link": item["official_url"],
                "access_level": "Partial",
                "required_documents": "\n".join(item["documents"]),
                "level": "Central",
                "state": "",
                "is_active": True,
                "min_age": None,
                "max_age": None,
                "max_income": None,
                "allowed_categories": "",
                "allowed_occupations": "",
            },
        )

    return len(items)
