from datetime import datetime
from sales_management.models import *
from client_management.models import *
from django.db.models import Sum

def get_sales_data(customer_pk=None, start_date=None, end_date=None):
    """
    This function fetches sales and collections data based on the customer and date range.
    It returns the formatted data as a list of dictionaries.
    """

    sales = CustomerSupply.objects.exclude(
        customer__sales_type__in=["CASH COUPON", "CREDIT COUPON"]
    ).order_by('-created_date')

    collections = CollectionPayment.objects.all()

    # Filter by customer ID if provided
    if customer_pk:
        sales = sales.filter(customer__pk=customer_pk)
        collections = collections.filter(customer__pk=customer_pk)

    # Filter by date range if both start_date and end_date are provided
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            sales = sales.filter(created_date__date__range=(start_date, end_date))
            collections = collections.filter(created_date__date__range=(start_date, end_date))
        except ValueError:
            raise ValueError("Invalid date format")

    transactions = []

    # Loop through sales and collect relevant data
    for supply in sales:
        van = supply.salesman.salesman_van.first() if supply.salesman else None
        transaction_data = {
            "trX_TIME": supply.created_date.strftime("%d-%m-%Y %H:%M"),
            "trX_TYPE": supply.customer.sales_type,
            "brancH_NAME": supply.customer.branch_id.name if supply.customer.branch_id else "N/A",
            "city": supply.customer.emirate.name if supply.customer.emirate else "N/A",
            "locatioN_NAME": supply.customer.location.location_name if supply.customer.location else "N/A",
            "vehiclE_NUMBER": van.plate if van else "N/A",
            "routE_NAME": supply.customer.routes.route_name if supply.customer.routes else "N/A",
            "customeR_UNIQ_NUMBER": supply.customer.custom_id,
            "beF_TAX_AMOUNT": float(supply.subtotal),
            "taX_AMOUNT": float(supply.vat),
            "witH_TAX_AMOUNT": float(supply.grand_total),
            "receiveD_AMOUNT": float(supply.amount_recieved),
            "paymenT_TYPE": supply.customer.sales_type,
            "banK_NAME": "Bank ",  # Placeholder
            "receipT_NUMBER": supply.invoice_no if supply.invoice_no else "N/A",
            "receipT_DATE": supply.created_date.strftime("%d-%m-%Y"),
            "deliverY_TYPE": supply.customer.customer_type,
            "hdR_DESC": "Electronics Sale",  # Placeholder
            "erP_SYS_EMP_ID": supply.salesman.id if supply.salesman else None,
            "otheR_SYS_HDR_ID": supply.id,
            "salesTransactionLines": [
                {
                    "otheR_SYS_HDR_ID": supply.id,
                    "erP_SYS_ITEM_ID": item.product.id,
                    "linE_DESCRIPTION": item.product.product_name,
                    "uoM_CODE": item.product.unit,  
                    "qty": item.quantity,
                    "uniT_PRICE": float(item.product.rate),
                    "beF_TAX_AMOUNT": float(item.customer_supply.subtotal),
                    "taX_AMOUNT": float(item.customer_supply.vat),
                    "witH_TAX_AMOUNT": float(item.customer_supply.grand_total),
                    "otheR_SYS_LINE_ID": item.id
                }
                for item in CustomerSupplyItems.objects.filter(customer_supply=supply)
            ],
            "paymentApplications": [
                {
                    "otheR_SYS_PMT_HDR_ID": col.id,
                    "applieD_INVOICE_ID": supply.id,
                    "applieD_AMOUNT": float(col.amount_received)
                }
                for col in collections.filter(customer=supply.customer)
            ]
        }
        transactions.append(transaction_data)

    return transactions
