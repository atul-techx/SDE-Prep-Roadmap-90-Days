from django.contrib import admin
from .models import StudentProfile, DailyContent, ProgressTracker, Notice

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'xp', 'current_streak', 'freezes_left', 'start_date', 'last_completed_date')
    search_fields = ('user__username', 'user__email')
    ordering = ('-xp', '-current_streak')

@admin.register(DailyContent)
class DailyContentAdmin(admin.ModelAdmin):
    list_display = ('day_number', 'topic_name')
    ordering = ('day_number',)

@admin.register(ProgressTracker)
class ProgressTrackerAdmin(admin.ModelAdmin):
    list_display = ('student', 'day', 'completed_at', 'used_freeze')
    list_filter = ('used_freeze', 'day')
    search_fields = ('student__user__username',)

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('text', 'is_active', 'created_at')
    list_filter = ('is_active',)
