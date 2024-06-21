from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.timezone import now
from rest_framework.views import APIView

from urls.models import Url
from urls.tasks import log_the_url_usages


class RedirectAPIView(APIView):
    authorization_classes = []

    def get(self, *args, **kwargs):
        url_obj = (Url.objects
                   .all_actives()
                   .filter(token=self.kwargs["token"])
                   .only("url")
                   .first())
        if not url_obj:
            return HttpResponseRedirect(redirect_to=settings.URL_SHORTENER_404_PAGE)

        log_the_url_usages.delay(url_obj.pk, now().strftime("%Y-%m-%d %H:%M:%S %z'"))
        return HttpResponseRedirect(redirect_to=url_obj.url)
