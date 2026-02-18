from django.urls import path
from .views import *



urlpatterns = [
    path('couponType',couponType, name='couponType'),
    path('create_couponType/',create_couponType, name='create_couponType'),
    path('view_couponType/<uuid:coupon_type_id>/', view_couponType, name="view_couponType"),
    path('edit_CouponType/<uuid:coupon_type_id>/', edit_CouponType, name="edit_CouponType"),
    path('delete_couponType/<uuid:coupon_type_id>/', delete_couponType, name='delete_couponType'),

#----------------------------------New Coupon-------------------------------------------------------------------

    path('get_next_coupon_bookno',get_next_coupon_bookno, name='get_next_coupon_bookno'),
    path('get_leaf_used_status_change',get_leaf_used_status_change, name='get_leaf_used_status_change'),
    
    path('new_coupon',new_coupon, name='new_coupon'),
    path('create_Newcoupon/',create_Newcoupon, name='create_Newcoupon'),
    path('generate_leaflets/<uuid:coupon_id>/', generate_leaflets, name='generate_leaflets'),

    path('get_leaflet_serial_numbers/', get_leaflet_serial_numbers, name='get_leaflet_serial_numbers'),
    path('save_coupon_data/', save_coupon_data, name='save_coupon_data'),
    path('view_Newcoupon/<uuid:coupon_id>/', view_Newcoupon, name="view_Newcoupon"),
    path('edit_NewCoupon/<uuid:coupon_id>/', edit_NewCoupon, name="edit_NewCoupon"),

    path('delete_Newcoupon/<uuid:coupon_id>/', delete_Newcoupon, name='delete_Newcoupon'),
    path('customer_stock/', customer_stock, name='customer_stock'),
    path('customer-stock-coupon-details/<uuid:customer>/', customer_stock_coupon_details, name='customer_stock_coupon_details'),
    path('generate_excel/', generate_excel, name='generate_excel'),
    path('customer_stock_pdf/', customer_stock_pdf, name='customer_stock_pdf'),

    path('redeemed_historyy/', redeemed_history, name='redeemed_historyy'),
    path('redeemed-coupon-details/<uuid:supply_pk>/', redeemed_coupon_details, name='redeemed_coupon_details'),
    path('print_redeemed_history/', print_redeemed_history, name='print_redeemed_history'),
    path('coupon_recharge/', coupon_recharge_list, name='coupon_recharge'),
    path("edit_coupon_recharge/<uuid:pk>/", edit_coupon_recharge, name="edit_coupon_recharge"),
    path("delete_coupon_recharge/<uuid:pk>/", delete_coupon_recharge, name="delete_coupon_recharge"),
    path(
        'reports/route-wise-coupon-report/',
        route_wise_coupon_report,
        name='route_wise_coupon_report'
    ),
    path('route-wise-coupon-balance/<uuid:route_id>/', route_balance_books, name='route_balance_books'),



 ]
