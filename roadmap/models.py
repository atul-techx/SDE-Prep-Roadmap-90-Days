from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    start_date = models.DateField(default=timezone.now)
    xp = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    freezes_left = models.IntegerField(default=2)
    last_completed_date = models.DateField(null=True, blank=True)
    
    # Extended Profile Fields
    full_name = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    cover_banner = models.ImageField(upload_to='cover_banners/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class DailyContent(models.Model):
    day_number = models.IntegerField(unique=True, primary_key=True)
    topic_name = models.CharField(max_length=255)
    video_link = models.URLField(blank=True, null=True)
    notes_link = models.URLField(blank=True, null=True)
    questions_list = models.JSONField(default=list, help_text="List of question URLs")

    def __str__(self):
        return f"Day {self.day_number}: {self.topic_name}"

class ProgressTracker(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='progress')
    day = models.ForeignKey(DailyContent, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)
    used_freeze = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'day')

    def __str__(self):
        return f"{self.student.user.username} completed Day {self.day.day_number}"

class Notice(models.Model):
    text = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.text

class Event(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateField()
    category = models.CharField(max_length=100, default='General')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} on {self.date}"

class CommunityMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='community_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} at {self.created_at}"
