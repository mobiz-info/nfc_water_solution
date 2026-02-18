import datetime
import uuid
from django.db import models

from accounts.models import Customers
from master.models import CategoryMaster
from product.models import Product

# Create your models here.
class CreditNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    credit_note_no = models.CharField(max_length=200)
    created_date = models.DateTimeField()
    net_taxable = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    vat = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    discount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    amout_total = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    amout_recieved = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    reason_for_return = models.TextField(max_length=200)
    
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'credit_note'
        verbose_name = ('Credit Note')
        verbose_name_plural = ('Credit Note')
    
    def __str__(self):
        return f'{self.id}'
    
    def save(self, *args, **kwargs):
        if not self.created_date:
            self.created_date = datetime.datetime.today().now(),
            
        if not self.credit_note_no:
            year = self.created_date.strftime("%y")
            prefix = f"CN-{year}/"

            credit_note_count = CreditNote.objects.filter(
                created_date__year=self.created_date.year,
                is_deleted=False,
                credit_note_no__startswith=prefix,
            ).count()

            new_number = credit_note_count + 1
            self.credit_note_no = f"{prefix}{new_number}"

        super().save(*args, **kwargs)
    
    def credit_note_items (self):
        items = CreditNoteItems.objects.filter(credit_note=self)
        return items
    
    def sub_total(self):
        total = 0
        
        items = CreditNoteItems.objects.filter(credit_note=self)
        for item in items:
            total += item.total_including_vat
        return total
    
    def total_qty(self):
        total = 0
        items = CreditNoteItems.objects.filter(credit_note=self)
        for item in items:
            total += item.qty
        return total
    
    def items_total_discount_amount(self):
        total = 0
        # Calculate the sub-total for SalesItems
        items =  CreditNoteItems.objects.filter(credit_note=self)
        for item in items:
            total += item.total_including_vat
        total = total - self.discount
        return total
    
class CreditNoteItems(models.Model):
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    qty = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    total_including_vat = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    remarks = models.TextField()
    is_deleted = models.BooleanField(default=False)
    
    category = models.ForeignKey(CategoryMaster, on_delete=models.CASCADE,null=True,blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True,blank=True)
    credit_note = models.ForeignKey(CreditNote, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'credit_not_items'
        verbose_name = ('Credit Note Items')
        verbose_name_plural = ('Credit Note Items')
    
    def __str__(self):
        return str(self.credit_note.credit_note_no)