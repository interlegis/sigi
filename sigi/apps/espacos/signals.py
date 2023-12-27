import traceback
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone
from sigi.apps.espacos.models import Reserva


@receiver(pre_delete, sender=Reserva)
def reserva_pre_delete(sender, **kwargs):
    origin = kwargs.get("origin", None)
    if origin and origin.count() == Reserva.objects.count():
        stack_array = [f"At {timezone.localtime()} all records deleted:"]
        stack_array.extend(traceback.format_stack())
        send_mail(
            subject="Armadilha deleção de reservas",
            message="\n".join(stack_array),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email for name, email in settings.ADMINS],
            fail_silently=True,
        )
