"""Register models with the admin site."""

from django.contrib import admin

from .models import IPRange, ASN

admin.site.register(IPRange)
admin.site.register(ASN)
