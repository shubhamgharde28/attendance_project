# attendance/management/commands/check_missing_reports.py
from django.core.management.base import BaseCommand
from attendance.utils import check_missing_reports

class Command(BaseCommand):
    help = "Check for employees who missed half-hourly reports"

    def handle(self, *args, **kwargs):
        self.stdout.write("Running missing report check...")
        check_missing_reports()
        self.stdout.write("Check completed.")
