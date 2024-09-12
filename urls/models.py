from datetime import datetime, timezone, timedelta
from random import choice

from django.conf import settings
from django.contrib.postgres.indexes import HashIndex
from django.db import models
from django.utils.timezone import now
from rest_framework.exceptions import ValidationError
from string import ascii_letters, digits
from urls.querysets import UrlQuerySet
from utils.models import TimeStampModel

SIZE = settings.URL_SHORTENER_MAXIMUM_URL_CHARS
BASE_URL = settings.URL_SHORTENER_BASE_URL
MAXIMUM_URL_CHARS = settings.URL_SHORTENER_MAXIMUM_URL_CHARS
MAXIMUM_RECURSION_DEPTH = settings.URL_SHORTENER_MAXIMUM_RECURSION_DEPTH
READY_TO_SET_TOKEN_URL = settings.URL_SHORTENER_READY_TO_SET_TOKEN_URL
DEFAULT_EXPIRATION_DAYS = settings.URL_SHORTENER_DEFAULT_EXPIRATION_DAYS
User = settings.AUTH_USER_MODEL
AVAILABLE_CHARS = ascii_letters + digits


def is_https(value):
    if not value.startswith('https://'):
        raise ValidationError('The URL should start with https://')


def get_default_expiration_date():
    return now() + timedelta(days=DEFAULT_EXPIRATION_DAYS)


def validate_not_naive(value):
    if value is None:
        return  # Skip validation if value is None (handle this according to your use case)

    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise ValidationError('The datetime must be timezone-aware.')


class Url(TimeStampModel):
    url = models.URLField(max_length=255, validators=[is_https], null=True, blank=True)
    token = models.CharField(max_length=MAXIMUM_URL_CHARS, editable=False)
    expiration_date = models.DateTimeField(default=get_default_expiration_date)

    objects = UrlQuerySet().as_manager()

    @property
    def short_url(self):
        return f"{settings.URL_SHORTENER_BASE_URL}/{self.token}/"

    @property
    def is_active(self):
        if self.expiration_date and self.expiration_date <= now():
            return False
        return True

    @classmethod
    def _create_random_string(cls):
        return "".join([choice(AVAILABLE_CHARS) for _ in range(5)])

    @classmethod
    def create_token(cls):
        token: str
        for _ in range(MAXIMUM_RECURSION_DEPTH):
            token = cls._create_random_string()
            if not Url.objects.all_actives().filter(token=token).exists():
                return token
        raise Exception("Maximum recursion depth occurred.")

    @classmethod
    def validate_token_is_unique(cls, token):
        if Url.objects.all_actives().filter(token=token).exists():
            raise ValidationError("Valid url object with this token already exists.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.url).replace("https://", "")

    class Meta:
        indexes = [
            models.Index(fields=['url'], name='ready_to_set_token_urls', condition=models.Q(url=READY_TO_SET_TOKEN_URL)),
            HashIndex(fields=["token"])
        ]


class UrlUser(models.Model):
    url = models.ForeignKey(Url, on_delete=models.CASCADE, related_name="url_users")
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field="username")

    def __str__(self):
        return str(self.user)


class UrlUsage(models.Model):
    url = models.ForeignKey(Url, on_delete=models.CASCADE, related_name="usages")
    created_at = models.DateTimeField(validators=[validate_not_naive])

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)