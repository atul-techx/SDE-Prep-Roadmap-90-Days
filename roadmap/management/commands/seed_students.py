from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from roadmap.models import StudentProfile
import random

class Command(BaseCommand):
    help = 'Seeds the database with 50 dummy students (student1 to student50) with random XP.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting student seed process...')
        
        created_count = 0
        for i in range(1, 51):
            username = f'student{i}'
            email = f'{username}@example.com'
            password = 'password123'
            
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, email=email, password=password)
                
                # Give random XP (e.g. multiples of 50 up to 3000) and random streak
                random_xp = random.randint(0, 60) * 50
                random_streak = random.randint(0, 15)
                
                StudentProfile.objects.create(
                    user=user,
                    xp=random_xp,
                    current_streak=random_streak
                )
                created_count += 1
                
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} new dummy students!'))
