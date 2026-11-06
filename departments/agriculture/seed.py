from portal.models import Department, Scheme

from .schemes import AGRICULTURE_ITEMS


def seed_agriculture_catalog():
    department, _ = Department.objects.update_or_create(
        code="AGR",
        defaults={
            "name": "Agriculture",
            "description": "Central agriculture schemes and farmer services.",
            "level": "Central",
        },
    )

    for item in AGRICULTURE_ITEMS:
        detail_sections = [
            item["summary"],
            item["description"],
            "Eligibility guidance: " + item["eligibility"],
            "Benefits: " + "; ".join(item["benefits"]),
            "Application process: " + "; ".join(item["workflow"]),
            "Expected result: " + "; ".join(item["result"]),
        ]
        if item.get("parameters"):
            detail_sections.append(
                "Soil test parameters: " + ", ".join(item["parameters"])
            )

        Scheme.objects.update_or_create(
            name=item["name"],
            department=department,
            defaults={
                "item_type": item["item_type"],
                "description": "\n\n".join(detail_sections),
                "official_link": item["official_link"],
                "access_level": "Partial",
                "required_documents": "\n".join(item["documents"]),
                "level": "Central",
                "state": "",
                "is_active": True,
                "min_age": None,
                "max_age": None,
                "max_income": None,
                "allowed_categories": "",
                "allowed_occupations": (
                    "Farmer" if item["item_type"] == "Scheme" else ""
                ),
            },
        )

    return len(AGRICULTURE_ITEMS)
