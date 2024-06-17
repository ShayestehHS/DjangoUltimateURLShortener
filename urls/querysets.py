from django.conf import settings
from django.db import models
from django.db.models import Q

from datetime import datetime

from django.utils.timezone import now
from pytz import UTC
from rest_framework.exceptions import ValidationError

READY_TO_SET_TOKEN_URL = settings.URL_SHORTENER_READY_TO_SET_TOKEN_URL


class UrlQuerySet(models.QuerySet):
    def all(self):
        return super(UrlQuerySet, self).all().exclude(url=READY_TO_SET_TOKEN_URL)

    def all_actives(self):
        return self.all().filter(expiration_date__gte=datetime.now(UTC))

    def create(self, url, **kwargs):
        if url == READY_TO_SET_TOKEN_URL:
            # If you want to create ready_to_set_token_object you have to use create_ready_to_set_token function
            raise ValidationError({"url": "You can not use ready_to_set_token_url"})

        if kwargs.pop("token", None):
            raise ValidationError({"url": "You can not pass token manually."})

        ready_to_set_token_obj = self.all_ready_to_set_token().first()
        if ready_to_set_token_obj:
            ready_to_set_token_obj.url = url
            ready_to_set_token_obj.expiration_date = kwargs.get('expiration_date', None)
            ready_to_set_token_obj.created_at = now()
            ready_to_set_token_obj.save()
            return ready_to_set_token_obj

        token = self.model.create_token()
        return super().create(url=url, token=token, **kwargs)

    def create_ready_to_set_token(self):
        return super().create(url=READY_TO_SET_TOKEN_URL, token=self.model.create_token())

    def all_ready_to_set_token(self):
        return super().all().filter(url=READY_TO_SET_TOKEN_URL)
