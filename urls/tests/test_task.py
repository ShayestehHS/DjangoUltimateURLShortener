from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.utils.timezone import now
from rest_framework import status
from rest_framework.reverse import reverse
from django.test.utils import override_settings

from urls.models import URL, UrlUsage
from urls.tasks import create_ready_to_set_token_periodically, log_the_url_usages


def get_redirect_url(token):
    return reverse("urls:redirect", kwargs={"token": token})


class TestUrlTask(TestCase):
    def tearDown(self):
        URL.objects.filter(pk__gte=1).delete()

    def test_create_ready_to_set_token_start_with_zero_ready_to_set_token(self):
        create_ready_to_set_token_periodically()
        self.assertEqual(URL.objects.all_ready_to_set_token().count(), settings.URL_SHORTENER_READY_TO_SET_TOKEN_LIMIT)

    def test_create_ready_to_set_token_start_with_one_ready_to_set_token(self):
        URL.objects.create_ready_to_set_token()
        self.assertEquals(URL.objects.all_ready_to_set_token().count(), 1)

        create_ready_to_set_token_periodically()
        self.assertEqual(URL.objects.all_ready_to_set_token().count(), settings.URL_SHORTENER_READY_TO_SET_TOKEN_LIMIT)

    def test_create_ready_to_set_token_start_with_limit_exceeded(self):
        for _ in range(settings.URL_SHORTENER_READY_TO_SET_TOKEN_LIMIT):
            URL.objects.create_ready_to_set_token()

        create_ready_to_set_token_periodically()
        self.assertEqual(URL.objects.all_ready_to_set_token().count(), settings.URL_SHORTENER_READY_TO_SET_TOKEN_LIMIT)
