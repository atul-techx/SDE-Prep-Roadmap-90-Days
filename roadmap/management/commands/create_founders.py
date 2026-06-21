from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from roadmap.models import StudentProfile

class Command(BaseCommand):
    help = 'Creates 3 superuser accounts for the founders'

    def handle(self, *args, **kwargs):
        founders = ['founder1', 'founder2', 'founder3']
        for founder in founders:
            if not User.objects.filter(username=founder).exists():
                user = User.objects.create_superuser(founder, f'{founder}@example.com', 'admin123')
                StudentProfile.objects.create(user=user)
                self.stdout.write(self.style.SUCCESS(f'Successfully created founder: {founder}'))
            else:
                self.stdout.write(self.style.WARNING(f'Founder {founder} already exists'))
