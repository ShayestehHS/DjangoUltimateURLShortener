from datetime import timedelta
from random import choice
from django.conf import settings
from django.contrib.postgres.indexes import HashIndex
from django.db import models
from django.utils.timezone import now
from rest_framework.exceptions import ValidationError
from string import ascii_letters, digits
from urls.querysets import UrlManager
from utils.models import TimeStampModel
from utils.validators import is_https

SIZE = settings.URL_SHORTENER_MAXIMUM_URL_CHARS
BASE_URL = settings.URL_SHORTENER_BASE_URL
MAXIMUM_URL_CHARS = settings.URL_SHORTENER_MAXIMUM_URL_CHARS
MAXIMUM_RECURSION_DEPTH = settings.URL_SHORTENER_MAXIMUM_RECURSION_DEPTH
READY_TO_SET_TOKEN_URL = settings.URL_SHORTENER_READY_TO_SET_TOKEN_URL
DEFAULT_EXPIRATION_DAYS = settings.URL_SHORTENER_DEFAULT_EXPIRATION_DAYS
User = settings.AUTH_USER_MODEL
AVAILABLE_CHARS = ascii_letters + digits


def get_default_expiration_date():
    return now() + timedelta(days=DEFAULT_EXPIRATION_DAYS)


class Url(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field="username")
    url = models.URLField(max_length=255, validators=[is_https], null=True, blank=True,unique=True)
    token = models.CharField(max_length=MAXIMUM_URL_CHARS, editable=False,null=True,blank=True,unique=True)
    expiration_date = models.DateTimeField(default=get_default_expiration_date)
    new_url = models.CharField(max_length=255,null=True,blank=True,unique=True)

    objects = UrlManager()
    class Meta:
        unique_together = ('user', 'url')

    @property
    def short_url(self):
        if not self.token:
            # Ensure 'token' is not None before displaying 'short_url' to avoid empty URL path
            return "-"
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
            models.Index(
                fields=["url"],
                name="ready_to_set_token_urls",
                condition=models.Q(url=READY_TO_SET_TOKEN_URL),
            ),
            HashIndex(fields=["token"]),
        ]




class UrlUsage(TimeStampModel):
    url = models.ForeignKey(Url, on_delete=models.CASCADE, related_name="usages")
    seen = models.IntegerField(null=True, blank=True)
    updated_at = None

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
