from django.urls import path, re_path
from . import views

app_name = 'api_erp_v1_transaction'

urlpatterns = [
    re_path(r'^sales_invoices_list/$', views.sales_invoices_list),
    re_path(r'^customer_transaction/$', views.customer_transaction),
    re_path(r'^saletransaction/$', views.saletransaction),
    re_path(r'^process_sales_transaction/$', views.process_sales_transaction),
    re_path(r'^expense_summary/$', views.expense_summary),
    re_path(r'^sales_summary/$', views.sales_summary),
    
    re_path(r'^van_issued_orders/$', views.van_issued_orders),
    re_path(r'^audit/$', views.audit),
]
