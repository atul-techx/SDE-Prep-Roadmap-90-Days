import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dsa_platform.settings')
django.setup()

from django.contrib.auth.models import User
users = User.objects.filter(is_superuser=True)
if not users:
    print("No superusers found. Creating a new one...")
    User.objects.create_superuser('founder', 'founder@example.com', 'Admin@123')
    print("Created superuser 'founder' with password 'Admin@123'")
else:
    for u in users:
        u.set_password('Admin@123')
        u.save()
        print(f"Reset password for superuser '{u.username}' to 'Admin@123'")
