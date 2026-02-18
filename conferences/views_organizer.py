from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Conference, Submission
from django.utils.translation import gettext as _

def organizer_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_organizer:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view

@login_required
@organizer_required
def submission_management_list(request):
    conference = Conference.get_current()
    status_filter = request.GET.get('status')
    
    proceedings = conference.proceedings_archive.first()
    if request.method == 'POST' and 'create_proceedings' in request.POST:
        if not proceedings:
            from .services import create_conference_proceedings
            create_conference_proceedings(conference.id)
            messages.success(request, _("Сборник успешно сформирован."))
            return redirect('conferences:submission_management_list')
        
    
    submissions = Submission.objects.filter(conference=conference).select_related('user')
    total_count = submissions.count()
    
    status_counts = {}
    status_choices_with_counts = []
    for status_val, status_name in Submission.STATUS_CHOICES:
        count = submissions.filter(status=status_val).count()
        status_counts[status_val] = count
        status_choices_with_counts.append((status_val, status_name, count))
    
    if status_filter:
        submissions = submissions.filter(status=status_filter)
    
    status_choices = Submission.STATUS_CHOICES
    
    return render(request, 'conferences/management/submission_list.html', {
        'conference': conference,
        'submissions': submissions,
        'proceedings': proceedings,
        'status_choices': status_choices,
        'status_choices_with_counts': status_choices_with_counts,
        'status_counts': status_counts,
        'total_submissions_count': total_count,
        'current_status': status_filter
    })

@login_required
@organizer_required
def submission_management_detail(request, submission_id):
    conference = Conference.get_current()
    submission = get_object_or_404(
        Submission.objects.prefetch_related('versions'), 
        id=submission_id, 
        conference=conference
    )
    
    return render(request, 'conferences/management/submission_detail.html', {
        'conference': conference,
        'submission': submission,
    })

@login_required
@organizer_required
def update_submission_status(request, submission_id):
    if request.method == 'POST':
        submission = get_object_or_404(Submission, id=submission_id)
        new_status = request.POST.get('new_status')
        comment = request.POST.get('comment', '')
        print("Recieved next data from form: ", new_status, comment)

        submission.status = new_status
        submission.save()
        
        if comment and new_status == 'revision':
            last_version = submission.versions.order_by('-created_at').first()
            if last_version:
                last_version.admin_comment = comment
                last_version.save()
            messages.info(request, _("Замечания отправлены автору."))

        messages.success(request, _("Статус изменен на: {}").format(submission.get_status_display()))
        
        return redirect('conferences:submission_management_detail', submission_id=submission.id)
    
    return redirect('conferences:submission_management_list')