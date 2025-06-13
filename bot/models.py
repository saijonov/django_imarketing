from django.db import models
from django.utils.translation import gettext_lazy as _

class User(models.Model):
    tg_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[('male', _('Male')), ('female', _('Female'))]
    )
    birthday = models.DateField()
    location = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    language = models.CharField(
        max_length=2,
        choices=[('uz', _('Uzbek')), ('ru', _('Russian'))],
        default='uz'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} {self.lastname}"

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

class Vacancy(models.Model):
    title = models.CharField(max_length=200)
    short_text_uz = models.TextField()
    short_text_ru = models.TextField()
    full_text_uz = models.TextField()
    full_text_ru = models.TextField()
    image = models.ImageField(upload_to='vacancies/')
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    custom_fields = models.JSONField(default=dict, blank=True)  # Using Django's built-in JSONField
    
    class Meta:
        verbose_name_plural = 'Vacancies'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class VacancyField(models.Model):
    """Model for custom vacancy fields defined by admin"""
    FIELD_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('file', 'File Upload'),
        ('choice', 'Multiple Choice'),
    ]
    
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=100)
    label_uz = models.CharField(max_length=200)
    label_ru = models.CharField(max_length=200)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    required = models.BooleanField(default=False)
    choices = models.TextField(blank=True, help_text='For multiple choice fields, enter choices one per line')
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.vacancy.title} - {self.name}"

class Feedback(models.Model):
    FEEDBACK_TYPES = [
        ('complaint', 'Complaint'),
        ('suggestion', 'Suggestion'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.name} - {self.type}"

class AboutSection(models.Model):
    text_uz = models.TextField()
    text_ru = models.TextField()
    image = models.ImageField(upload_to='about/')
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return "About Section"

    class Meta:
        verbose_name = _('About Section')
        verbose_name_plural = _('About Sections')
