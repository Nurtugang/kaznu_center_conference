import os
import re
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Submission

from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox

User = get_user_model()


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput()
    )
    password_confirm = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput()
    )

    captcha = ReCaptchaField(
        label="Капча",
        widget=ReCaptchaV2Checkbox(attrs={
            'data-theme': 'light',
            'data-size': 'normal',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'last_name', 'first_name', 'organization']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        common_class = "appearance-none block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:border-[#8a1538] focus:ring-1 focus:ring-[#8a1538] sm:text-sm transition-all"

        for field_name, field in self.fields.items():
            if field_name != 'captcha':
                field.widget.attrs.update({'class': common_class})

            if field_name == 'organization':
                field.widget.attrs['placeholder'] = 'Например: КазНУ им. аль-Фараби'

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if not password:
            return password

        if len(password) < 8:
            raise ValidationError("Пароль должен содержать минимум 8 символов.")

        if not re.search(r'\d', password):
            raise ValidationError("Пароль должен содержать хотя бы одну цифру.")

        if not re.search(r'[A-ZА-Я]', password):
            raise ValidationError("Пароль должен содержать хотя бы одну заглавную букву.")

        if not re.search(r'[a-zа-я]', password):
            raise ValidationError("Пароль должен содержать хотя бы одну строчную букву.")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Пароль должен содержать хотя бы один специальный символ (!@#$%).")

        return password

    def clean_password_confirm(self):
        p1 = self.cleaned_data.get('password')
        p2 = self.cleaned_data.get('password_confirm')

        if p1 and p2 and p1 != p2:
            raise ValidationError("Введенные пароли не совпадают.")
        return p2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким Email уже зарегистрирован.")
        return email


class SubmissionForm(forms.ModelForm):
    file = forms.FileField(
        label="Файл (тезисы)",
        required=True,
        help_text="Допустимые форматы: PDF, DOC, DOCX. Макс. 10МБ."
    )

    author_comment = forms.CharField(
        label="Комментарий к работе",
        required=False,
        widget=forms.Textarea()
    )

    class Meta:
        model = Submission
        fields = ['title', 'authors_list', 'abstract_text', 'keywords']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        input_class = "appearance-none block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:border-[#8a1538] focus:ring-1 focus:ring-[#8a1538] sm:text-sm transition-all"

        textarea_class = f"{input_class} min-h-[120px]"

        file_class = "block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-bold file:bg-[#8a1538]/10 file:text-[#8a1538] hover:file:bg-[#8a1538]/20 cursor-pointer"

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = textarea_class
                field.widget.attrs['rows'] = 4
            elif isinstance(field.widget, (forms.FileInput, forms.ClearableFileInput)):
                field.widget.attrs['class'] = file_class
            else:
                field.widget.attrs['class'] = input_class

            if field_name == 'title':
                field.widget.attrs['placeholder'] = 'Введите полное название работы'
            elif field_name == 'keywords':
                field.widget.attrs['placeholder'] = 'Экология, экономика, цифровизация...'
            elif field_name == 'authors_list':
                field.widget.attrs['placeholder'] = 'Иванов И.И. (КазНУ), Петров П.П. (МГУ)...'
            elif field_name == 'author_comment':
                field.widget.attrs['placeholder'] = 'Дополнительная информация для рецензента...'

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            ext = os.path.splitext(file.name)[1].lower()
            valid_extensions = ['.pdf', '.doc', '.docx']
            if ext not in valid_extensions:
                raise ValidationError("Неподдерживаемый формат файла. Пожалуйста, загрузите PDF или Word документ.")

            if file.size > 10 * 1024 * 1024:
                raise ValidationError("Файл слишком большой. Максимальный размер — 10 МБ.")

        return file