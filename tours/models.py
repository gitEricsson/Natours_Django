from django.db import models

class Tour(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()
    maxGroupSize = models.IntegerField()
    difficulty = models.CharField(max_length=50)
    ratingsAverage = models.DecimalField(max_digits=2, decimal_places=1, default=4.5)
    ratingsQuantity = models.IntegerField(default=0)
    description = models.TextField()
    imageCover = models.ImageField(upload_to='tours/')
    startDates = models.JSONField()

    def __str__(self):
        return self.name
