from django.contrib import admin
from .models import UrlUsage,UrlUser
from urls.models import Url


@admin.register(Url)
class UrlAdmin(admin.ModelAdmin):
    fields = ("url", "short_url", "created_at", "expiration_date")
    readonly_fields = ("short_url", "created_at",)
    list_display = ("__str__", "token", "created_at", "is_active")
    ordering = ("-updated_at", )
    search_fields = ("token", "url")
    search_help_text = "Search by 'URL' or 'Token' to quickly find specific records."

    def is_active(self, obj):
        return obj.is_active

    is_active.short_description = 'Is Active'
    is_active.boolean = True


admin.site.register(UrlUser)
admin.site.register(UrlUsage)
