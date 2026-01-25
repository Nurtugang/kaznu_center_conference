from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'conferences'

urlpatterns = [
    path('', views.conference_detail, name='detail'),
    
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='conferences/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    path('submit/', views.submit_work, name='submit'),
    path('submission/<int:submission_id>/resubmit/', views.resubmit_work, name='resubmit'),
    
    path('program/', views.conference_program, name='program'),
    path('committee/', views.conference_committee, name='committee'),
    path('gallery/', views.conference_gallery, name='gallery'),
    path('proceedings/', views.conference_proceedings, name='proceedings'),
    path('venue/', views.conference_venue, name='venue'),
    path('documentation/', views.conference_documentation, name='documentation'),
    path('contacts/', views.conference_contacts, name='contacts'),
    path('participation-fee/', views.participation_fee, name='participation_fee'),
    path('submission-format/', views.submission_format, name='submission_format'),
]