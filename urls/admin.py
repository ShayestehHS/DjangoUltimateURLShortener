from django.contrib import admin
from .models import UrlUsage
from urls.models import Url
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ("id", "username", "email", "first_name", "last_name", "is_staff")
    search_fields = ("id", "username", "email")


@admin.register(Url)
class UrlAdmin(admin.ModelAdmin):
    fields = ("user","url", "short_url", "created_at", "expiration_date")
    readonly_fields = (
        "short_url",
        "created_at",
    )
    list_display = ("id","__str__", "user","token","new_url", "created_at", "is_active")
    ordering = ("-updated_at",)
    search_fields = ("token", "url")
    search_help_text = "Search by 'URL' or 'Token' to quickly find specific records."

    def is_active(self, obj):
        return obj.is_active

    is_active.short_description = "Is Active"
    is_active.boolean = True




admin.site.register(UrlUsage)
