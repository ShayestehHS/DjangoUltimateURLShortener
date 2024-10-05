from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.test import TestCase
from urls.api.views import ReturnAvailableToken
from urls.models import Url
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APIClient
from unittest import mock
from django.urls import reverse
from django.test import override_settings
from django.conf import settings

READY_TO_SET_TOKEN_URL = settings.URL_SHORTENER_READY_TO_SET_TOKEN_URL


class CustomTestCase(TestCase):
    def assertMinimumNumQueries(self, min_queries):
        """
        Assert that at least `min_queries` queries are executed within the context.
        """
        return _AssertMinimumNumQueries(self, min_queries)

    def assertMaximumNumQueries(self, max_queries):
        """
        Assert that at most `max_queries` queries are executed within the context.
        """
        return _AssertMaximumNumQueries(self, max_queries)

    def assertQueryCountRange(self, min_queries, max_queries):
        """
        Assert that the number of queries executed is within a given range.
        """
        return _AssertQueryCountRange(self, min_queries, max_queries)


class _AssertMinimumNumQueries:
    def __init__(self, test_case, min_queries):
        self.test_case = test_case
        self.min_queries = min_queries

    def __enter__(self):
        self.context = CaptureQueriesContext(connection)
        self.context.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        executed_queries = len(self.context)
        self.context.__exit__(exc_type, exc_value, traceback)
        self.test_case.assertGreaterEqual(
            executed_queries,
            self.min_queries,
            "%d queries executed, at least %d expected\nCaptured queries were:\n%s"
            % (
                executed_queries,
                self.min_queries,
                "\n".join(
                    "%d. %s" % (i, query["sql"])
                    for i, query in enumerate(self.context.captured_queries, start=1)
                ),
            ),
        )


class _AssertMaximumNumQueries:
    def __init__(self, test_case, max_queries):
        self.test_case = test_case
        self.max_queries = max_queries

    def __enter__(self):
        self.context = CaptureQueriesContext(connection)
        self.context.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        executed_queries = len(self.context)
        self.context.__exit__(exc_type, exc_value, traceback)
        self.test_case.assertLessEqual(
            executed_queries,
            self.max_queries,
            "%d queries executed, at most %d expected\nCaptured queries were:\n%s"
            % (
                executed_queries,
                self.max_queries,
                "\n".join(
                    "%d. %s" % (i, query["sql"])
                    for i, query in enumerate(self.context.captured_queries, start=1)
                ),
            ),
        )


class _AssertQueryCountRange:
    def __init__(self, test_case, min_queries, max_queries):
        self.test_case = test_case
        self.min_queries = min_queries
        self.max_queries = max_queries

    def __enter__(self):
        self.context = CaptureQueriesContext(connection)
        self.context.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        executed_queries = len(self.context)
        self.context.__exit__(exc_type, exc_value, traceback)
        self.test_case.assertGreaterEqual(
            executed_queries,
            self.min_queries,
            "%d queries executed, at least %d expected\nCaptured queries were:\n%s"
            % (
                executed_queries,
                self.min_queries,
                "\n".join(
                    "%d. %s" % (i, query["sql"])
                    for i, query in enumerate(self.context.captured_queries, start=1)
                ),
            ),
        )
        self.test_case.assertLessEqual(
            executed_queries,
            self.max_queries,
            "%d queries executed, at most %d expected\nCaptured queries were:\n%s"
            % (
                executed_queries,
                self.max_queries,
                "\n".join(
                    "%d. %s" % (i, query["sql"])
                    for i, query in enumerate(self.context.captured_queries, start=1)
                ),
            ),
        )


class TestReReturnAvailableTokenturn(CustomTestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        Url.objects.create(url=READY_TO_SET_TOKEN_URL, token="token1")
        Url.objects.create(Url=READY_TO_SET_TOKEN_URL, token="token2")

    @mock.patch("urls.api.views.Url.create_token")
    def test_available_tokens_insufficient(self, create_token_mock):
        create_token_mock.side_effect = ["token3", "token4"]
        with self.assertQueryCountRange(3, 5):
            response = self.client.get(reverse("availabletoken"))
            self.assertEqual(create_token_mock.call_count, 2)
            self.assertIn("available_tokens", response.data)
            self.assertEqual(len(response.data["available_tokens"]), 4)
            self.assertListEqual(
                response.data["available_tokens"],
                ["token1", "token2", "token3", "token4"],
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(create_token_mock.call_count, 2)

    @mock.patch("urls.api.views.Url.create_token")
    def test_available_tokens_insufficient_no_creation(self, create_token_mock):
        Url.objects.create(url=READY_TO_SET_TOKEN_URL, token="token3")
        Url.objects.create(url=READY_TO_SET_TOKEN_URL, token="token4")
        with self.assertQueryCountRange(1, 2):
            response = self.client.get(reverse("availabletoken"))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data["available_token"]), 4)
            self.assertIn("available_tokens", response.data)
            self.assertListEqual(
                response.data["available_tokens"],
                ["token1", "token2", "token3", "token4"],
            )
            create_token_mock.assert_not_called()

    @mock.patch("urls.api.views.Url.create_token")
    def test_create_token_validation_error(self, create_token_mock):
        create_token_mock.side_effect = ValidationError("Invalid token")
        with self.assertQueryCountRange(1, 2):
            response = self.client.get(reverse("availabletoken"))
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("error", response.data)
            self.assertEqual(response.data["error"], "Invalid token")
            create_token_mock.assert_called_once()

    @mock.patch("urls.api.views.Url.create_token")
    def test_create_token_general_exception(self, create_token_mok):
        create_token_mok.side_effect = Exception("Unexpected error")
        with self.assertQueryCountRange(1, 2):
            response = self.client.get(reverse("availabletoken"))
            self.assertIn("error", response.data)
            self.assertEqual(response.data["error"], "failed to generate new token")
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            create_token_mok.assert_called_once()

    @mock.patch("urls.api.views.Url.create_token")
    def test_return_only_four_tokens(self, create_token_moke):
        create_token_moke.side_effect = ["token3", "token4", "token5"]
        with self.assertQueryCountRange(1, 2):
            response = self.client.get(reverse("availabletoken"))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("available_tokens", response.data)
            self.assertEqual(len(response.data["available_tokens"]), 4)
            self.assertListEqual(
                response.data["available_tokens"],
                ["token1", "token2", "token3", "token4"],
            )
            self.assertEqual(create_token_moke.call_count, 2)
