from django.conf import settings
from django.urls import path,re_path
from django.conf.urls.static import static
from django.views.generic import TemplateView

from .views import *
from accounts import views

urlpatterns = [
    path('move-schedule-view',move_schedule_view, name='move_schedule_view'),
    
    path('login',user_login, name='login'),
    path('users', Users_List.as_view(), name='users'),
    path('user_create',User_Create.as_view(), name='user_create'),
    path('user_edit/<str:pk>', User_Edit.as_view(), name='user_edit'),
    path('user_details/<str:pk>', User_Details.as_view(), name='user_details'),
    path('user_delete/<str:pk>', User_Delete.as_view(), name='user_delete'),
    path('customer_complaint/<str:pk>/', CustomerComplaintView.as_view(), name='customer_complaint'),


    path('customers', Customer_List.as_view(), name='customers'),
    path('customer_create',create_customer, name='customer_create'),
    path('load_locations/', load_locations, name='load_locations'),
    path('customer_details/<str:pk>', Customer_Details.as_view(), name='customer_details'),
    path('edit_customer/<str:pk>',edit_customer, name='edit_customer'),
    path('delete_customer/<str:pk>',delete_customer, name='delete_customer'),
    path('customer_list_excel', customer_list_excel, name="customer_list_excel"),
    path('customer_qr_multiple_print', print_multiple_qrs, name="print_multiple_qrs"),
    
    path('visit_days_assign/<str:customer_id>', visit_days_assign, name="visit_days_assign"),
    path('customer_rate_history/<str:pk>/', CustomerRateHistoryListView.as_view(), name='customer_rate_history'),
    re_path(r'^other_product_rate_change/(?P<pk>.*)/$',  OtherProductRateChangeView.as_view(), name='other_product_rate_change'),   
    path('customer-username-change/<uuid:customer_id>/', customer_username_change, name='customer_username_change'),
    path('customer-password-change/<uuid:customer_id>/', customer_password_change, name='customer_password_change'),
    
    path('latest_customers', Latest_Customer_List.as_view(), name='latest_customers'),
    path('inactive_customers', Inactive_Customer_List.as_view(), name='inactive_customers'),
    path('print_inactive_customers', PrintInactiveCustomerList.as_view(), name='print_inactive_customers'),
    path('non_visited_customers', NonVisitedCustomersView.as_view(), name="non_visited_customers"),

    path('change-password/<int:user_id>/', change_password, name='change_password'),
    path('password-change-done/', TemplateView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),
    
    path('missing_customers', MissingCustomersView.as_view(), name='missing_customers'),
    path('missing_customers_pdf/', MissingCustomersPdfView.as_view(), name='missing_customers_pdf'),  
    path('missed_on_delivery/<uuid:route_id>/', MissedOnDeliveryView.as_view(), name='missed_on_delivery'),
    path('missed_on_delivery/<uuid:route_id>/print/', MissedOnDeliveryPrintView.as_view(), name='missed_on_delivery_print'),
    
    path('processing_log', processing_log_list, name='processing_log'),
    
    path('gps_settings/', Gps_Route_List.as_view(), name='gps_settings'),
    path('gps_active/<uuid:route_id>/', activate_gps_for_route, name='gps_active'),
    path("gps_lock_view/<uuid:route_id>/", gps_lock_view, name="gps_lock_view"),
]
