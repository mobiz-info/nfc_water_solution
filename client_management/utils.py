from decimal import Decimal
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from accounts.models import CustomUser
from client_management.models import CustomerCredit
from invoice_management.models import Invoice

def get_customer_outstanding_amount(customer):
    
    invoice_total = Invoice.objects.filter(
        customer=customer,
        # salesman = salesman,
        is_deleted=False
    ).aggregate(
        total=Sum(
            ExpressionWrapper(
                F("amout_total") - F("amout_recieved"),
                output_field=DecimalField()
            )
        )
    )["total"] or Decimal("0.00")
    customer_credit = (
        CustomerCredit.objects
        .filter(customer=customer)
        .aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    )
    final_outstanding = invoice_total - customer_credit

    return final_outstanding

def get_salesman_from_customer(customer):
    return CustomUser.objects.filter(
        route=customer.routes
    ).first()