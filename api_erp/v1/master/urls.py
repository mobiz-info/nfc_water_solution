from django.urls import path, re_path
from . import views

app_name = 'api_erp_v1_master'

urlpatterns = [
    re_path(r'^route/$', views.routes),
    re_path(r'^sync-erp-route/$', views.sync_erp_route),
    
    re_path(r'^branch/$', views.branch),
    re_path(r'^sync-erp-branch/$', views.sync_erp_branch),
    
    re_path(r'^emirate/$', views.emirate),
    re_path(r'^sync-erp-emirate/$', views.sync_erp_emirate),
    
    re_path(r'^designation/$', views.designation),
    re_path(r'^sync-erp-designation/$', views.sync_erp_designation),
    
    re_path(r'^location/$', views.location),
    re_path(r'^sync-erp-locations/$', views.sync_erp_locations),
    
    re_path(r'^users/$', views.user_list),
    re_path(r'^sync-erp-users/$', views.sync_erp_user_list),
    
    re_path(r'^customer/$', views.customer),
    re_path(r'^sync-erp-customer/$', views.sync_erp_customer),
    
    re_path(r'^product-items/$', views.product_item_list),
    re_path(r'^sync-erp-product/$', views.sync_erp_product),
    
    re_path(r'^van/$', views.van),
    re_path(r'^sync-erp-van/$', views.sync_erp_van),
    
    re_path(r'^payment_methods/$', views.payment_methods),
    
]
