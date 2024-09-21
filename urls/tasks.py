from datetime import datetime
from .models import Url
from celery import shared_task
from django.conf import settings
import uuid
from urls.models import Url, UrlUsage


@shared_task
def create_ready_to_set_token_periodically():
    ready_to_set_token_count = Url.objects.all_ready_to_set_token().count()
    limit = settings.URL_SHORTENER_READY_TO_SET_TOKEN_LIMIT
    if ready_to_set_token_count < limit:
        for _ in range(limit - ready_to_set_token_count):
            # ToDo: Use bulk_create
            Url.objects.create_ready_to_set_token()


@shared_task
def generate_token(url_id):
    generated_token = settings.URL_SHORTENER_BASE_URL + uuid.uuid4().hex
    url = Url.objects.get(pk=url_id)
    url.token = generated_token
    url.save()


@shared_task()
def log_the_url_usages(url_id, created_at):
    # ToDo: Use bulk create instead
    UrlUsage.objects.create(
        url_id=url_id,
        created_at=datetime.strptime(
            created_at,
            "%Y-%m-%d %H:%M:%S %z",
        ),
    )


@shared_task()
def delete_short_url(short_url):
    pass


@shared_task()
def delete_short_irl_with_long(long_url):
    pass
