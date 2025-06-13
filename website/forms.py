from django import forms
from .models import Application
from django.utils.translation import gettext_lazy as _

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['name', 'email', 'phone', 'location', 'cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, vacancy=None, language='uz', **kwargs):
        super().__init__(*args, **kwargs)
        self.vacancy = vacancy
        self.language = language

        # Set labels based on language
        labels_uz = {
            'name': 'To\'liq ism',
            'email': 'Email',
            'phone': 'Telefon raqam',
            'location': 'Yashash joyi',
            'cover_letter': 'Xat',
        }
        labels_ru = {
            'name': 'ФИО',
            'email': 'Email',
            'phone': 'Номер телефона',
            'location': 'Место жительства',
            'cover_letter': 'Письмо',
        }

        # Apply labels based on language
        labels = labels_uz if language == 'uz' else labels_ru
        for field_name, label in labels.items():
            self.fields[field_name].label = label

        # Add custom fields from vacancy
        if vacancy:
            for field in vacancy.fields.all().order_by('order'):
                field_name = f'custom_{field.id}'
                label = field.label_uz if language == 'uz' else field.label_ru
                self.fields[field_name] = forms.CharField(
                    label=label,
                    required=field.required,
                    widget=forms.Textarea(attrs={'rows': 4}) if field.field_type == 'text' else forms.TextInput()
                )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.vacancy:
            instance.vacancy = self.vacancy
            # Save custom field answers
            answers = {}
            for field in self.vacancy.fields.all():
                field_name = f'custom_{field.id}'
                if field_name in self.cleaned_data:
                    answers[str(field.id)] = self.cleaned_data[field_name]
            instance.answers = answers
        if commit:
            instance.save()
        return instance 