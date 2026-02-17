import io
import logging
from pypdf import PdfWriter
from django.core.files.base import ContentFile
from .models import Conference, Submission, Proceedings

logger = logging.getLogger(__name__)

def create_conference_proceedings(conference_id):
    """
    Собирает все PDF-файлы заявок со статусом 'ready_for_print' 
    в один файл и сохраняет в модель Proceedings.
    """
    conference = Conference.objects.get(id=conference_id)
    merger = PdfWriter()
    
    submissions = Submission.objects.filter(
        conference=conference, 
        status='ready_for_print', 
        final_file__isnull=False
    ).order_by('id')

    if not submissions.exists():
        return None

    for sub in submissions:
        if sub.final_file and sub.final_file.storage.exists(sub.final_file.name):
            merger.append(sub.final_file.path)

    buffer = io.BytesIO()
    merger.write(buffer)
    buffer.seek(0)

    proceedings = Proceedings(conference=conference)
    
    filename = f"proceedings_{conference.slug}_{conference.id}.pdf"
    
    proceedings.file.save(filename, ContentFile(buffer.getvalue()), save=True)
    
    merger.close()
    
    logger.info(f"Сборник трудов для конференции '{conference.title}' успешно создан.")
    return proceedings