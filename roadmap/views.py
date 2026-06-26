from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from .models import StudentProfile, DailyContent, ProgressTracker, Notice, Event, DayAccessLog, Note
from django.db.models import Sum

from .forms import StudentRegistrationForm

def landing_page_view(request):
    # Build data for the 90 days learning path
    days_data = []
    content_map = {dc.day_number: dc.topic_name for dc in DailyContent.objects.all()}
    
    for i in range(1, 91):
        days_data.append({
            'day_number': i,
            'topic': content_map.get(i, 'Topic Locked - Login to Reveal')
        })
        
    return render(request, 'roadmap/landing.html', {'days_data': days_data})

def register_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('founder_dashboard')
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = StudentProfile.objects.create(user=user)
            
            # Save the extra fields to profile
            profile.full_name = form.cleaned_data.get('full_name')
            profile.contact_number = form.cleaned_data.get('contact_number')
            profile.save()
            
            login(request, user)
            if user.is_superuser:
                return redirect('founder_dashboard')
            return redirect('dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'roadmap/register.html', {'form': form})

def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next')
    
    if request.user.is_authenticated:
        if next_url:
            return redirect(next_url)
        if request.user.is_superuser:
            return redirect('founder_dashboard')
        return redirect('dashboard')
        
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
    return render(request, 'roadmap/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return redirect('login')

@login_required
def dashboard_view(request):
    if request.user.is_superuser:
        return redirect('founder_dashboard')

    profile = request.user.profile
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    current_day_number = (today - profile.start_date).days + 1
    
    # Cap at 90
    if current_day_number > 90:
        current_day_number = 90
    elif current_day_number < 1:
        current_day_number = 1

    # Check if streak is at risk
    days_since_last = (today - profile.last_completed_date).days if profile.last_completed_date else 0
    streak_at_risk = days_since_last > 1 and profile.current_streak > 0
    
    # If streak is at risk and they haven't applied a freeze, their streak is effectively 0
    display_streak = profile.current_streak if not streak_at_risk else 0

    all_days = DailyContent.objects.order_by('day_number')
    completed_days = ProgressTracker.objects.filter(student=profile).values_list('day__day_number', flat=True)
    
    days_data = []
    for day_num in range(1, 91):
        day_obj = all_days.filter(day_number=day_num).first()
        status = 'locked'
        if day_num <= current_day_number:
            status = 'unlocked'
        if day_num in completed_days:
            status = 'completed'
            
        days_data.append({
            'day_number': day_num,
            'day_obj': day_obj,
            'status': status
        })
        
    latest_notice = Notice.objects.filter(is_active=True).order_by('-created_at').first()

    context = {
        'profile': profile,
        'current_day_number': current_day_number,
        'days_data': days_data,
        'latest_notice': latest_notice,
        'streak_at_risk': streak_at_risk,
        'display_streak': display_streak,
        'show_welcome_back': request.session.pop('show_welcome_back', False),
    }
    return render(request, 'roadmap/dashboard.html', context)

@login_required
def founder_dashboard_view(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
        
    students = StudentProfile.objects.select_related('user').filter(user__is_superuser=False).order_by('-xp')
    
    student_data = []
    for st in students:
        max_day = ProgressTracker.objects.filter(student=st).aggregate(Sum('day__day_number')) # Just rough logic for progression
        # Actually better to count how many days completed:
        days_completed = ProgressTracker.objects.filter(student=st).count()
        status = 'ACTIVE'
        # Check if they recently used a freeze (e.g. within last 3 days)
        recent_freeze = ProgressTracker.objects.filter(student=st, used_freeze=True, completed_at__gte=timezone.now() - timedelta(days=3)).exists()
        if recent_freeze:
            status = 'FREEZE USED'
            
        display_name = st.full_name if st.full_name else st.user.username
        
        student_data.append({
            'profile_id': st.id,
            'real_username': st.user.username,
            'username': display_name,
            'email': st.user.email,
            'contact': st.contact_number if st.contact_number else 'N/A',
            'initials': display_name[0].upper() if display_name else 'U',
            'progress': days_completed,
            'streak': st.current_streak,
            'xp': st.xp,
            'status': status
        })

    return render(request, 'roadmap/founder_dashboard.html', {'students': student_data})

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

@login_required
def founder_student_detail_view(request, profile_id):
    if not request.user.is_superuser:
        return redirect('dashboard')
        
    profile = get_object_or_404(StudentProfile, id=profile_id)
    today = timezone.now().date()
    
    current_day_number = (today - profile.start_date).days + 1
    if current_day_number > 90:
        current_day_number = 90
    elif current_day_number < 1:
        current_day_number = 1

    days_since_last = (today - profile.last_completed_date).days if profile.last_completed_date else 0
    streak_at_risk = days_since_last > 1 and profile.current_streak > 0
    display_streak = profile.current_streak if not streak_at_risk else 0

    all_days = DailyContent.objects.order_by('day_number')
    completed_days = ProgressTracker.objects.filter(student=profile).values_list('day__day_number', flat=True)
    
    days_data = []
    for day_num in range(1, 91):
        day_obj = all_days.filter(day_number=day_num).first()
        status = 'locked'
        if day_num <= current_day_number:
            status = 'unlocked'
        if day_num in completed_days:
            status = 'completed'
            
        days_data.append({
            'day_number': day_num,
            'day_obj': day_obj,
            'status': status
        })
        
    context = {
        'student_profile': profile,
        'current_day_number': current_day_number,
        'display_streak': display_streak,
        'days_data': days_data,
        'total_completed': len(completed_days),
    }
    return render(request, 'roadmap/founder_student_detail.html', context)

import calendar as cal
from datetime import date

@login_required
def calendar_view(request):
    today = timezone.now().date()
    
    try:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
    except ValueError:
        year = today.year
        month = today.month
        
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
        
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
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
        
    current_date = date(year, month, 1)
        
    return render(request, 'roadmap/calendar.html', {
        'calendar_grid': calendar_grid,
        'current_month_name': current_date.strftime('%B %Y'),
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
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
def student_day_content_view(request, day_number):
    if request.user.is_superuser:
        return redirect('founder_dashboard')
        
    profile = request.user.profile
    today = timezone.now().date()
    current_day_number = (today - profile.start_date).days + 1
    
    if day_number > current_day_number:
        messages.error(request, "This day is locked.")
        return redirect('dashboard')
        
    day_obj = get_object_or_404(DailyContent, day_number=day_number)
    is_completed = ProgressTracker.objects.filter(student=profile, day=day_obj).exists()
    
    access_log, created = DayAccessLog.objects.get_or_create(student=profile, day=day_obj)
    
    unlock_time = access_log.first_accessed_at + timedelta(hours=2)
    now = timezone.now()
    can_complete = now >= unlock_time
    
    time_remaining_seconds = 0
    if not can_complete:
        time_remaining_seconds = (unlock_time - now).total_seconds()
        
    context = {
        'day': day_obj,
        'is_completed': is_completed,
        'can_complete': can_complete,
        'time_remaining_seconds': time_remaining_seconds,
        'unlock_time': unlock_time,
    }
    return render(request, 'roadmap/day_content.html', context)

@login_required
def founder_content_list_view(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
        
    days = DailyContent.objects.all().order_by('day_number')
    return render(request, 'roadmap/founder_content_list.html', {'days': days})

@login_required
def founder_content_edit_view(request, day_number):
    if not request.user.is_superuser:
        return redirect('dashboard')
        
    day, created = DailyContent.objects.get_or_create(day_number=day_number, defaults={'topic_name': f'Day {day_number}'})
    
    if request.method == 'POST':
        day.topic_name = request.POST.get('topic_name', day.topic_name)
        day.rich_content = request.POST.get('rich_content', '')
        day.save()
        messages.success(request, f"Day {day_number} content updated successfully!")
        return redirect('founder_content_list')
        
    return render(request, 'roadmap/founder_content_edit.html', {'day': day})

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
def mark_completed_view(request, day_number):
    if request.method == 'POST':
        profile = request.user.profile
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        current_day_number = (today - profile.start_date).days + 1
        if day_number > current_day_number:
            messages.error(request, "This day is locked.")
            return redirect('dashboard')
            
        day_obj = get_object_or_404(DailyContent, day_number=day_number)
        
        access_log = DayAccessLog.objects.filter(student=profile, day=day_obj).first()
        if not access_log or timezone.now() < (access_log.first_accessed_at + timedelta(hours=2)):
            messages.error(request, "You must wait 2 hours after opening the content before marking it as complete.")
            return redirect('student_day_content', day_number=day_number)
            
        if ProgressTracker.objects.filter(student=profile, day=day_obj).exists():
            messages.info(request, "Day already completed.")
            return redirect('dashboard')
            
        if profile.last_completed_date == today:
            pass
        elif profile.last_completed_date == yesterday:
            profile.current_streak += 1
        else:
            profile.current_streak = 1
            
        profile.last_completed_date = today
        profile.xp += 10
        profile.save()
        
        ProgressTracker.objects.create(student=profile, day=day_obj)
        messages.success(request, f"+10 XP! Day {day_number} completed.")
        
    return redirect('dashboard')

@login_required
def apply_freeze_view(request):
    if request.method == 'POST':
        profile = request.user.profile
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        days_since_last = (today - profile.last_completed_date).days if profile.last_completed_date else 0
        streak_at_risk = days_since_last > 1 and profile.current_streak > 0
        
        if profile.freezes_left > 0 and streak_at_risk:
            profile.freezes_left -= 1
            profile.last_completed_date = yesterday
            profile.save()
            messages.success(request, "Streak freeze applied! Streak restored.")
        else:
            messages.error(request, "Cannot apply freeze. You may not have freezes left, or your streak is not at risk.")
            
    return redirect('dashboard')

@login_required
def community_view(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        if content or image:
            from .models import CommunityMessage
            CommunityMessage.objects.create(user=request.user, content=content, image=image)
        return redirect('community')
        
    from .models import CommunityMessage
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
    profile = request.user.profile
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
