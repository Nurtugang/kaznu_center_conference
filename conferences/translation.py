from modeltranslation.translator import register, TranslationOptions
from .models import (
    Conference,
    Document,
    GalleryMedia,
    ContactPerson,
    CommitteeMember
)

@register(Conference)
class ConferenceTranslationOptions(TranslationOptions):
    fields = (
        'title',
        'short_title',
        'description',
        'location',
        'location_description',
        'program',
        'committee',
        'participation_fee',
        'submission_format',
    )

@register(Document)
class DocumentTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

@register(GalleryMedia)
class GalleryMediaTranslationOptions(TranslationOptions):
    fields = ('caption',)

@register(ContactPerson)
class ContactPersonTranslationOptions(TranslationOptions):
    fields = ('position',)

@register(CommitteeMember)
class CommitteeMemberTranslationOptions(TranslationOptions):
    fields = ('position', 'organization', 'bio')