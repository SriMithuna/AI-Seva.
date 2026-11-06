from django.core.management.base import BaseCommand

from departments.agriculture.seed import seed_agriculture_catalog


class Command(BaseCommand):
    help = "Load or update the five Agriculture schemes and services for AI Seva"

    def handle(self, *args, **options):
        total = seed_agriculture_catalog()
        self.stdout.write(
            self.style.SUCCESS(
                f"Loaded or updated {total} Agriculture schemes and services."
            )
        )
