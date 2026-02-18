from django.contrib import admin
from django.views.static import serve
from django.urls import  include, path, re_path

from core import settings
from master import views as general_views
from master.whatsapp_convesation import water_order_handler

urlpatterns = [
    path('ckeditor/', include('ckeditor_uploader.urls')),

    path('', include('master.urls')),
    path('admin/', admin.site.urls),
    path('dashboard/',general_views.home,name='home'),
    
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path("", include("custody.urls")),
    path('bottle/', include('bottle_management.urls')),
    
    path('product/', include('product.urls')),
    path('van/', include('van_management.urls')),
    path('client/', include('client_management.urls')),
    path('coupon/',include('coupon_management.urls')),
    path('care/',include('customer_care.urls')),
    path('order/',include('order.urls')),
    path('competitor_analysis/',include('competitor_analysis.urls')),
    path('sales_management/',include('sales_management.urls')),
    path('tax_settings/',include(('tax_settings.urls'),namespace='tax_settings')),
    path('invoice-management/',include(('invoice_management.urls'),namespace='invoice')),
    path('credit-note/',include(('credit_note.urls'),namespace='credit_note')),
    
    path('water_order_handler/', water_order_handler, name='water_order_handler'),
    
    path('api/',include('apiservices.urls')),
    
    # path('api-auth/', include('rest_framework.urls')),
    path('erp-api/v1/auth/', include(('api_erp.v1.authentication.urls','authentication'), namespace='api_erp_v1_authentication')),
    
    path('erp-api/v1/master/',include(('api_erp.v1.master.urls','master'), namespace='api_erp_v1_master')),
    path('erp-api/v1/transaction/',include(('api_erp.v1.transaction.urls','transaction'), namespace='api_erp_v1_transaction')),
    
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]
