# Generated by Django 4.2.5 on 2023-09-24 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tours', '0002_tour_provider'),
    ]

    operations = [
        migrations.AddField(
            model_name='tour',
            name='price_on_request',
            field=models.BooleanField(default=False, verbose_name='Цена по запросу'),
        ),
    ]
