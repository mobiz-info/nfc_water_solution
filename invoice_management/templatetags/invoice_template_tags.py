import datetime
from datetime import timedelta
from django.utils import timezone

from django import template
from django.db.models import Q, Sum, F, Case, When, IntegerField

from accounts.models import Customers
from client_management.models import *
from sales_management.models import *

register = template.Library()

@register.simple_tag
def get_total_values(queryset):
    # Ensure queryset is a QuerySet, not a list
    if isinstance(queryset, list):
        # If queryset is a list, convert it back into a QuerySet
        queryset = Invoice.objects.filter(pk__in=[instance.pk for instance in queryset])
    
    # Query the database for the total values
    net_taxable = queryset.aggregate(total_net_taxable=Sum('net_taxable'))['total_net_taxable'] or 0
    vat = queryset.aggregate(total_vat=Sum('vat'))['total_vat'] or 0
    discount = queryset.aggregate(total_discount=Sum('discount'))['total_discount'] or 0
    amout_total = queryset.aggregate(total_amout_total=Sum('amout_total'))['total_amout_total'] or 0
    amout_recieved = queryset.aggregate(total_amout_recieved=Sum('amout_recieved'))['total_amout_recieved'] or 0
    
    return {
        "net_taxable": net_taxable,
        "vat": vat,
        "discount": discount,
        "amout_total": amout_total,
        "amout_recieved": amout_recieved,
    }