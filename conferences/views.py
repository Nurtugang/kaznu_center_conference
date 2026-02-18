from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Conference, Submission, SubmissionVersion, Proceedings
from django.contrib.auth import login
from .forms import RegistrationForm, SubmissionForm
from django.contrib import messages
from django.db.models import Prefetch
from django.contrib.auth.views import LoginView


def register(request):
    conference = Conference.get_current()

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user, backend='conferences.backends.EmailOrUsernameModelBackend')
            return redirect('conferences:profile')
    else:
        form = RegistrationForm()
    return render(request, 'conferences/register.html', {
        'form': form,
        'conference': conference
    })

@login_required
def submit_work(request):
    conference = Conference.get_current()
    
    if conference.registration_deadline < timezone.now():
        messages.error(request, "Срок подачи заявок на эту конференцию истек.")
        return redirect('conferences:detail')

    if Submission.objects.filter(user=request.user, conference=conference).exists():
        messages.warning(request, "Вы уже подали заявку на эту конференцию.")
        return redirect('conferences:profile')

    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            submission.conference = conference
            submission.save()
            
            SubmissionVersion.objects.create(
                submission=submission,
                file=form.cleaned_data['file'],
                version_number=1,
                author_comment=form.cleaned_data['author_comment']
            )
            
            messages.success(request, "Ваша работа успешно принята и отправлена на проверку!")
            return redirect('conferences:profile')
    else:
        form = SubmissionForm()
    
    return render(request, 'conferences/submit.html', {
        'form': form, 
        'conference': conference
    })

@login_required
def resubmit_work(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id, user=request.user)
    
    last_version = submission.versions.order_by('-version_number').first()
    
    if submission.status != 'revision':
        messages.error(request, "Эта работа не требует доработки или уже проверяется.")
        return redirect('conferences:profile')

    if request.method == 'POST':
        new_version_num = (last_version.version_number + 1) if last_version else 1

        new_file = request.FILES.get('file')
        author_comment = request.POST.get('author_comment', '')

        if new_file:
            new_version_num = (last_version.version_number + 1) if last_version else 1
            
            SubmissionVersion.objects.create(
                submission=submission,
                file=new_file,
                version_number=new_version_num,
                author_comment=author_comment
            )
            
            submission.status = 'under_review'
            submission.save()
            
            messages.success(request, f"Версия №{new_version_num} успешно загружена. Статус обновлен.")
            return redirect('conferences:profile')
        else:
            messages.error(request, "Пожалуйста, выберите файл.")

    return render(request, 'conferences/resubmit.html', {
        'submission': submission,
        'last_version': last_version
    })

def conference_detail(request):
    conference = Conference.get_current()
    user_submission = None
    if request.user.is_authenticated:
        user_submission = Submission.objects.filter(user=request.user, conference=conference).first()
    
    # Логика для таймера (передаем в контекст)
    now = timezone.now()
    
    return render(request, 'conferences/detail.html', {
        'conference': conference,
        'user_submission': user_submission,
        'now': now
    })

def conference_program(request):
    conference = Conference.get_current()
    return render(request, 'conferences/program.html', {'conference': conference})

def conference_committee(request):
    conference = Conference.get_current()
    committee_members = conference.committee_members.all().order_by('order', 'full_name')
    return render(request, 'conferences/committee.html', {
        'conference': conference,
        'committee_members': committee_members
    })

def conference_gallery(request):
    conference = Conference.get_current()
    media = conference.media.all()
    return render(request, 'conferences/gallery.html', {'conference': conference, 'media': media})

def conference_proceedings(request):
    conference = Conference.get_current()
    proceeding = Proceedings.objects.filter(conference=conference).first()
    is_released = timezone.now().date() >= conference.notification_date
    submissions = []
    if is_released:
        submissions = Submission.objects.filter(conference=conference, status='ready_for_print').prefetch_related('versions').order_by('title')
        
    return render(request, 'conferences/proceedings.html', {
        'conference': conference, 
        'is_released': is_released,
        'submissions': submissions,
        'proceeding': proceeding
    })
    
def conference_venue(request):
    conference = Conference.get_current()
    return render(request, 'conferences/venue.html', {'conference': conference})

def conference_documentation(request):
    conference = Conference.get_current()
    documents = conference.documents.all()
    return render(request, 'conferences/documentation.html', {
        'conference': conference,
        'documents': documents
    })

def conference_contacts(request):
    conference = Conference.get_current()
    contacts = conference.contacts.all()
    return render(request, 'conferences/contacts.html', {
        'conference': conference,
        'contacts': contacts
    })

def participation_fee(request):
    conference = Conference.get_current()
    return render(request, 'conferences/participation_fee.html', {'conference': conference})

def submission_format(request):
    conference = Conference.get_current()
    return render(request, 'conferences/submission_format.html', {'conference': conference})

@login_required
def profile_view(request):
    conference = Conference.get_current()
    
    submissions = Submission.objects.filter(user=request.user)\
        .select_related('conference')\
        .prefetch_related(
            Prefetch('versions', queryset=SubmissionVersion.objects.order_by('-created_at'))
        )
    
    return render(request, 'conferences/profile.html', {
        'submissions': submissions,
        'conference': conference,
    })

class UserLoginView(LoginView):
    template_name = 'conferences/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['conference'] = Conference.get_current()
        return context

def privacy_policy(request):
    conference = Conference.get_current()
    return render(request, 'conferences/privacy.html', {
        'conference': conference
    })

def terms(request):
    conference = Conference.get_current()
    return render(request, 'conferences/terms.html', {
        'conference': conference
    })