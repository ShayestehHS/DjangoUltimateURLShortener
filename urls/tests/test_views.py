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

    @patch("urls.api.views.RedirectAPIView.log_the_url_usages")
    @patch("urls.api.views.cache.get")
    @patch("urls.api.views.cache.set")
    @override_settings(URL_SHORTENER_USE_CACHE=True)
    def test_redirect_view_with_valid_token_redirect_to_correct_url(self, mock_cache_set, mock_cache_get, mock_log_the_url_usages):
        url = Url.objects.create(url="https://example.com")
        mock_cache_get.return_value = None

        with self.assertNumQueries(1):
            response = self.client.get(get_redirect_url(url.token))
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.assertEqual(response["location"], url.url)

        mock_log_the_url_usages.assert_called_once()
        mock_cache_get.assert_called_once()
        mock_cache_set.assert_called_once()

    @patch("urls.api.views.RedirectAPIView.log_the_url_usages")
    @patch("urls.api.views.cache.get")
    @patch("urls.api.views.cache.set")
    @override_settings(URL_SHORTENER_USE_CACHE=True)
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_redirect_view_with_valid_cached_key_redirect_to_correct_url(self, mock_cache_set, mock_cache_get, mock_log_the_url_usages):
        url_obj = Url.objects.create(url="https://example.com")
        mock_cache_get.return_value = {
            "redirect_url": url_obj.url,
            "url_pk": url_obj.pk
        }

        with self.assertNumQueries(0):
            response = self.client.get(get_redirect_url(url_obj.token))
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.assertEqual(response["location"], url_obj.url)

        mock_log_the_url_usages.assert_called_once()
        mock_cache_get.assert_called_once()
        mock_cache_set.assert_not_called()

    @patch("urls.api.views.RedirectAPIView.log_the_url_usages")
    @patch("urls.api.views.RedirectAPIView.get_object")
    @patch("urls.api.views.cache.get")
    @patch("urls.api.views.cache.set")
    @override_settings(URL_SHORTENER_USE_CACHE=True)
    def test_redirect_view_is_cache_the_token_with_correct_key_value_ttl(self, mock_cache_set, mock_cache_get, mock_get_object, mock_log_the_url_usages):
        token = Url.create_token()
        url_obj = Url(pk=0, token=token, url="https://example.com")
        url_obj.remaining_seconds = 12
        mock_get_object.return_value = url_obj
        mock_cache_get.return_value = None

        with self.assertNumQueries(0):
            response = self.client.get(get_redirect_url(token))
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.assertEqual(response["location"], url_obj.url)

        cache_value = {
            "redirect_url": url_obj.url,
            "url_pk": url_obj.pk
        }
        mock_cache_get.assert_called_once_with(token)
        mock_cache_set.assert_called_once_with(token, cache_value, url_obj.remaining_seconds)

    @patch("urls.api.views.cache.get")
    @patch("urls.api.views.cache.set")
    @override_settings(URL_SHORTENER_USE_CACHE=True)
    def test_redirect_view_with_expired_token_redirect_to_404_page(self, mock_cache_set, mock_cache_get):
        url = Url.objects.create(url="https://example.com", expiration_date=now() - timedelta(days=1))
        mock_cache_get.return_value = None

        with self.assertNumQueries(1):
            response = self.client.get(get_redirect_url(url.token))
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.assertEqual(response["location"], settings.URL_SHORTENER_404_PAGE)

        mock_cache_get.assert_called_once()
        mock_cache_set.assert_not_called()

    @patch("urls.api.views.cache.get")
    @patch("urls.api.views.cache.set")
    @override_settings(URL_SHORTENER_USE_CACHE=True)
    def test_redirect_view_with_ready_to_set_token_redirect_to_404_page(self, mock_cache_set, mock_cache_get):
        url = Url.objects.create_ready_to_set_token()
        mock_cache_get.return_value = None

        with self.assertNumQueries(1):
            response = self.client.get(get_redirect_url(url.token))
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.assertEqual(response["location"], settings.URL_SHORTENER_404_PAGE)

        mock_cache_get.assert_called_once()
        mock_cache_set.assert_not_called()

    @patch("urls.api.views.cache.get")
    @patch("urls.api.views.cache.set")
    @override_settings(URL_SHORTENER_USE_CACHE=True)
    def test_redirect_view_with_long_token_redirect_to_404_page(self, mock_cache_set, mock_cache_get):
        token = "".join([choice(AVAILABLE_CHARS) for _ in range(settings.URL_SHORTENER_MAXIMUM_TOKEN_LENGTH + 1)])

        with self.assertNumQueries(0):
            response = self.client.get(get_redirect_url(token))
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.assertEqual(response["location"], settings.URL_SHORTENER_404_PAGE)

        mock_cache_get.assert_not_called()
        mock_cache_set.assert_not_called()

    @patch("urls.api.views.cache.get")
    @patch("urls.api.views.cache.set")
    @override_settings(URL_SHORTENER_USE_CACHE=True)
    def test_redirect_view_with_invalid_token_redirect_to_404_page(self, mock_cache_set, mock_cache_get):
        token = "".join([choice(AVAILABLE_CHARS) for _ in range(settings.URL_SHORTENER_MAXIMUM_TOKEN_LENGTH)])
        mock_cache_get.return_value = None

        with self.assertNumQueries(1):
            response = self.client.get(get_redirect_url(token))
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.assertEqual(response["location"], settings.URL_SHORTENER_404_PAGE)

        mock_cache_get.assert_called_once()
        mock_cache_set.assert_not_called()

    @patch("urls.api.views.cache.get")
    @patch("urls.api.views.cache.set")
    @override_settings(URL_SHORTENER_USE_CACHE=True)
    def test_redirect_view_with_short_token_redirect_to_404_page(self, mock_cache_set, mock_cache_get):
        token = "".join([choice(AVAILABLE_CHARS) for _ in range(settings.URL_SHORTENER_MAXIMUM_TOKEN_LENGTH - 1)])

        with self.assertNumQueries(0):
            url = get_redirect_url(token)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.assertEqual(response["location"], settings.URL_SHORTENER_404_PAGE)

        mock_cache_get.assert_not_called()
        mock_cache_set.assert_not_called()
