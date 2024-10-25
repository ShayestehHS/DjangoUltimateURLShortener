from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from urls.models import URL


def invalidate_cache(url_object: URL):
    cache.delete(url_object.token)


@receiver(post_save, sender=URL)
def invalidate_cache_on_update(sender, instance, **kwargs):
    invalidate_cache(instance)


@receiver(post_delete, sender=URL)
def invalidate_cache_on_delete(sender, instance, **kwargs):
    invalidate_cache(instance)
