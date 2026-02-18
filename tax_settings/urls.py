from django.urls import path,re_path
from . import views

app_name = 'tax_settings'

urlpatterns = [
    re_path(r'tax-types/$', views.tax_types, name='tax_types'),
    re_path(r'create-tax-type/$', views.create_tax_type, name='create_tax_type'),
    re_path(r'^edit-tax-type/(?P<pk>.*)/$', views.edit_tax_type, name='edit_tax_type'),
    re_path(r'^delete-tax-type/(?P<pk>.*)/$', views.delete_tax_type, name='delete_tax_type'),   
]


