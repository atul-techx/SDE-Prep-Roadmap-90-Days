from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('founder-dashboard/', views.founder_dashboard_view, name='founder_dashboard'),
    path('founder-dashboard/register/', views.founder_register_student_view, name='founder_register_student'),
    path('founder-dashboard/student/<int:profile_id>/', views.founder_student_detail_view, name='founder_student_detail'),
    path('founder-dashboard/content/', views.founder_content_list_view, name='founder_content_list'),
    path('founder-dashboard/content/<int:day_number>/edit/', views.founder_content_edit_view, name='founder_content_edit'),
    path('founder-dashboard/notes/', views.founder_notes_view, name='founder_notes'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/add/', views.add_event_view, name='add_event'),
    path('community/', views.community_view, name='community'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('notes/', views.student_notes_view, name='student_notes'),
    path('profile/', views.profile_view, name='profile'),
    path('', views.landing_page_view, name='home'),
    path('complete/<int:day_number>/', views.mark_completed_view, name='mark_completed'),
    path('day/<int:day_number>/', views.student_day_content_view, name='student_day_content'),
    path('toggle-task/', views.toggle_task_completion, name='toggle_task_completion'),
    path('apply-freeze/', views.apply_freeze_view, name='apply_freeze'),
    path('setup-founder-account/', views.setup_founder_view, name='setup_founder'),
]
