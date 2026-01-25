import re
import os
from PIL import Image
from io import BytesIO
from django.utils import timezone
from django.core.files.base import ContentFile
from django_ckeditor_5.fields import CKEditor5Field
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator


class User(AbstractUser):
    organization = models.CharField("Организация", max_length=255, blank=True)

    email = models.EmailField("Электронная почта", unique=True)

    def __str__(self):
        full_name = f"{self.last_name} {self.first_name}".strip()
        return full_name if full_name else self.username

class Conference(models.Model):
    title = models.CharField("Название конференции", max_length=500)
    short_title = models.CharField("Краткое название", max_length=100)
    slug = models.SlugField("URL-префикс", unique=True)
    description = models.TextField("Описание")
    location = models.CharField("Место проведения", max_length=255)
    
    start_date = models.DateField("Дата начала конференции")
    registration_deadline = models.DateTimeField("Дедлайн регистрации/подачи")
    notification_date = models.DateField("Дата оглашения результатов")
    
    program = CKEditor5Field("Программа конференции", config_name='default', blank=True)
    committee = CKEditor5Field("Оргкомитет", config_name='default', blank=True)
    
    poster = models.ImageField("Постер (широкоугольный)", upload_to='conf/posters/')
    
    is_active = models.BooleanField("Активна", default=True)
    
    @classmethod
    def get_current(cls):
        return cls.objects.order_by('-id').first()

    def save(self, *args, **kwargs):
        if self.poster:
            img = Image.open(self.poster)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            output = BytesIO()
            img.save(output, format='WebP', quality=80)
            output.seek(0)
            
            name = os.path.splitext(self.poster.name)[0] + '.webp'
            self.poster.save(name, ContentFile(output.read()), save=False)
            
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.title

class Submission(models.Model):
    STATUS_CHOICES = [
        ('under_review', 'На проверке'),
        ('revision', 'Требуется доработка'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='submissions')
    
    title = models.CharField("Название работы", max_length=500)
    authors_list = models.TextField(
        "Список соавторов", 
        help_text="ФИО, ученая степень, организация (каждый соавтор с новой строки или через запятую)",
        blank=True
    )
    abstract_text = models.TextField(
        "Аннотация", 
        help_text="Краткое описание работы (200-500 слов)",
        blank=True
    )
    keywords = models.CharField(
        "Ключевые слова", 
        max_length=255, 
        help_text="Введите 3-5 слов через запятую",
        blank=True
    )
    
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='under_review')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'conference')
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def __str__(self):
        return f"{self.title[:50]}... ({self.user.last_name})"

    def get_latest_version(self):
        """Возвращает последний загруженный файл"""
        return self.versions.order_by('-created_at').first()

    def get_version_count(self):
        """Возвращает общее количество версий"""
        return self.versions.count()
    
    @property
    def keywords_list(self):
        if not self.keywords:
            return []
        words = re.split(r'[,\s]+', self.keywords)
        return [w.strip() for w in words if w.strip()]

class SubmissionVersion(models.Model):
    submission = models.ForeignKey(
        Submission, 
        on_delete=models.CASCADE, 
        related_name='versions'
    )
    
    file = models.FileField(
        "Файл версии", 
        upload_to='submissions/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
    )
    
    version_number = models.PositiveIntegerField("Номер версии", default=1)
    
    author_comment = models.TextField("Комментарий автора", blank=True, help_text="Что изменилось в этой версии?")
    admin_comment = models.TextField("Ответ оргкомитета", blank=True, help_text="Замечания к этой конкретной версии")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Версия работы"
        verbose_name_plural = "Версии работы"
        ordering = ['-created_at']

    def __str__(self):
        return f"v{self.version_number} — {self.created_at.strftime('%d.%m.%Y')}"
        
class GalleryMedia(models.Model):
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='media')
    file = models.FileField("Файл (Фото или Видео)", upload_to='conf/gallery/')
    is_video = models.BooleanField("Это видео?", default=False)
    caption = models.CharField("Подпись", max_length=255, blank=True)

    class Meta:
        verbose_name = "Медиа галереи"
        verbose_name_plural = "Галерея"