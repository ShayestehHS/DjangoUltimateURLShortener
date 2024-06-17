from django.contrib import admin
from django.db import models

from urls.models import Url, UrlUser

from flat_json_widget.widgets import FlatJsonWidget


class UrlUserInline(admin.TabularInline):
    model = UrlUser
    extra = 1
    autocomplete_fields = ["user"]


@admin.register(Url)
class UrlAdmin(admin.ModelAdmin):
    fields = ("url", "short_url", "created_at", "expiration_date", "query_params")
    readonly_fields = ("short_url", "created_at",)
    list_display = ("__str__", "token", "created_at", "is_expired")
    formfield_overrides = {
        models.JSONField: {'widget': FlatJsonWidget}
    }
    inlines = [UrlUserInline]
    ordering = ("-updated_at", )

    def is_expired(self, obj):
        return obj.is_expired

    is_expired.short_description = 'Is Expired'
    is_expired.boolean = True
