from datetime import timedelta
from unittest.mock import patch

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from utils.tests import CustomTestCase
from urls.models import URL
from string import ascii_letters, digits

AVAILABLE_CHARS = ascii_letters + digits


class TestUrlModel(CustomTestCase):
    def test_create_two_url_with_none_name_success(self):
        URL.objects.create(url="https://google.com")
        URL.objects.create(url="https://google.com")

    def test_create_url_with_duplicate_name_raise_exception(self):
        URL.objects.create(name='test', url="https://google.com")
        with self.assertNumQueries(3):
            with self.assertRaisesMessage(ValidationError, expected_message="Url with this Name already exists."):
                URL.objects.create(name='test', url="https://google.com")

    def test_create_url_with_same_token_and_not_expired_raise_maximum_recursion(self):
        url = URL.objects.create(url='https://example.com', expiration_date=now() + timedelta(days=1))

        with patch("urls.models.URL._create_random_string", return_value=url.token):
            with self.assertNumQueries(6):
                with self.assertRaisesMessage(Exception, "Maximum recursion depth occurred."):
                    """
                        Get the read_to_set_token_obj
                        Validate token is valid * 5
                    """
                    URL.objects.create(url='https://example2.com')

    def test_create_url_with_same_token_and_expired_date_success(self):
        url = URL.objects.create(url='https://example.com', expiration_date=now() - timedelta(days=1))

        with patch("urls.models.URL._create_random_string", return_value=url.token):
            with self.assertNumQueries(3):
                """
                    1- Check ready_token_to_set object is exists
                    2- Check expiration_date of created token[duplicate]
                    3- Create Url object
                """
                URL.objects.create(url='https://example2.com')

    def test_create_url_that_start_with_http_raise_validation_error(self):
        with self.assertRaisesMessage(ValidationError, "The URL should start with https://"):
            with self.assertNumQueries(0):
                URL.objects.create(url='http://example.com')

    def test_create_url_object_success(self):
        with self.assertNumQueries(3):
            """
                1- Check ready_token_to_set object is exists
                2- Check expiration_date of created token
                3- Create Url object
            """
            url = URL.objects.create(url='https://example.com')

        self.assertEqual(url.url, 'https://example.com')
        self.assertNotEqual(url.url, settings.URL_SHORTENER_READY_TO_SET_TOKEN_URL)
        self.assertEqual(len(url.token), settings.URL_SHORTENER_MAXIMUM_TOKEN_LENGTH)
        self.assertEqual(url.created_at.date(), now().date())
        self.assertEqual(url.expiration_date.day, (now() + timedelta(days=getattr(settings, "URL_SHORTENER_DEFAULT_EXPIRATION_DAYS"))).day)
        self.assertEqual(URL.objects.all().count(), 1)
        self.assertEqual(URL.objects.all_actives().count(), 1)
        self.assertEqual(URL.objects.all_ready_to_set_token().count(), 0)

    def test_create_ready_to_set_url_object_with_manger_success(self):
        with self.assertNumQueries(2):
            """
                1- Check expiration_date of created token
                2- Create ready_to_set_token_object Url
            """
            url = URL.objects.create_ready_to_set_token()

        self.assertEqual(url.url, getattr(settings, "URL_SHORTENER_READY_TO_SET_TOKEN_URL"))
        self.assertIsNotNone(url.token)
        self.assertEqual(url.created_at.date(), now().date())
        self.assertEqual(url.expiration_date.day, (now() + timedelta(days=getattr(settings, "URL_SHORTENER_DEFAULT_EXPIRATION_DAYS"))).day)

        self.assertTrue(URL.objects.all_actives().filter(id=url.id).exists())
        self.assertTrue(URL.objects.all_ready_to_set_token().filter(id=url.id).exists())
        self.assertNotIn(url, URL.objects.exclude_ready_to_set_urls().all())

    def test_create_url_with_existent_ready_to_set_token_success(self):
        ready_to_set_url_obj: URL = URL.objects.create_ready_to_set_token()
        ready_to_set_url_obj.created_at = now() - timedelta(days=3)
        ready_to_set_url_obj.save()

        before_token = ready_to_set_url_obj.token
        with self.assertNumQueries(2):
            """
                Get the read_to_set_token_obj
                Update the url of selected obj
            """
            URL.objects.create(url='https://example.com', expiration_date=now() + timedelta(days=4))
        ready_to_set_url_obj.refresh_from_db()
        self.assertEquals(ready_to_set_url_obj.url, 'https://example.com')
        self.assertEquals(before_token, ready_to_set_url_obj.token)
        self.assertEquals(ready_to_set_url_obj.created_at.day, now().day)
        self.assertEquals(ready_to_set_url_obj.expiration_date.day, (now() + timedelta(days=4)).day)

    def test_create_url_with_non_existent_ready_to_set_token_success(self):
        URL.objects.all_ready_to_set_token().delete()
        with self.assertMinimumNumQueries(3):
            """
                Get the read_to_set_token_obj
                Validate token is valid * n
                Create the url object
            """
            URL.objects.create(url='https://example.com')

    def test_create_url_object_with_ready_to_set_token_url_address_raise_validation_error(self):
        with self.assertRaisesMessage(ValidationError, "You can not use ready_to_set_token_url"):
            URL.objects.create(url=settings.URL_SHORTENER_READY_TO_SET_TOKEN_URL)

    def test_create_url_object_with_suggested_token_success(self):
        token = URL.create_token()

        with self.assertNumQueries(2):
            URL.objects.create(url='https://example.com', token=token)

        self.assertTrue(URL.objects.all_actives().filter(token=token).exists())

    def test_create_url_object_with_suggested_token_but_active_token_as_input_raise_validation_error(self):
        active_url = URL.objects.create(url='https://example.com')

        with self.assertNumQueries(1):
            with self.assertRaisesMessage(ValidationError, "This token is already active."):
                URL.objects.create("https://example2.com", token=active_url.token)

    def test_create_url_object_with_suggested_token_but_expired_token_success(self):
        expired_url = URL.objects.create(url='https://example.com', expiration_date=now() - timedelta(days=3))
        self.assertFalse(URL.objects.all_actives().filter(id=expired_url.id).exists())

        with self.assertNumQueries(2):
            url = URL.objects.create("https://example.com", token=expired_url.token)

        self.assertTrue(URL.objects.all_actives().filter(token=url.token).exists())

    def test_create_url_object_with_suggested_token_but_with_ready_to_set_token_fail(self):
        ready_to_set_token_url_object = URL.objects.create_ready_to_set_token()

        with self.assertNumQueries(1):
            with self.assertRaisesMessage(ValidationError, "This token is already active."):
                URL.objects.create("https://example.com", token=ready_to_set_token_url_object.token)

    def test_create_url_object_with_expired_token_but_not_case_sensitive_match_success(self):
        test_code = "aBcDe"
        with patch("urls.models.URL._create_random_string", return_value=test_code.lower()):
            URL.objects.create(url='https://example.com', expiration_date=now() + timedelta(days=3))

        with patch("urls.models.URL._create_random_string", return_value=test_code.upper()):
            with self.assertNumQueries(3):
                """
                    1- Check for ready_to_set_token URL -> should fail
                    2- Create random token and check is valid or not
                    3- Insert created token to the DB
                """
                URL.objects.create(url='https://example2.com', expiration_date=now() + timedelta(days=3))

    def test_get_url_object_with_not_case_equality_fail(self):
        test_code = "aBcDe"
        with patch("urls.models.URL._create_random_string", return_value=test_code.lower()):
            URL.objects.create(url='https://example.com', expiration_date=now() + timedelta(days=3))

        with self.assertRaises(URL.DoesNotExist):
            URL.objects.get(token=test_code.upper())

    def test_get_or_create_ready_to_set_token_without_any_ready_to_set_token(self):
        self.assertFalse(URL.objects.all_ready_to_set_token().exists())

        with self.assertNumQueries(3):
            url = URL.objects.get_or_create_ready_to_set_token()

        self.assertEqual(url.url, settings.URL_SHORTENER_READY_TO_SET_TOKEN_URL)
        self.assertTrue(URL.objects.all_actives().filter(token=url.token).exists())
        self.assertTrue(URL.objects.all_ready_to_set_token().filter(token=url.token).exists())

    def test_get_or_create_ready_to_set_token_with_exists_ready_to_set_token(self):
        url = URL.objects.create_ready_to_set_token()
        self.assertTrue(URL.objects.all_ready_to_set_token().count(), 1)

        with self.assertNumQueries(1):
            created_url = URL.objects.get_or_create_ready_to_set_token()

        self.assertEqual(url, created_url)
