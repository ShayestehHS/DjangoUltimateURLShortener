# Generated by Django 5.0.8 on 2024-09-21 03:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('urls', '0002_urlusage_seen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='url',
            name='token',
            field=models.CharField(blank=True, editable=False, max_length=5, null=True),
        ),
    ]
