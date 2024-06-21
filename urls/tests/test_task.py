from django.conf import settings
from django.test import TestCase

from urls.models import Url
from urls.tasks import create_ready_to_set_token_periodically


class TestUrlTask(TestCase):
    def tearDown(self):
        Url.objects.filter(pk__gte=1).delete()

    def test_create_ready_to_set_token_start_with_zero_ready_to_set_token(self):
        create_ready_to_set_token_periodically()
        self.assertEqual(Url.objects.all_ready_to_set_token().count(), settings.URL_SHORTENER_READY_TO_SET_TOKEN_LIMIT)

    def test_create_ready_to_set_token_start_with_one_ready_to_set_token(self):
        Url.objects.create_ready_to_set_token()
        self.assertEquals(Url.objects.all_ready_to_set_token().count(), 1)

        create_ready_to_set_token_periodically()
        self.assertEqual(Url.objects.all_ready_to_set_token().count(), settings.URL_SHORTENER_READY_TO_SET_TOKEN_LIMIT)

    def test_create_ready_to_set_token_start_with_limit_exceeded(self):
        for _ in range(settings.URL_SHORTENER_READY_TO_SET_TOKEN_LIMIT):
            Url.objects.create_ready_to_set_token()

        create_ready_to_set_token_periodically()
        self.assertEqual(Url.objects.all_ready_to_set_token().count(), settings.URL_SHORTENER_READY_TO_SET_TOKEN_LIMIT)
