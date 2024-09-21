from django.conf import settings
from django.core.cache import cache
from django.db.models import F, ExpressionWrapper, DurationField
from django.db.models.functions import Now
from django.http import HttpResponseRedirect
from django.utils.timezone import now
from rest_framework.views import APIView

from urls.models import Url
from urls.tasks import log_the_url_usages

MAXIMUM_TOKEN_LENGTH = settings.URL_SHORTENER_MAXIMUM_TOKEN_LENGTH
URL_PK_SEPERATOR = settings.URL_SHORTENER_URL_PK_SEPERATOR


class RedirectAPIView(APIView):
    authorization_classes = []

    def get(self, *args, **kwargs):
        token = self.kwargs["token"]
        if len(token) != MAXIMUM_TOKEN_LENGTH:
            return HttpResponseRedirect(redirect_to=settings.URL_SHORTENER_404_PAGE)

        if cached_value := cache.get(token):
            split_list = cached_value.split(URL_PK_SEPERATOR)
            redirect_url = split_list[0]
            url_pk = split_list[-1]
        else:
            url_obj = self.get_object(token)
            if not url_obj:
                return HttpResponseRedirect(redirect_to=settings.URL_SHORTENER_404_PAGE)

            redirect_url = url_obj.url
            url_pk = url_obj.pk
            cache.set(token, f"{redirect_url}{URL_PK_SEPERATOR}{url_pk}", url_obj.remaining_seconds)

        self.log_the_url_usages(url_pk)
        return HttpResponseRedirect(redirect_to=redirect_url)

    def log_the_url_usages(self, url_pk):
        log_the_url_usages.delay(url_pk, now().strftime("%Y-%m-%d %H:%M:%S %z'"))

    def get_object(self, token):
        return (
            Url.objects
            .filter(token=token)
            .exclude_ready_to_set_urls()
            .all_actives()
            .annotate(
                remaining_seconds=ExpressionWrapper(
                    F('expiration_date') - Now(),
                    output_field=DurationField(),
                )
            )
            .only("url")
            .order_by()
            .first()
        )
