import ipaddress
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


def validate_ip_range(value):
    """Validates an IP range using the ipaddress module."""
    try:
        assert ipaddress.ip_network(value, strict=False).is_global
    except ValueError as err:
        raise ValidationError(
            _('(%value)s is not a valid IP address or network'),
            code='invalid',
            params={'value': value}
        ) from err
    except AssertionError as err:
        raise ValidationError(
            _('(%valie)s is not a public IP address or network'),
            code='invalid',
            params={'value': value}
        ) from err


class ASN(models.Model):
    """Stores an ASN for evaluation."""
    class Status(models.IntegerChoices):
        CLEAR = -1
        UNCHECKED = 0
        BANNED = 1
    # All ASNs are 4 bytes, but are unsigned integers
    # necessitating 8 bytes for storage with signed integers
    asn = models.PositiveBigIntegerField()
    asn_status = models.SmallIntegerField(
        choices=Status.choices,
        default=Status.UNCHECKED
    )
    description = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)


class IPRange(models.Model):
    """Represents possible proxy."""
    address = models.CharField(max_length=255, unique=True,
                               validators=[validate_ip_range])
    range_start = models.BinaryField(max_length=35)
    range_end = models.BinaryField(max_length=35)
    asn = models.ForeignKey(ASN, on_delete=models.CASCADE, blank=True, null=True)
    scheduled = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    check_reason = models.TextField()
