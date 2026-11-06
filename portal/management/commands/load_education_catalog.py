from django.core.management.base import BaseCommand

from departments.education.seed import seed_education_catalog


class Command(BaseCommand):
    help = "Load or update the Education schemes and services for AI Seva"

    def handle(self, *args, **options):
        total = seed_education_catalog()
        self.stdout.write(
            self.style.SUCCESS(
                f"Loaded or updated {total} Education schemes and services."
            )
        )
