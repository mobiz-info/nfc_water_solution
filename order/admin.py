from django.contrib import admin
from . models import *

# Register your models here.
admin.site.register(Customer_Order)
admin.site.register(Order)
admin.site.register(Change_Reason)
admin.site.register(Order_change)
admin.site.register(Order_return)