import re
import os
import logging
import subprocess

from PIL import Image
from io import BytesIO
from django.db import models
from django.conf import settings
from django.forms import ValidationError
from django.core.files.base import ContentFile
from django.contrib.auth.models import AbstractUser
from django_ckeditor_5.fields import CKEditor5Field
from django.core.validators import FileExtensionValidator

logger = logging.getLogger(__name__)


class User(AbstractUser):
    ROLE_CHOICES = [
        ('author', 'Автор (Участник)'),
        ('organizer', 'Организатор (Админ/Редактор)'),
    ]
    
    role = models.CharField("Роль", max_length=20, choices=ROLE_CHOICES, default='author')
    organization = models.CharField("Организация", max_length=255, blank=True)
    email = models.EmailField("Электронная почта", unique=True)

    @property
    def is_organizer(self):
        return self.role == 'organizer' or self.is_staff
    
    def __str__(self):
        full_name = f"{self.last_name} {self.first_name}".strip()
        return full_name if full_name else self.username


class Conference(models.Model):
    title = models.CharField("Название конференции", max_length=500)
    short_title = models.CharField("Краткое название", max_length=100)
    slug = models.SlugField("URL-префикс", unique=True)

    description = CKEditor5Field("Описание", config_name='default')

    location = models.CharField("Место проведения (коротко)", max_length=255)
    location_description = CKEditor5Field("Место проведения (подробно)", blank=True, null=True, config_name='default')

    start_date = models.DateField("Дата начала конференции")
    registration_deadline = models.DateTimeField("Дедлайн регистрации/подачи")
    notification_date = models.DateField("Дата оглашения результатов")

    program = CKEditor5Field("Программа конференции", config_name='default', blank=True)
    committee = CKEditor5Field("Оргкомитет (текст)", config_name='default', blank=True,
                               help_text="Общее описание комитета, если нужно")
    participation_fee = CKEditor5Field("Плата за участие", config_name='default', blank=True)
    submission_format = CKEditor5Field("Формат работы", config_name='default', blank=True)

    poster = models.ImageField("Постер (широкоугольный)", upload_to='conf/posters/')
    is_active = models.BooleanField("Активна", default=True)

    class Meta:
        verbose_name = "Kонференция"
        verbose_name_plural = "Kонференции"

    @classmethod
    def get_current(cls):
        return cls.objects.order_by('-id').first()

    def save(self, *args, **kwargs):
        if self.poster:
            try:
                img = Image.open(self.poster)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                output = BytesIO()
                img.save(output, format='WebP', quality=80)
                output.seek(0)

                new_name = os.path.splitext(self.poster.name)[0] + '.webp'
                self.poster.save(new_name, ContentFile(output.read()), save=False)
            except Exception as e:
                print(f"Ошибка обработки изображения: {e}")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

def get_conference_pdf_path(instance, filename):
    return f'submissions/{instance.id}/{filename}'

