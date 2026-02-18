from django.contrib import admin
from .models import *

# Register your models here.
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id','first_name', 'last_name','username')
    search_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
    )
    list_filter = ("user_type",)
    ordering = ('-id',)
admin.site.register(CustomUser,CustomUserAdmin)

class CustomersAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'created_date', 'custom_id','visit_schedule')
    ordering = ('-created_date',)
    search_fields = ('customer_name', 'custom_id') 
admin.site.register(Customers,CustomersAdmin)

class SendNotificationAdmin(admin.ModelAdmin):
    list_display = ('device_token', 'user', 'created_on')
    ordering = ('-created_on',)
admin.site.register(Send_Notification,SendNotificationAdmin)
admin.site.register(GpsLog)
admin.site.register(CustomUserExportStatus)