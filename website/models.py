from django.db import models
from django.utils.translation import gettext_lazy as _
from bot.models import Vacancy

class Application(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='applications')
    name = models.CharField(_('Full Name'), max_length=255)
    email = models.EmailField(_('Email'))
    phone = models.CharField(_('Phone'), max_length=20)
    resume = models.FileField(_('Resume'), upload_to='resumes/')
    cover_letter = models.TextField(_('Cover Letter'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.vacancy.title}"

    class Meta:
        verbose_name = _('Application')
        verbose_name_plural = _('Applications')
        ordering = ['-created_at']
