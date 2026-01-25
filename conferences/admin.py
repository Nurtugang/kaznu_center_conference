from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Conference, Submission, GalleryMedia, SubmissionVersion

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
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'is_active', 'slug')
    list_filter = ('is_active', 'start_date')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}

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
class GalleryMediaAdmin(admin.ModelAdmin):
    list_display = ('conference', 'caption', 'is_video', 'file')
    list_filter = ('conference', 'is_video')