# Generated by Django 5.0.8 on 2024-09-19 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('urls', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='urlusage',
            name='seen',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]