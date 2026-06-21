from django.core.management.base import BaseCommand
from roadmap.models import StudentProfile

class Command(BaseCommand):
    help = 'Resets freezes_left to 2 for all students'

    def handle(self, *args, **kwargs):
        count = StudentProfile.objects.update(freezes_left=2)
        self.stdout.write(self.style.SUCCESS(f'Successfully reset freezes for {count} students.'))
