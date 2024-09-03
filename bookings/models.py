from django.db import models
from users.models import User
from tours.models import Tour

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    booking_date = models.DateField()

    def __str__(self):
        return f'{self.user.username} - {self.tour.name}'