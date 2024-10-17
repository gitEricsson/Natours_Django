from django.db import models
from tours.models import Tour

class Appointment(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    participants = models.PositiveIntegerField(default=0)
    sold_out = models.BooleanField(default=False)

    def __str__(self):
        return f"Appointment for {self.tour.name} on {self.date}"

    class Meta:
        unique_together = ('tour', 'date')
