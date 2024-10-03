from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from django.utils.timezone import now

READY_TO_SET_TOKEN_URL = settings.URL_SHORTENER_READY_TO_SET_TOKEN_URL


class UrlQuerySet(models.QuerySet):
    def all_actives(self):
        return self.filter(expiration_date__gte=now())

    def exclude_ready_to_set_urls(self):
        return self.all().exclude(url=READY_TO_SET_TOKEN_URL)


class UrlManager(models.Manager):
    def get_queryset(self):
        return UrlQuerySet(model=self.model, using=self._db)

    def exclude_ready_to_set_urls(self):
        return self.get_queryset().exclude_ready_to_set_urls()

    def all_actives(self):
        return self.get_queryset().all_actives()

    def create(self, url, **kwargs):
        if url == READY_TO_SET_TOKEN_URL:
            # If you want to create ready_to_set_token_object you have to use create_ready_to_set_token function
            raise ValidationError("You can not use ready_to_set_token_url")

        if suggested_token := kwargs.pop("token", None):
            if (
                self.get_queryset()
                .filter(token=suggested_token)
                .filter(Q(url=READY_TO_SET_TOKEN_URL) | Q(expiration_date__gte=now()))
                .exists()
            ):
                raise ValidationError("This token is already active.")
            return super().create(url=url, token=suggested_token, **kwargs)

        if ready_to_set_token_obj := self.all_ready_to_set_token().first():
            ready_to_set_token_obj.url = url
            ready_to_set_token_obj.expiration_date = kwargs.get("expiration_date", None)
            ready_to_set_token_obj.created_at = now()
            ready_to_set_token_obj.save()
            return ready_to_set_token_obj

        token = self.model.create_token()
        return super().create(url=url, token=token, **kwargs)

    def create_ready_to_set_token(self):
        return super().create(
            url=READY_TO_SET_TOKEN_URL, token=self.model.create_token()
        )

    def all_ready_to_set_token(self):
        return super().all().filter(url=READY_TO_SET_TOKEN_URL).order_by()