def get_submission_file_path(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f"{instance.version_number}.{ext}"
    return os.path.join('submissions', str(instance.submission.id), new_filename)

class Submission(models.Model):
    STATUS_CHOICES = [
        ('under_review', 'На проверке'),
        ('revision', 'Требуется доработка'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено'),
        ('ready_for_print', 'Готово к печати (верстка)'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='submissions')

    title = models.CharField("Название работы", max_length=500)
    authors_list = models.TextField("Список соавторов", help_text="ФИО, ученая степень, организация (каждый соавтор с новой строки или через запятую)", blank=True)
    abstract_text = models.TextField("Аннотация", help_text="Краткое описание работы (200-500 слов)", blank=True)
    keywords = models.CharField("Ключевые слова", max_length=255, help_text="Введите 3-5 слов через запятую", blank=True)
    
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='under_review')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    final_file = models.FileField(
        "Финальный файл (PDF)", 
        upload_to=get_conference_pdf_path, 
        blank=True, 
        null=True, 
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    
    class Meta:
        unique_together = ('user', 'conference')
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = Submission.objects.get(pk=self.pk)
            if old_instance.status != 'ready_for_print' and self.status == 'ready_for_print':
                self.convert_to_pdf()
        super().save(*args, **kwargs)
    
    def convert_to_pdf(self):
        """Конвертирует последний docx в pdf и сохраняет в папку заявки"""
        last_version = self.versions.order_by('-created_at').first()
        if not last_version or not last_version.file:
            return

        input_path = last_version.file.path
        output_dir = os.path.join(settings.MEDIA_ROOT, 'submissions', str(self.id))
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        try:
            # Вызов LibreOffice
            subprocess.run([
                'soffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', output_dir,
                input_path
            ], check=True, capture_output=True)

            filename_docx = os.path.basename(input_path)
            filename_pdf = os.path.splitext(filename_docx)[0] + '.pdf'
            
            relative_path = os.path.join('submissions', str(self.id), filename_pdf)
            self.final_file = relative_path.replace('\\', '/')
            
            logger.info(f"Успешная конвертация: {filename_pdf} для ID {self.id}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка LibreOffice (ID {self.id}): {e.stderr}")
        except Exception as e:
            logger.exception(f"Ошибка при конвертации заявки ID {self.id}: {e}")
        
    def __str__(self):
        return f"{self.title[:50]}... ({self.user.last_name})"

    def get_version_count(self):
        return self.versions.count()


class SubmissionVersion(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='versions')
    file = models.FileField(
        "Файл версии (DOC/DOCX)",
        upload_to=get_submission_file_path,
        validators=[FileExtensionValidator(allowed_extensions=['doc', 'docx'])]
    )
    version_number = models.PositiveIntegerField("Номер версии", default=1)
    author_comment = models.TextField("Комментарий автора", blank=True)
    admin_comment = models.TextField("Ответ оргкомитета", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Версия работы"
        verbose_name_plural = "Версии работы"
        ordering = ['-created_at']

class Proceedings(models.Model):
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='proceedings_archive')
    file = models.FileField("Файл сборника", upload_to='conf/proceedings/')
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    
    class Meta:
        verbose_name = "Сборник трудов"
        verbose_name_plural = "Сборники трудов"
        ordering = ['-created_at']

    def __str__(self):
        return f"Сборник {self.conference.short_title}"


class GalleryMedia(models.Model):
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='media')
    file = models.FileField("Файл (Фото или Видео)", upload_to='conf/gallery/')
    is_video = models.BooleanField("Это видео?", default=False)
    caption = models.CharField("Подпись", max_length=255, blank=True)

    class Meta:
        verbose_name = "Медиа галереи"
        verbose_name_plural = "Галерея"


class Document(models.Model):
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField("Название документа", max_length=255)
    file = models.FileField("Файл документа", upload_to='conf/documents/')
    description = models.TextField("Описание", blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title


class ContactPerson(models.Model):
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='contacts')
    full_name = models.CharField("ФИО", max_length=255)
    position = models.CharField("Должность", max_length=255)
    email = models.EmailField("Email")
    phone = models.CharField("Телефон", max_length=50, blank=True)
    photo = models.ImageField("Фотография", upload_to='conf/contacts/', blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Контактное лицо"
        verbose_name_plural = "Контактные лица"
        ordering = ['order', 'full_name']

    def __str__(self):
        return self.full_name


class CommitteeMember(models.Model):
    ROLE_CHOICES = [
        ('chair', 'Председатель'),
        ('vice_chair', 'Зам. председателя'),
        ('member', 'Член комитета'),
        ('secretary', 'Секретарь'),
    ]

    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='committee_members')
    full_name = models.CharField("ФИО", max_length=255)
    role = models.CharField("Роль", max_length=20, choices=ROLE_CHOICES, default='member')
    position = models.CharField("Должность", max_length=500)
    organization = models.CharField("Организация", max_length=500, blank=True)
    photo = models.ImageField("Фотография", upload_to='conf/committee/', blank=True)
    bio = models.TextField("Биография", blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Член комитета"
        verbose_name_plural = "Члены комитета"
        ordering = ['order', 'full_name']

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"