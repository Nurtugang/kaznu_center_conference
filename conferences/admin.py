from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline
from .models import (
    User, Conference, Submission, GalleryMedia,
    SubmissionVersion, Document, ContactPerson, CommitteeMember
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'last_name', 'first_name', 'organization', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Доп. информация', {'fields': ('organization',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Доп. информация', {'fields': ('organization',)}),
    )


@admin.register(Conference)
class ConferenceAdmin(TranslationAdmin):
    list_display = ('title', 'start_date', 'is_active', 'slug')
    list_filter = ('is_active', 'start_date')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }

    fieldsets = (
        ('Основная информация', {
            'fields': (
            'title', 'short_title', 'slug', 'description', 'location', 'location_description', 'poster', 'is_active')
        }),
        ('Даты', {
            'fields': ('start_date', 'registration_deadline', 'notification_date')
        }),
        ('Контент страниц', {
            'fields': ('program', 'committee', 'participation_fee', 'submission_format'),
            'classes': ('collapse',)
        }),
    )


class SubmissionVersionInline(admin.TabularInline):
    model = SubmissionVersion
    extra = 0
    readonly_fields = ('version_number', 'author_comment', 'created_at')
    fields = ('version_number', 'file', 'author_comment', 'admin_comment', 'created_at')
    can_delete = False


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'conference', 'status', 'get_version_count', 'updated_at')
    list_filter = ('status', 'conference')
    search_fields = ('title', 'user__last_name', 'user__email')
    list_editable = ('status',)

    inlines = [SubmissionVersionInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'conference', 'status', 'title', 'authors_list')
        }),
        ('Контент', {
            'fields': ('abstract_text', 'keywords')
        }),
    )

    def get_version_count(self, obj):
        return obj.versions.count()

    get_version_count.short_description = "Версий"


@admin.register(GalleryMedia)
class GalleryMediaAdmin(TranslationAdmin):
    list_display = ('conference', 'caption', 'is_video', 'file')
    list_filter = ('conference', 'is_video')


@admin.register(Document)
class DocumentAdmin(TranslationAdmin):
    list_display = ('title', 'conference', 'uploaded_at')
    list_filter = ('conference', 'uploaded_at')
    search_fields = ('title', 'description')


@admin.register(ContactPerson)
class ContactPersonAdmin(TranslationAdmin):
    list_display = ('full_name', 'position', 'email', 'conference', 'order')
    list_filter = ('conference',)
    list_editable = ('order',)
    search_fields = ('full_name', 'email')


@admin.register(CommitteeMember)
class CommitteeMemberAdmin(TranslationAdmin):
    list_display = ('full_name', 'role', 'position', 'conference', 'order')
    list_filter = ('conference', 'role')
    list_editable = ('order',)
    search_fields = ('full_name', 'position', 'organization')