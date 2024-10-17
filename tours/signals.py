from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Tour
from appointments.models import Appointment

@receiver(post_save, sender=Tour)
def create_appointments(sender, instance, **kwargs):
    for date in instance.start_dates:
        Appointment.objects.create(date=date, tour=instance)

@receiver(pre_save, sender=Tour)
def update_appointments(sender, instance, **kwargs):
    if instance.id:
        tour = Tour.objects.get(id=instance.id)
        
        # Update appointments if start_dates are changed
        if instance.start_dates != tour.start_dates:
            for date in instance.start_dates:
                Appointment.objects.create(date=date, tour=instance)
        
        # Update appointments if max_group_size is changed
        if instance.max_group_size != tour.max_group_size:
            appointments = Appointment.objects.filter(tour=instance)
            for appointment in appointments:
                appointment.sold_out = appointment.participants >= instance.max_group_size
                appointment.save()
