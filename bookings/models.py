from django.db import models
from tours.models import Tour
from users.models import User
from appointments.models import Appointment

class Booking(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='bookings')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.email}'s booking for {self.tour.name}"

    class Meta:
        unique_together = ('user', 'appointment')
