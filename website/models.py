from django.db import models
from django.utils.translation import gettext_lazy as _
from bot.models import Vacancy

class Application(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='applications')
    name = models.CharField(_('Ism'), max_length=255)
    email = models.EmailField(_('Email'))
    phone = models.CharField(_('Telefon'), max_length=20)
    cover_letter = models.TextField(_('Xat'), blank=True)
    answers = models.JSONField(default=dict, blank=True)  # Store answers to custom fields
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.vacancy.title}"

    class Meta:
        verbose_name = _('Application')
        verbose_name_plural = _('Applications')
        ordering = ['-created_at']

    def get_extra_question_label(self):
        return self.extra_question_title if self.extra_question_title else _('Extra Question')
