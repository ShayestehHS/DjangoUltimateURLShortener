from django.urls import path, include
from urls.api import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r"user", views.UserView, basename="user")

router.register(r"redirect", views.RedirectAPIView, basename="redirect")


app_name = "urls"

urlpatterns = [
    # path("<str:token>/", views.RedirectAPIView.as_view(), name="redirect"),
    path("", include(router.urls)),
]
