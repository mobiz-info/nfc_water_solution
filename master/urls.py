from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='dashboard'),
    path('overview/', overview, name='overview'),
    path('sales/', sales, name='sales'),
    path('bottles/', bottles, name='bottles'),
    path('coupons/', coupons, name='coupons'),
    path('customer-statistics/', customer_statistics, name='customer-statistics'),
    path('others/', others, name='others'),
    path('branch', Branch_List.as_view(), name='branch'),
    path('branch_create', Branch_Create.as_view(), name='branch_create'),
    path('branch_edit/<str:pk>', Branch_Edit.as_view(), name='branch_edit'),
    path('branch_details/<str:pk>', Branch_Details.as_view(), name='branch_details'),
    path('delete_branch/<str:pk>/',Branch_Delete.as_view(), name='delete_branch'),

    # path('route', Route_List.as_view(), name='route'),
    # path('route_create', Route_Create.as_view(), name='route_create'),
    # path('route_edit/<str:pk>', Route_Edit.as_view(), name='route_edit'),
    # path('route_details/<str:pk>', Route_Details.as_view(), name='route_details'),
    # path('route/delete/<uuid:pk>/', Route_Delete.as_view(), name='route_delete'),

    path('route/', Route_List.as_view(), name='route'),
    path('route_create/', Route_Create.as_view(), name='route_create'),
    path('route_edit/<str:pk>/', Route_Edit.as_view(), name='route_edit'),
    path('route_details/<str:pk>/', Route_Details.as_view(), name='route_details'),
    path('route/delete/<uuid:pk>/', Route_Delete.as_view(), name='route_delete'),


    path('designation', Designation_List.as_view(), name='designation'),
    path('designation_create',Designation_Create.as_view(), name='designation_create'),
    path('designation_edit/<str:pk>', Designation_Edit.as_view(), name='designation_edit'),
    path('designation_details/<str:pk>', Designation_Details.as_view(), name='designation_details'),
    path('designation_delete/<str:pk>', Designation_Delete.as_view(), name='designation_delete'),

    path('branch', branch, name='branch'),
    path('locations_list', Location_List.as_view(), name="locations_list"),
    path('location_add', Location_Adding.as_view(), name="location_add"),
    path('location_edit/<uuid:pk>', Location_Edit.as_view(), name='location_edit'),
    path('location_delete/<uuid:pk>/', Location_Delete.as_view(), name='location_delete'),

    path('category', Category_List.as_view(), name='category'),
    path('category_create',Category_Create.as_view(), name='category_create'),
    path('category_edit/<str:pk>', Category_Edit.as_view(), name='category_edit'),
    path('category_details/<str:pk>', Category_Details.as_view(), name='category_details'),

    path('privacy/', privacy, name='privacy'),
    path('privacy_list/', privacy_list, name='privacy_list'),
    path('privacy/create/', privacy_create, name='privacy_create'),
    path('privacy/edit/<uuid:pk>/', privacy_edit, name='privacy_edit'),
    path('privacy/delete/<uuid:pk>/', privacy_delete, name='privacy_delete'),
    
    path('terms-and-conditions/', terms_and_conditions, name='terms_and_conditions'),
    path('terms_and_conditions_list/', terms_and_conditions_list, name='terms_and_conditions_list'),
    path('terms-and-conditions/create/', terms_and_conditions_create, name='terms_and_conditions_create'),
    path('terms-and-conditions/edit/<uuid:pk>/', terms_and_conditions_edit, name='terms_and_conditions_edit'),
    path('terms-and-conditions/delete/<uuid:pk>/', terms_and_conditions_delete, name='terms_and_conditions_delete'),
    
    path('amount-change-customer-list/', AmountChangesCustomersList.as_view(), name='amount_change_customer_list'),
    path('amount-change-list/', AmountChangesList.as_view(), name='amount_change_list'),
    
    path('create_outstanding_variation_invoice/', create_outstanding_variation_invoice, name='create_outstanding_variation_invoice'),
    path('update_outstanding_variation_invoice/', update_outstanding_variation_invoice, name='update_outstanding_variation_invoice'),
    path('create_outstanding_variation_outstanding/', create_outstanding_variation_outstanding, name='create_outstanding_variation_outstanding'),
    path('update_outstanding_variation_outstanding/', update_outstanding_variation_outstanding, name='update_outstanding_variation_outstanding'),
    
    path('customer-outstanding-variation-clearing/', customer_outstanding_variation_clearing, name='customer_outstanding_variation_clearing'),
    
    path('permission-management/', permission_management_tab_list, name='permission_management_tab_list'),
    path('permission-management/create/', permission_management_tab_create, name='permission_management_tab_create'),
    path('permission-management/update/<uuid:pk>/', permission_management_tab_update, name='permission_management_tab_update'),
    path('permission-management/delete/<uuid:pk>/', permission_management_tab_delete, name='permission_management_tab_delete'),
    
   ]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

