from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from urls.models import Url, UrlUsage


class UrlAdminForm(ModelForm):
    class Meta:
        model = Url
        fields = ("url", "token", "expiration_date")

    def clean_token(self):
        token = self.cleaned_data["token"]
        if (Url.objects
                .all_actives()
                .exclude_ready_to_set_urls()
                .filter(token=token)
                .exists()):
            raise ValidationError("This token is active.")

    def clean_url(self):
        url = self.cleaned_data["url"]
        if url.startswith("http://"):
            raise ValidationError("You can not use insecure URL.")
        if url == settings.URL_SHORTENER_READY_TO_SET_TOKEN_URL:
            raise ValidationError("You can not use this url because it is a reserved url.")


@admin.register(Url)
class UrlAdmin(admin.ModelAdmin):
    form = UrlAdminForm
    list_display = ("__str__", "token", "created_at", "is_active")
    ordering = ("-updated_at",)
    search_fields = ("token", "url")
    search_help_text = "Search by 'URL' or 'Token' to quickly find specific records."

    def is_active(self, obj):
        return obj.is_active

    is_active.short_description = 'Is Active'
    is_active.boolean = True

    def has_change_permission(self, request, obj=None):
        if obj:
            return False
        return True

    def save_model(self, request, obj, form, change):
        Url.objects.create(**form.cleaned_data)


@admin.register(UrlUsage)
class UrlUsageAdmin(admin.ModelAdmin):
    list_display = ("id", "url", "get_token", "created_at", )
    ordering = ("-id", )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("url")

    def get_token(self, obj: UrlUsage):
        return obj.url.token
    get_token.short_description = 'Token'

