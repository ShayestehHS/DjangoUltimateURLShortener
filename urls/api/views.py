from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.timezone import now
from rest_framework.exceptions import NotFound
from rest_framework import viewsets
from rest_framework.decorators import action

from urls.models import Url
from urls.tasks import log_the_url_usages
from rest_framework.response import Response


class RedirectAPIView(viewsets.ViewSet):
    authorization_classes = []

    @action(detail=True, methods=["get"])
    def get_data(self, request, *args, **kwargs):
        token = self.kwargs.get("pk")
        if len(token) != settings.URL_SHORTENER_MAXIMUM_URL_CHARS:
            raise NotFound({"token": "Given token not found."})

        url_obj = Url.objects.all_actives().filter(token=token).only("url").first()
        if not url_obj:
            return HttpResponseRedirect(redirect_to=settings.URL_SHORTENER_404_PAGE)

        log_the_url_usages.delay(url_obj.pk, now().strftime("%Y-%m-%d %H:%M:%S %z'"))
        return HttpResponseRedirect(redirect_to=url_obj.url)
