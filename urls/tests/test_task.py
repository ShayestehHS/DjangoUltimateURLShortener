from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.utils.timezone import now
from rest_framework import status
from rest_framework.reverse import reverse
from django.test.utils import override_settings

from urls.models import Url, UrlUsage
from urls.tasks import create_ready_to_set_token_periodically, log_the_url_usages


def get_redirect_url(token):
    return reverse("urls:redirect", kwargs={"token": token})


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


class TestUrlUsageTask(TestCase):
    def tearDown(self):
        Url.objects.filter(pk__gt=0).delete()

    @patch("urls.tasks.log_the_url_usages.delay")
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_create_url_usage_obj_on_view_of_url(self, mock_log_the_url_usages):
        url = Url.objects.create(url="https://example.com")

        with self.assertNumQueries(1):
            res = self.client.get(get_redirect_url(url.token))
            self.assertEqual(res.status_code, status.HTTP_302_FOUND, res)

        mock_log_the_url_usages.assert_called_once()
        log_the_url_usages(url.id, now().strftime("%Y-%m-%d %H:%M:%S %z"))
        self.assertEqual(UrlUsage.objects.filter(url=url).count(), 1)
