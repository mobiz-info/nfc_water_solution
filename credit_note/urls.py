from django.urls import path,re_path
from . import views

app_name = 'credit_note'

urlpatterns = [
    # re_path(r'^get-building-no/(?P<route_id>.*)/$', views.get_building_no, name='get_building_no'),
    # re_path(r'^get-customers/(?P<route_id>.*)/(?P<building_no>.*)/$', views.get_customer, name='get_customer'),
    # re_path(r'^get-products/(?P<category_id>.*)/$', views.get_products, name='get_products'),
    # re_path(r'^get-customer-rate/(?P<product>.*)/(?P<customer>.*)/$', views.get_customer_rate, name='get_customer_rate'),
    
    re_path(r'credit-note-list/$', views.credit_note_list, name='credit_note_list'),
    re_path(r'credit-note-customers/$', views.credit_note_customers, name='credit_note_customers'),
    re_path(r'create-credit-note/(?P<customer_pk>.*)/$', views.create_credit_note, name='create_credit_note'),
    re_path(r'^credit-note/(?P<pk>.*)/$', views.credit_note_info, name='credit_note_info'),
    re_path(r'^edit-credit-note/(?P<pk>.*)/$', views.edit_credit_note, name='edit_credit_note'),
    re_path(r'^delete-credit-note/(?P<pk>.*)/$', views.delete_credit_note, name='delete_credit_note'),   
]


