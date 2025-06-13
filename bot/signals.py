from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Vacancy
from .tasks import send_vacancy_notification
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Vacancy)
def notify_users_new_vacancy(sender, instance, created, **kwargs):
    """
    Signal handler to send email notifications when a new vacancy is created
    """
    logger.info(f"Signal triggered for vacancy {instance.id}. Created: {created}, Published: {instance.is_published}")
    if created and instance.is_published:
        # Trigger the Celery task asynchronously
        logger.info(f"Queueing email notification task for vacancy {instance.id}")
        send_vacancy_notification.delay(instance.id) 