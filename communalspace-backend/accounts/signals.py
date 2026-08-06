from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import EmailVerificationToken, User


@receiver(post_save, sender=User)
def send_verification_email(sender, instance, created, **kwargs):
    if created:
        token = EmailVerificationToken.objects.create(user=instance)
        verification_link = (
            f"http://localhost:8000/api/accounts/verify-email/{token.token}/"
        )
        send_mail(
            subject="Verify your CommunalSpace account",
            message=f"Hi {instance.first_name},\n\nClick the link below to verify your account:\n\n{verification_link}\n\nIf you did not register, ignore this email.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
        )
