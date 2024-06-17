from django.http import HttpResponseRedirect
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView

from urls.models import Url


class RedirectAPIView(APIView):
    authorization_classes = []

    def get(self, *args, **kwargs):
        url_obj = get_object_or_404(Url.objects.all_actives().only("url"), token=self.kwargs["token"])
        return HttpResponseRedirect(redirect_to=url_obj.url)
