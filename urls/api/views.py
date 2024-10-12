from typing import Any
from django.conf import settings
from django.core.cache import cache
from django.db.models import F, ExpressionWrapper, DurationField
from django.db.models.functions import Now
from django.http import HttpRequest, HttpResponseRedirect
from django.utils.timezone import now
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from urls.models import READY_TO_SET_TOKEN_URL
from urls.models import Url
from rest_framework import status
from rest_framework.response import Response
from urls.tasks import log_the_url_usages

USE_CELERY_AS_USAGE_LOGGER = settings.URL_SHORTENER_USE_CELERY_AS_USAGE_LOGGER
MAXIMUM_TOKEN_LENGTH = settings.URL_SHORTENER_MAXIMUM_TOKEN_LENGTH


class RedirectAPIView(APIView):
    authorization_classes = []

    def get(self, *args, **kwargs):
        token = self.kwargs["token"]
        if len(token) != MAXIMUM_TOKEN_LENGTH:
            return HttpResponseRedirect(redirect_to=settings.URL_SHORTENER_404_PAGE)

        if settings.URL_SHORTENER_USE_CACHE and (cached_value := cache.get(token)):
            redirect_url = cached_value["redirect_url"]
            url_pk = cached_value["url_pk"]
        else:
            url_obj = self.get_object(token)
            if not url_obj:
                return HttpResponseRedirect(redirect_to=settings.URL_SHORTENER_404_PAGE)

            redirect_url = url_obj.url
            url_pk = url_obj.pk
            if settings.URL_SHORTENER_USE_CACHE:
                data = {"redirect_url": redirect_url, "url_pk": url_pk}
                cache.set(token, data, url_obj.remaining_seconds)

        self.log_the_url_usages(url_pk)
        return HttpResponseRedirect(redirect_to=redirect_url)

    def log_the_url_usages(self, url_pk):
        usage_log_args = (url_pk, now().strftime("%Y-%m-%d %H:%M:%S %z"))
        if USE_CELERY_AS_USAGE_LOGGER:
            log_the_url_usages.delay(*usage_log_args)
        else:
            log_the_url_usages(*usage_log_args)

    def get_object(self, token):
        queryset = (
            Url.objects.filter(token=token)
            .exclude_ready_to_set_urls()
            .all_actives()
            .only("url")
            .order_by()
        )
        if settings.URL_SHORTENER_USE_CACHE:
            queryset = queryset.annotate(
                remaining_seconds=ExpressionWrapper(
                    F("expiration_date") - Now(),
                    output_field=DurationField(),
                )
            )
        return queryset.first()


class ReturnAvailableToken(APIView):

    def get(self, *args, **kwargs):
        attempts = 0
        max_attempts = 10
        available_tokens = list(
            Url.objects.all_actives().values_list("token", flat=True)[:4]
        )
        while len(available_tokens) < 4 and attempts < max_attempts:
            new_url = Url.objects.create_ready_to_set_token()
            available_tokens.append(new_url.token)
            attempts += 1

        return Response(list(available_tokens), status=status.HTTP_200_OK)
