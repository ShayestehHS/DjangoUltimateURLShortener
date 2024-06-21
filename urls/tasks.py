from celery import shared_task
from django.conf import settings

from urls.models import Url


@shared_task
def create_ready_to_set_token_periodically():
    ready_to_set_token_count = Url.objects.all_ready_to_set_token().count()
    limit = settings.URL_SHORTENER_READY_TO_SET_TOKEN_LIMIT
    if ready_to_set_token_count < limit:
        for _ in range(limit - ready_to_set_token_count):
            # ToDo: Use bulk_create
            Url.objects.create_ready_to_set_token()
