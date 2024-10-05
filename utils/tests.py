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
