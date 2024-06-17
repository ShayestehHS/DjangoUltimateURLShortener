from django.conf import settings
from django.http import HttpResponseRedirect
from rest_framework.views import APIView

from urls.models import Url


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
        return HttpResponseRedirect(redirect_to=url_obj.url)
