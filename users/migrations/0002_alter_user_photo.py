# Generated by Django 5.0.7 on 2024-09-14 05:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='dev-data/data/img/'),
        ),
    ]
