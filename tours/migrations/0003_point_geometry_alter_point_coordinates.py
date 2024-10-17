# Generated by Django 5.0.7 on 2024-09-16 22:56

import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields
from django.db import migrations, models
from django.contrib.gis.geos import Point

def populate_geometry(apps, schema_editor):
    PointModel = apps.get_model('tours', 'Point')

    for point in PointModel.objects.all():
        if point.coordinates:
            # Assuming coordinates is [longitude, latitude]
            point.geometry = Point(point.coordinates[0], point.coordinates[1], srid=4326)
            point.save()



class Migration(migrations.Migration):

    dependencies = [
        ('tours', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='point',
            name='geometry',
            field=django.contrib.gis.db.models.fields.PointField(geography=True, null=True, srid=4326),
        ),
        migrations.RunPython(populate_geometry),
    ]
