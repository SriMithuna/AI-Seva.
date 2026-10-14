
from django.core.management.base import BaseCommand
from portal.models import Department, Scheme


DATA = [
    ("Education", "EDU", [
        ("Post-Matric Scholarship", "Scholarship support for eligible students.", "SC,ST", "Student", 0, 1000000),
        ("Central Sector Scholarship", "Financial assistance for eligible college students.", "", "Student", 0, 450000),
        ("PM Vidyalaxmi", "Education loan support for eligible students.", "", "Student", 0, None),
    ]),
    ("Agriculture", "AGR", [
        ("PM-KISAN", "Income support for eligible farmer families.", "", "Farmer", 0, None),
        ("PM Fasal Bima Yojana", "Crop insurance for eligible farmers.", "", "Farmer", 0, None),
        ("Kisan Credit Card", "Credit access for eligible farmers.", "", "Farmer", 0, None),
    ]),
    ("Health & Wellness", "HLT", [
        ("Ayushman Bharat PM-JAY", "Health coverage for eligible families.", "", "", 0, 250000),
        ("PM Matru Vandana Yojana", "Maternity benefit support for eligible applicants.", "", "", 18, None),
        ("Janani Suraksha Yojana", "Support for eligible mothers.", "", "", 18, None),
    ]),
    ("Housing & Rural Development", "HRD", [
        ("PMAY-Gramin", "Housing assistance for eligible rural households.", "", "", 18, 300000),
        ("PMAY-Urban", "Housing assistance under eligible urban components.", "", "", 18, None),
        ("NSAP Pensions", "Social assistance pensions for eligible beneficiaries.", "", "", 60, 300000),
        ("DAY-NRLM", "Livelihood support through rural self-help groups.", "", "", 18, None),
    ]),
    ("Labour, Skill & MSME", "LSM", [
        ("PM Kaushal Vikas Yojana", "Skill training support.", "", "Unemployed", 18, None),
        ("PM SVANidhi", "Working capital support for eligible street vendors.", "", "Self-employed", 18, None),
        ("PM Vishwakarma", "Support for eligible traditional artisans.", "", "Self-employed", 18, None),
    ]),
    ("Postal Services", "POST", [
        ("Sukanya Samriddhi Yojana (SSY)", "Savings scheme for eligible girl children.", "", "", 0, None),
        ("Senior Citizens' Savings Scheme (SCSS)", "Savings scheme for eligible senior citizens.", "", "", 60, None),
        ("Public Provident Fund (PPF)", "Long-term savings scheme.", "", "", 18, None),
    ]),
    ("Law & Justice", "LAW", [
        ("Nyaya Bandhu", "Pro bono legal assistance for eligible applicants.", "", "", 18, None),
        ("Tele-Law", "Access to legal advice through digital services.", "", "", 18, None),
    ]),
    ("Tamil Nadu State Schemes", "TN", [
        ("Pudhumai Penn", "Tamil Nadu education assistance scheme.", "", "", 18, None),
        ("Kalaignar Magalir Urimai Thogai", "Financial assistance under Tamil Nadu scheme rules.", "", "", 18, None),
    ]),
]


class Command(BaseCommand):
    help = "Load starter scheme data for AI Seva"

    def handle(self, *args, **options):
        total = 0

        for department_name, code, schemes in DATA:
            level = "State" if code == "TN" else "Central"

            department, _ = Department.objects.update_or_create(
                code=code,
                defaults={
                    "name": department_name,
                    "level": level,
                },
            )

            for name, description, categories, occupations, min_age, max_income in schemes:
                Scheme.objects.update_or_create(
                    name=name,
                    department=department,
                    defaults={
                        "item_type": "Scheme",
                        "description": description,
                        "level": level,
                        "state": "Tamil Nadu" if code == "TN" else "",
                        "is_active": True,
                        "min_age": min_age,
                        "max_income": max_income,
                        "allowed_categories": categories,
                        "allowed_occupations": occupations,
                    },
                )
                total += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Loaded or updated {total} starter schemes."
            )
        )
        self.stdout.write(
            "Verify official eligibility rules before using these records for real applications."
        )
