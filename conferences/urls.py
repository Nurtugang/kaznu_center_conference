from django.urls import path
from django.contrib.auth import views as auth_views
from . import views, views_organizer
from .api import active_conferences_api

app_name = 'conferences'

urlpatterns = [
    path('', views.conference_detail, name='detail'),
    
    path('register/', views.register, name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    path('submit/', views.submit_work, name='submit'),
    path('submission/<int:submission_id>/resubmit/', views.resubmit_work, name='resubmit'),
    
    path('management/submissions/', views_organizer.submission_management_list, name='submission_management_list'),
    path('management/submissions/<int:submission_id>/', views_organizer.submission_management_detail, name='submission_management_detail'),
    path('management/submissions/<int:submission_id>/update/', views_organizer.update_submission_status, name='update_submission_status'),
    
    path('program/', views.conference_program, name='program'),
    path('committee/', views.conference_committee, name='committee'),
    path('gallery/', views.conference_gallery, name='gallery'),
    path('proceedings/', views.conference_proceedings, name='proceedings'),
    path('venue/', views.conference_venue, name='venue'),
    path('documentation/', views.conference_documentation, name='documentation'),
    path('contacts/', views.conference_contacts, name='contacts'),
    path('participation-fee/', views.participation_fee, name='participation_fee'),
    path('submission-format/', views.submission_format, name='submission_format'),
    path('privacy/', views.privacy_policy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    
    path('api/conferences/', active_conferences_api, name='api_conferences'),
]