import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.http import JsonResponse
from .models import StudentProfile, Topic, DayContent, Question, QuestionProgress, Notice, Event, Note, CommunityMessage
from django.db.models import Sum, Count, OuterRef, Exists, Prefetch

from .forms import StudentRegistrationForm

def landing_page_view(request):
    days_data = []
    # Simplified for now
    return render(request, 'roadmap/landing.html', {
        'days_data': days_data,
        'is_public_page': True
    })

def register_view(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = StudentProfile.objects.create(user=user)
            profile.full_name = form.cleaned_data.get('full_name')
            profile.contact_number = form.cleaned_data.get('contact_number')
            profile.save()
            login(request, user)
            if user.is_superuser:
                return redirect('founder_dashboard')
            return redirect('dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'roadmap/register.html', {'form': form, 'is_public_page': True})

def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            request.session['show_welcome_back'] = True
            if next_url:
                return redirect(next_url)
            if user.is_superuser:
                return redirect('founder_dashboard')
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
        
    for field_name, field in form.fields.items():
        if field_name == 'username':
            field.widget.attrs.update({'placeholder': 'Enter your username'})
        elif field_name == 'password':
            field.widget.attrs.update({'placeholder': 'Enter your password'})
            
    return render(request, 'roadmap/login.html', {'form': form, 'is_public_page': True})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('home')

@login_required
def dashboard_view(request):
    if request.user.is_superuser:
        return redirect('founder_dashboard')

    profile = request.user.profile
    today = timezone.now().date()
    
    current_day_number = (today - profile.start_date).days + 1
    if current_day_number > 90:
        current_day_number = 90
    elif current_day_number < 1:
        current_day_number = 1

    days_since_last = (today - profile.last_completed_date).days if profile.last_completed_date else 0
    streak_at_risk = days_since_last > 1 and profile.current_streak > 0
    display_streak = profile.current_streak if not streak_at_risk else 0

    topics = Topic.objects.all().order_by('order').prefetch_related(
        Prefetch('days', queryset=DayContent.objects.all().order_by('day_number')),
        Prefetch('days__questions', queryset=Question.objects.all().order_by('order'))
    )
    
    completed_q_ids = set(QuestionProgress.objects.filter(student=profile, completed=True).values_list('question_id', flat=True))
    
    topics_data = []
    total_questions = 0
    total_completed = 0
    
    for topic in topics:
        topic_questions = 0
        topic_completed = 0
        days_data = []
        for day in topic.days.all():
            day_questions = []
            for q in day.questions.all():
                is_completed = q.id in completed_q_ids
                total_questions += 1
                topic_questions += 1
                if is_completed:
                    total_completed += 1
                    topic_completed += 1
                
                day_questions.append({
                    'id': q.id,
                    'name': q.name,
                    'difficulty': q.difficulty,
                    'article_link': q.article_link,
                    'youtube_link': q.youtube_link,
                    'leetcode_link': q.leetcode_link,
                    'completed': is_completed
                })
            
            days_data.append({
                'day': day,
                'questions': day_questions,
            })
            
        topics_data.append({
            'topic': topic,
            'days': days_data,
            'total': topic_questions,
            'completed': topic_completed,
            'progress': int((topic_completed / topic_questions * 100) if topic_questions > 0 else 0)
        })

    overall_progress = int((total_completed / total_questions * 100) if total_questions > 0 else 0)
    latest_notice = Notice.objects.filter(is_active=True).order_by('-created_at').first()

    context = {
        'profile': profile,
        'current_day_number': current_day_number,
        'topics_data': topics_data,
        'latest_notice': latest_notice,
        'streak_at_risk': streak_at_risk,
        'display_streak': display_streak,
        'total_completed': total_completed,
        'total_questions': total_questions,
        'overall_progress_percentage': overall_progress,
        'show_welcome_back': request.session.pop('show_welcome_back', False),
    }
    return render(request, 'roadmap/dashboard.html', context)

@login_required
@require_POST
def toggle_task_completion(request):
    try:
        data = json.loads(request.body)
        question_id = data.get('question_id')
        completed = data.get('completed', False)
        
        if not question_id:
            return JsonResponse({'success': False, 'error': 'Missing question_id'}, status=400)
            
        profile = request.user.profile
        question = get_object_or_404(Question, id=question_id)
        
        tracker, created = QuestionProgress.objects.get_or_create(student=profile, question=question)
        tracker.completed = completed
        tracker.save()
        
        # Recalculate progress for UI update
        total_qs = Question.objects.count()
        total_done = QuestionProgress.objects.filter(student=profile, completed=True).count()
        overall = int((total_done / total_qs * 100) if total_qs > 0 else 0)
        
        topic_qs = Question.objects.filter(day__topic=question.day.topic).count()
        topic_done = QuestionProgress.objects.filter(student=profile, completed=True, question__day__topic=question.day.topic).count()
        topic_prog = int((topic_done / topic_qs * 100) if topic_qs > 0 else 0)
        
        return JsonResponse({
            'success': True, 
            'overall_progress': overall,
            'topic_progress': topic_prog,
            'topic_id': question.day.topic.id,
            'total_done': total_done
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def apply_freeze_view(request):
    return redirect('dashboard')

@login_required
def community_view(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        if content or image:
            CommunityMessage.objects.create(user=request.user, content=content, image=image)
        return redirect('community')
        
    messages_list = CommunityMessage.objects.all().order_by('-created_at')
    return render(request, 'roadmap/community.html', {'community_messages': messages_list})

@login_required
def leaderboard_view(request):
    students = StudentProfile.objects.select_related('user').filter(user__is_superuser=False).order_by('-xp')
    leaderboard_data = []
    for index, student in enumerate(students):
        leaderboard_data.append({
            'rank': index + 1,
            'profile': student,
        })
    return render(request, 'roadmap/leaderboard.html', {'leaderboard_data': leaderboard_data})

@login_required
def profile_view(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        profile.full_name = request.POST.get('full_name')
        profile.gender = request.POST.get('gender')
        
        email = request.POST.get('email')
        if email:
            request.user.email = email
            request.user.save()
            
        profile.state = request.POST.get('state')
        profile.city = request.POST.get('city')
        profile.pincode = request.POST.get('pincode')
        
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        if 'cover_banner' in request.FILES:
            profile.cover_banner = request.FILES['cover_banner']
            
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
        
    return render(request, 'roadmap/profile.html', {'profile': profile})

@login_required
def founder_dashboard_view(request):
    if not request.user.is_superuser: return redirect('dashboard')
    students = StudentProfile.objects.select_related('user').filter(user__is_superuser=False)
    return render(request, 'roadmap/founder_dashboard.html', {'students': students})

@login_required
def founder_student_detail_view(request, profile_id):
    if not request.user.is_superuser: return redirect('dashboard')
    profile = get_object_or_404(StudentProfile, id=profile_id)
    return render(request, 'roadmap/founder_student_detail.html', {'student_profile': profile})

import calendar as cal
from datetime import date

@login_required
def calendar_view(request):
    today = timezone.now().date()
    year = today.year
    month = today.month
    
    c = cal.Calendar(firstweekday=6)
    weeks = c.monthdatescalendar(year, month)
    
    colors = ['bg-indigo-500', 'bg-emerald-500', 'bg-rose-500', 'bg-amber-500', 'bg-sky-500', 'bg-purple-500', 'bg-pink-500', 'bg-teal-500']
    events = Event.objects.filter(date__year=year, date__month=month)
    events_by_date = {}
    for e in events:
        cat_hash = sum(ord(c) for c in e.category) if e.category else 0
        e.color_class = colors[cat_hash % len(colors)]
        
        if e.date not in events_by_date:
            events_by_date[e.date] = []
        events_by_date[e.date].append(e)
        
    calendar_grid = []
    for week in weeks:
        week_data = []
        for d in week:
            day_events = events_by_date.get(d, [])
            week_data.append({
                'date': d,
                'day': d.day,
                'in_month': d.month == month,
                'is_today': d == today,
                'events': day_events
            })
        calendar_grid.append(week_data)
        
    return render(request, 'roadmap/calendar.html', {
        'calendar_grid': calendar_grid,
        'current_month_name': today.strftime('%B %Y')
    })

@login_required
def add_event_view(request):
    if not request.user.is_superuser:
        return redirect('calendar')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        date_str = request.POST.get('date')
        category = request.POST.get('category')
        description = request.POST.get('description', '')
        if title and date_str and category:
            Event.objects.create(title=title, date=date_str, category=category, description=description)
            messages.success(request, 'Event added successfully.')
        else:
            messages.error(request, 'Please fill all required fields.')
            
    return redirect('calendar')

@login_required
def founder_content_list_view(request):
    return redirect('founder_dashboard')

@login_required
def founder_content_edit_view(request, day_number):
    return redirect('founder_dashboard')

@login_required
def founder_notes_view(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        category = request.POST.get('category')
        description = request.POST.get('description')
        file = request.FILES.get('file')
        
        if title and file:
            Note.objects.create(title=title, category=category, description=description, file=file)
            messages.success(request, "Note uploaded successfully!")
        else:
            messages.error(request, "Title and File are required.")
        return redirect('founder_notes')
        
    notes = Note.objects.all().order_by('-uploaded_at')
    categories = [c[0] for c in Note.CATEGORY_CHOICES]
    return render(request, 'roadmap/founder_notes.html', {'notes': notes, 'categories': categories})

@login_required
def student_notes_view(request):
    category_filter = request.GET.get('category')
    notes = Note.objects.all().order_by('-uploaded_at')
    
    if category_filter:
        notes = notes.filter(category=category_filter)
        
    categories = [c[0] for c in Note.CATEGORY_CHOICES]
    
    return render(request, 'roadmap/student_notes.html', {
        'notes': notes, 
        'categories': categories,
        'current_category': category_filter
    })

@login_required
def student_day_content_view(request, day_number):
    return redirect('dashboard')

@login_required
def mark_completed_view(request, day_number):
    return redirect('dashboard')

@login_required
def founder_register_student_view(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = StudentProfile.objects.create(user=user)
            profile.full_name = form.cleaned_data.get('full_name')
            profile.contact_number = form.cleaned_data.get('contact_number')
            profile.save()
            messages.success(request, f"Student {user.username} registered successfully.")
            return redirect('founder_dashboard')
    else:
        form = StudentRegistrationForm()
        
    return render(request, 'roadmap/founder_register_student.html', {'form': form})

def setup_founder_view(request):
    from django.contrib.auth.models import User
    from django.http import HttpResponse
    if User.objects.filter(username='founder').exists():
        return HttpResponse("Founder account exists!")
    try:
        user = User.objects.create_superuser('founder', 'founder@example.com', 'Founder@90Days')
        StudentProfile.objects.create(user=user, full_name="Founder", contact_number="000")
        return HttpResponse("SUCCESS! <a href='/login/'>Click here to login</a>")
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")
