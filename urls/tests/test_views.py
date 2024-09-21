from datetime import timedelta
from random import choice
from unittest.mock import patch

from django.conf import settings
from django.test.utils import override_settings
from django.utils.timezone import now
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from urls.models import Url, AVAILABLE_CHARS


def get_redirect_url(token):
    return reverse("urls:redirect", kwargs={"token": token})


class TestRedirectUrlView(APITestCase):
    def setUp(self) -> None:
        Url.objects.filter(pk__gte=1).delete()

    @patch("urls.tasks.log_the_url_usages.delay")
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_redirect_view_with_valid_token_redirect_to_correct_url(self, mock_log_the_url_usages):
        url = Url.objects.create(url="https://example.com")

        with self.assertNumQueries(1):
            response = self.client.get(get_redirect_url(url.token))
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.assertEqual(response["location"], url.url)

        mock_log_the_url_usages.assert_called_once()

    def test_redirect_view_with_expired_token_redirect_to_404_page(self):
        url = Url.objects.create(url="https://example.com", expiration_date=now() - timedelta(days=1))

        with self.assertNumQueries(1):
            response = self.client.get(get_redirect_url(url.token))
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.assertEqual(response["location"], settings.URL_SHORTENER_404_PAGE)

    def test_redirect_view_with_ready_to_set_token_redirect_to_404_page(self):
        url = Url.objects.create_ready_to_set_token()

        with self.assertNumQueries(1):
            response = self.client.get(get_redirect_url(url.token))
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.assertEqual(response["location"], settings.URL_SHORTENER_404_PAGE)

    def test_redirect_view_with_long_token_redirect_to_404_page(self):
        token = "".join([choice(AVAILABLE_CHARS) for _ in range(settings.URL_SHORTENER_MAXIMUM_TOKEN_LENGTH + 1)])

        with self.assertNumQueries(0):
            response = self.client.get(get_redirect_url(token))
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.assertEqual(response["location"], settings.URL_SHORTENER_404_PAGE)

    def test_redirect_view_with_invalid_token_redirect_to_404_page(self):
        token = "".join([choice(AVAILABLE_CHARS) for _ in range(settings.URL_SHORTENER_MAXIMUM_TOKEN_LENGTH)])

        with self.assertNumQueries(1):
            response = self.client.get(get_redirect_url(token))
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.assertEqual(response["location"], settings.URL_SHORTENER_404_PAGE)

    def test_redirect_view_with_short_token_redirect_to_404_page(self):
        token = "".join([choice(AVAILABLE_CHARS) for _ in range(settings.URL_SHORTENER_MAXIMUM_TOKEN_LENGTH - 1)])

        with self.assertNumQueries(0):
            url = get_redirect_url(token)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.assertEqual(response["location"], settings.URL_SHORTENER_404_PAGE)
