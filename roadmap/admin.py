from django.contrib import admin
from .models import StudentProfile, Topic, DayContent, Question, QuestionProgress, Notice

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'xp', 'current_streak', 'freezes_left', 'start_date', 'last_completed_date')
    search_fields = ('user__username', 'user__email')
    ordering = ('-xp', '-current_streak')

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'allocated_days', 'order')

@admin.register(DayContent)
class DayContentAdmin(admin.ModelAdmin):
    list_display = ('day_number', 'topic', 'name')
    
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('name', 'day', 'difficulty')

@admin.register(QuestionProgress)
class QuestionProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'question', 'completed_at', 'completed')

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('text', 'is_active', 'created_at')
    list_filter = ('is_active',)
