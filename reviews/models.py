from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from tours.models import Tour

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    review = models.TextField(null=False, blank=False)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user.email} for {self.tour.name}'