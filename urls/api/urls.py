from django.urls import path
from urls.api import views

app_name = "urls"

urlpatterns = [
    path("<str:token>/", views.RedirectAPIView.as_view(), name="redirect"),
    path(
        "availabletoken/", views.ReturnAvailableToken.as_view(), name="availabletoken"
    ),
]
