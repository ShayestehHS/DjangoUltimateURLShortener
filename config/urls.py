from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('u/admin/', admin.site.urls),
    path('u/', include("urls.api.urls")),
]
