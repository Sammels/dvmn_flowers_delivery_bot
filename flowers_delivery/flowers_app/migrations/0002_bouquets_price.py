# Generated by Django 4.2.4 on 2023-08-25 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flowers_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bouquets',
            name='price',
            field=models.IntegerField(default=0),
        ),
    ]
