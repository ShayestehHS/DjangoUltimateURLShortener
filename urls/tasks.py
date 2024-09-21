from datetime import datetime
from .models import Url
from celery import shared_task
from django.conf import settings
import uuid
import string
import random
from urls.models import Url, UrlUsage
from rest_framework.response import Response
from rest_framework import status

# @shared_task
# def create_ready_to_set_token_periodically():
#     ready_to_set_token_count = Url.objects.all_ready_to_set_token().count()
#     limit = settings.URL_SHORTENER_READY_TO_SET_TOKEN_LIMIT
#     if ready_to_set_token_count < limit:
#         for _ in range(limit - ready_to_set_token_count):
#             # ToDo: Use bulk_create
#             Url.objects.create_ready_to_set_token()


@shared_task
def generate_token(url_id):
    generated_token = "".join(
        random.choices(
            string.ascii_letters + string.digits, k=settings.URL_SHORTENER_MAXIMUM_URL_CHARS
        )
    )
    url = Url.objects.get(pk=url_id)
    url.token = generated_token
    new_url = settings.URL_SHORTENER_BASE_URL +'?'+'token'+ '=' + url.token
    url.new_url = new_url
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
def delete_short_url(url_id):
    url = Url.objects.get(pk =url_id)
    url.delete()
    

