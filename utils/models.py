from django.db import models

from utils.validators import validate_not_naive

class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, validators=[validate_not_naive])
    updated_at = models.DateTimeField(auto_now=True, validators=[validate_not_naive])

    class Meta:
        abstract = True
