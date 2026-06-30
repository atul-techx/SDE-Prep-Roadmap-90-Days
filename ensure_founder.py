import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dsa_platform.settings")
django.setup()

from django.contrib.auth.models import User
from roadmap.models import StudentProfile

u = User.objects.get(username='founder')
StudentProfile.objects.get_or_create(user=u, defaults={'full_name': 'Founder'})
print("Founder profile ensured.")
