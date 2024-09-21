from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from urls.models import Url


def invalidate_cache(url_object: Url):
    cache.delete(url_object.token)


@receiver(post_save, sender=Url)
def invalidate_cache_on_update(sender, instance, **kwargs):
    invalidate_cache(instance)


@receiver(post_delete, sender=Url)
def invalidate_cache_on_delete(sender, instance, **kwargs):
    invalidate_cache(instance)
