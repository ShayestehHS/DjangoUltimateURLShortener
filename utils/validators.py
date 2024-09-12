from django.core.exceptions import ValidationError


def is_https(value):
    if not value.startswith('https://'):
        raise ValidationError('The URL should start with https://')


def validate_not_naive(value):
    if value is None:
        return  # Skip validation if value is None (handle this according to your use case)

    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise ValidationError('The datetime must be timezone-aware.')

