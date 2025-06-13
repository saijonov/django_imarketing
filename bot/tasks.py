from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from .models import Vacancy
from website.models import Application
from django.utils.translation import gettext as _
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_vacancy_notification(vacancy_id):
    """
    Send email notifications to all users who have provided their email
    when a new vacancy is created.
    """
    logger.info(f"Starting email notification task for vacancy {vacancy_id}")
    try:
        vacancy = Vacancy.objects.get(id=vacancy_id)
        logger.info(f"Found vacancy: {vacancy.title}")
        
        # Get unique email addresses from applications using a set to ensure uniqueness
        email_set = set(Application.objects.filter(
            Q(email__isnull=False) & ~Q(email='')
        ).values_list('email', flat=True))
        
        logger.info(f"Found {len(email_set)} unique email addresses from applications")
        
        if not email_set:
            logger.warning("No email addresses found in applications")
            return "No email addresses found in applications"
        
        # Get the site URL from settings
        site_url = getattr(settings, 'SITE_URL', 'http://192.168.1.19:8000')
        
        # Prepare email content in Uzbek
        subject = _("Yangi vakansiya: {}").format(vacancy.title)
        
        message = _("""
Hurmatli mijoz!

Imarketing kompaniyasida yangi vakansiya ochildi:

Vakansiya: {}
Qisqa ma'lumot: {}

Batafsil ma'lumot uchun quyidagi havolani bosing:
{}

Hurmat bilan,
Imarketing jamoasi
""").format(
            vacancy.title,
            vacancy.short_text_uz,
            f"{site_url}/vacancy/{vacancy.id}?lang=uz"
        )
        
        # Send email to each unique email address
        for email in email_set:
            logger.info(f"Sending email to {email}")
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False  # Changed to False to see any email errors
                )
                logger.info(f"Successfully sent email to {email}")
            except Exception as e:
                logger.error(f"Failed to send email to {email}: {str(e)}")
        
        return f"Successfully sent notifications to {len(email_set)} users"
        
    except Vacancy.DoesNotExist:
        logger.error(f"Vacancy {vacancy_id} not found")
        return "Vacancy not found"
    except Exception as e:
        logger.error(f"Error in send_vacancy_notification: {str(e)}")
        return f"Error sending notifications: {str(e)}" 