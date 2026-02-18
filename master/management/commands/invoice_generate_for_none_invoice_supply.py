import datetime
import random

from django.db.models import Q
from django.core.management.base import BaseCommand

from accounts.models import CustomUser
from client_management.models import CustomerSupply, CustomerSupplyItems, DialyCustomers, InactiveCustomers
from invoice_management.models import Invoice, InvoiceDailyCollection, InvoiceItems
from master.functions import generate_receipt_no
from sales_management.models import Receipt

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        
        supplies = CustomerSupply.objects.filter(invoice_no="").exclude(customer__sales_type="FOC")
        for supply in supplies:
            date_part = supply.created_date.strftime('%Y%m%d')
            # Create the invoice
            invoice = Invoice.objects.create(
                # invoice_no=generate_invoice_no(supply.created_date.date()),
                created_date=supply.created_date,
                net_taxable=supply.net_payable,
                vat=supply.vat,
                discount=supply.discount,
                amout_total=supply.subtotal,
                amout_recieved=supply.amount_recieved,
                customer=supply.customer,
                reference_no="generated from command"
            )
            
            if supply.customer.sales_type == "CREDIT":
                invoice.invoice_type = "credit_invoice"
            if invoice.amout_total == invoice.amout_recieved:
                invoice.invoice_status = "paid"
            invoice.save()
            
            supply.invoice_no = invoice.invoice_no
            supply.save()

            # Create invoice items
            for item in CustomerSupplyItems.objects.filter(customer_supply=supply):
                
                InvoiceItems.objects.create(
                    category=item.product.category,
                    product_items=item.product,
                    qty=item.quantity,
                    rate=item.amount,
                    invoice=invoice,
                    remarks='invoice genereted from supply items reference no : ' + invoice.reference_no
                )
                # print("invoice generate")
            InvoiceDailyCollection.objects.create(
                invoice=invoice,
                created_date=supply.created_date,
                customer=invoice.customer,
                salesman=supply.customer.sales_staff,
                amount=invoice.amout_recieved,
            )

            invoice_numbers = []
            invoice_numbers.append(invoice.invoice_no)
                
            receipt = Receipt.objects.create(
                transaction_type="supply",
                instance_id=str(supply.id),  
                amount_received=supply.amount_recieved,
                customer=supply.customer,
                invoice_number=",".join(invoice_numbers),
                created_date=invoice.created_date
            )
            
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {supply.invoice_no}'))
            
        self.stdout.write(self.style.SUCCESS(f'Successfully updated all supplies are updated'))
