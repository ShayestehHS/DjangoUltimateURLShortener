from django.contrib import admin
from django.db import models

from urls.models import Url

from flat_json_widget.widgets import FlatJsonWidget


@admin.register(Url)
class UrlAdmin(admin.ModelAdmin):
    fields = ("url", "short_url", "created_at", "expiration_date")
    readonly_fields = ("short_url", "created_at",)
    list_display = ("__str__", "token", "created_at", "is_active")
    formfield_overrides = {
        models.JSONField: {'widget': FlatJsonWidget}
    }
    ordering = ("-updated_at", )
    search_fields = ("token", "url")

    def is_active(self, obj):
        return obj.is_active

    is_active.short_description = 'Is Active'
    is_active.boolean = True
