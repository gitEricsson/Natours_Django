from django.db import models
from users.models import User
from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.db import models as gis_models

class Point(models.Model):
    description = models.CharField(max_length=255)
    type = models.CharField(max_length=50, default='Point')
    coordinates = coordinates = ArrayField(models.FloatField(), size=2)
    geometry = gis_models.PointField(geography=True, srid=4326, null=True)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.description

class Location(Point):
    day = models.IntegerField()

    class Meta:
        ordering = ['day']

class Tour(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('difficult', 'Difficult'),
    ]

    name = models.CharField(max_length=255)
    duration = models.IntegerField()
    max_group_size = models.IntegerField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    ratings_average = models.DecimalField(max_digits=3, decimal_places=2, default=4.5)
    ratings_quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    summary = models.TextField()
    description = models.TextField()
    image_cover = models.ImageField(upload_to='tours/covers/')
    images = ArrayField(models.CharField(max_length=255), blank=True)
    start_dates = ArrayField(models.DateTimeField())
    start_location = models.ForeignKey(Point, on_delete=models.PROTECT, related_name='tours_starting')
    locations = models.ManyToManyField(Location, related_name='tours')
    guides = models.ManyToManyField(User, related_name='tours')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-ratings_average']