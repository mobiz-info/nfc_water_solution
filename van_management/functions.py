from django.db.models import Sum

from master.models import RouteMaster
from product.models import Staff_Orders_details
from van_management.models import Van, Van_Routes, VanProductStock, VanSaleDamage
from client_management.models import CustomerSupply


def vanstock_curreptions(van, date):
    van_instance = Van.objects.get(pk=van)
    f_gallon_supply = CustomerSupply.objects.filter(
        salesman=van_instance.salesman, 
        created_date__date=date, 
        customersupplyitems__product__product_name="5 Gallon"
    )
    
    if VanProductStock.objects.filter(product__product_name="5 Gallon",van=van_instance,created_date=date).exists():
        van_stock = VanProductStock.objects.get(
            product__product_name="5 Gallon", 
            van=van_instance, 
            created_date=date
        )

        total_sales = f_gallon_supply.exclude(customer__sales_type="FOC").aggregate(
            total_quantity=Sum('customersupplyitems__quantity')
        )['total_quantity'] or 0

        total_foc = f_gallon_supply.filter(customer__sales_type="FOC").aggregate(
            total_quantity=Sum('customersupplyitems__quantity')
        )['total_quantity'] or 0

        total_foc += f_gallon_supply.aggregate(
            total_quantity=Sum('allocate_bottle_to_free')
        )['total_quantity'] or 0

        total_empty = f_gallon_supply.aggregate(
            total_quantity=Sum('collected_empty_bottle')
        )['total_quantity'] or 0

        damage_instance = VanSaleDamage.objects.filter(van=van_instance, created_date__date=date)
        total_damage = damage_instance.aggregate(total_damage=Sum('quantity'))['total_damage'] or 0
        damage_bottles = damage_instance.filter(reason__reason__iexact="damage").aggregate(total_damage=Sum('quantity'))['total_damage'] or 0
        leak_bottles = damage_instance.filter(reason__reason__iexact="leak").aggregate(total_damage=Sum('quantity'))['total_damage'] or 0
        service_bottles = damage_instance.filter(reason__reason__iexact="service").aggregate(total_damage=Sum('quantity'))['total_damage'] or 0

        # Update van stock
        if van_stock.sold_count != total_sales:
            van_stock.sold_count = total_sales

        if van_stock.foc != total_foc:
            van_stock.foc = total_foc

        if van_stock.empty_can_count != total_empty:
            van_stock.empty_can_count += total_empty - leak_bottles - service_bottles

        if van_stock.damage_count != total_damage:
            van_stock.damage_count += total_damage
            
        staff_order_details = Staff_Orders_details.objects.filter(staff_order_id__order_date=date,product_id__product_name="5 Gallon",staff_order_id__created_by=van_instance.salesman.pk)
        issued_count = staff_order_details.aggregate(total_count=Sum('issued_qty'))['total_count'] or 0
        
        net_load = van_stock.opening_count + issued_count
        total_sale = total_sales + total_foc
        
        balance_stock = net_load - total_sale - damage_bottles
        
        if van_stock.stock != balance_stock:
            if balance_stock >= 0 :
                van_stock.stock = balance_stock
            else:
                van_stock.stock = 0
        
        van_stock.save()
