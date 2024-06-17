from datetime import timedelta

from django.conf import settings
from django.test import TestCase
from django.utils.timezone import now
from rest_framework import status
from rest_framework.reverse import reverse

from urls.models import Url

def get_redirect_url(token):
    return reverse("urls:redirect", kwargs={"token": token})


class TestRedirectUrlView(TestCase):
    def setUp(self) -> None:
        Url.objects.filter(pk__gte=1).delete()

    def test_redirect_with_valid_token(self):
        url = Url.objects.create(url="https://example.com")

        with self.assertNumQueries(1):
            response = self.client.get(get_redirect_url(url.token))
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.assertEqual(response["location"], url.url)

    def test_redirect_with_invalid_token(self):
        with self.assertNumQueries(1):
            response = self.client.get(get_redirect_url("abcdf"))
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.assertEqual(response["location"], settings.URL_SHORTENER_404_PAGE)

    def test_redirect_with_expired_token(self):
        url = Url.objects.create(url="https://example.com", expiration_date=now() - timedelta(days=1))

        with self.assertNumQueries(1):
            response = self.client.get(get_redirect_url(url.token))
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.assertEqual(response["location"], settings.URL_SHORTENER_404_PAGE)

    def test_redirect_with_ready_to_set_token(self):
        url = Url.objects.create_ready_to_set_token()

        with self.assertNumQueries(1):
            response = self.client.get(get_redirect_url(url.token))
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.assertEqual(response["location"], settings.URL_SHORTENER_404_PAGE)
