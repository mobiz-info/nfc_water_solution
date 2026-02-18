from django.urls import path,re_path
from . import views

app_name = 'invoice'

urlpatterns = [
    re_path(r'^get-building-no/(?P<route_id>.*)/$', views.get_building_no, name='get_building_no'),
    re_path(r'^get-customers/(?P<route_id>.*)/(?P<building_no>.*)/$', views.get_customer, name='get_customer'),
    re_path(r'^get-products/(?P<category_id>.*)/$', views.get_products, name='get_products'),
    re_path(r'^get-customer-rate/(?P<product>.*)/(?P<customer>.*)/$', views.get_customer_rate, name='get_customer_rate'),
    
    re_path(r'^invoice/(?P<pk>.*)/$', views.invoice, name='invoice'),   
    re_path(r'invoice-list/$', views.invoice_list, name='invoice_list'),
    re_path(r'invoice-customers/$', views.invoice_customers, name='invoice_customers'),
    re_path(r'create-invoice/(?P<customer_pk>.*)/$', views.create_invoice, name='create_invoice'),
    re_path(r'^invoice/(?P<pk>.*)/$', views.invoice_info, name='invoice_info'),
    re_path(r'^edit-invoice/(?P<pk>.*)/$', views.edit_invoice, name='edit_invoice'),
    re_path(r'^delete-invoice/(?P<pk>.*)/$', views.delete_invoice, name='delete_invoice'),
    re_path(r'^customerwise-invoice/$', views.customerwise_invoice, name='customerwise_invoice'), 
    re_path(r'^edit_customerwise_invoice/(?P<customer_id>.*)/$', views.edit_customerwise_invoice, name='edit_customerwise_invoice'), 
    re_path(r'^make-payment/$', views.make_payment, name='make_payment'),
    
    path('payment-adjust/',views.today_route_outstanding_list, name='payment_adjust'),
    re_path(r'^invoice-adjust/(?P<customer_id>.*)/$',views.invoice_adjust,name='invoice_adjust'),
]


