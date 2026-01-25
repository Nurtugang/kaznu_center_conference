from django import forms
from django.contrib.auth import get_user_model
from .models import Submission, SubmissionVersion
from django.core.exceptions import ValidationError
import os

User = get_user_model()

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'class': 'w-full px-5 py-3 bg-gray-50 border border-gray-100 rounded-xl outline-none'}))
    password_confirm = forms.CharField(label="Подтверждение", widget=forms.PasswordInput(attrs={'class': 'w-full px-5 py-3 bg-gray-50 border border-gray-100 rounded-xl outline-none'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'last_name', 'first_name', 'organization']
        widgets = {
            field: forms.TextInput(attrs={'class': 'w-full px-5 py-3 bg-gray-50 border border-gray-100 rounded-xl outline-none'}) 
            for field in ['username', 'email', 'last_name', 'first_name', 'organization']
        }

    def clean_password_confirm(self):
        p1 = self.cleaned_data.get('password')
        p2 = self.cleaned_data.get('password_confirm')
        if p1 != p2: raise forms.ValidationError("Пароли не совпадают")
        return p2

class SubmissionForm(forms.ModelForm):
    file = forms.FileField(
        label="Файл (тезисы)", 
        required=True,
        help_text="Допустимые форматы: PDF, DOC, DOCX"
    )
    
    author_comment = forms.CharField(
        label="Комментарий к работе",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-5 py-3 bg-gray-50 border border-gray-100 rounded-xl outline-none focus:border-brand/30 transition-colors',
            'rows': 3,
            'placeholder': 'Дополнительная информация для оргкомитета (необязательно)...'
        })
    )
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            ext = os.path.splitext(file.name)[1].lower()
            valid_extensions = ['.pdf', '.doc', '.docx']
            if not ext in valid_extensions:
                raise ValidationError("Неподдерживаемый формат файла. Пожалуйста, загрузите PDF или Word документ.")
            
            if file.size > 10 * 1024 * 1024:
                raise ValidationError("Файл слишком большой. Максимальный размер — 10 МБ.")
        return file

    class Meta:
        model = Submission
        fields = ['title', 'authors_list', 'abstract_text', 'keywords']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-5 py-3 bg-gray-50 border border-gray-100 rounded-xl outline-none focus:border-brand/30 transition-colors',
                'placeholder': 'Введите название работы'
            }),
            'authors_list': forms.Textarea(attrs={
                'class': 'w-full px-5 py-3 bg-gray-50 border border-gray-100 rounded-xl outline-none focus:border-brand/30 transition-colors',
                'rows': 3,
                'placeholder': 'Иванов И.И. (КазНУ), Петров П.П. (МГУ)...'
            }),
            'abstract_text': forms.Textarea(attrs={
                'class': 'w-full px-5 py-3 bg-gray-50 border border-gray-100 rounded-xl outline-none focus:border-brand/30 transition-colors',
                'rows': 5,
                'placeholder': 'Краткое содержание вашей работы...'
            }),
            'keywords': forms.TextInput(attrs={
                'class': 'w-full px-5 py-3 bg-gray-50 border border-gray-100 rounded-xl outline-none focus:border-brand/30 transition-colors',
                'placeholder': 'Экология, ЦУР, инновации'
            }),
            
        }