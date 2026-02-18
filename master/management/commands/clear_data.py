import datetime
from django.core.management.base import BaseCommand
from accounts.models import CustomUser, Customers
from client_management.models import CustodyCustom, Customer_Inhand_Coupons, CustomerCart, CustomerCoupon, CustomerCouponStock, CustomerCustodyStock, CustomerOrders, CustomerOutstanding, CustomerOutstandingReport, CustomerReturn, CustomerSupply, CustomerSupplyStock, DialyCustomers, NonvisitReport, OutstandingAmount, Vacation
from coupon_management.models import CouponLeaflet, FreeLeaflet, NewCoupon
from customer_care.models import CouponPurchaseModel, CustodyPullOutModel, CustomerComplaint, DiffBottlesModel, OtherRequirementModel
from invoice_management.models import Invoice
from order.models import ChangeOrReturn, Customer_Order
from sales_management.models import CollectionPayment, CustomerCoupons, OutstandingLog, SaleEntryLog, SalesmanSpendingLog, Transaction, Transactionn
from van_management.models import CustomerProductReplace, CustomerProductReturn
from django.db.models import Count,Sum

class Command(BaseCommand):
    help = 'Generate usernames and passwords for customers based on their name and mobile number'

    def handle(self, *args, **kwargs):
        # custom_ids = ["2257","1909","1651","1657","1658","2087","1663","2262","2264","2089","1898","2320","1673","1896","2058","2090","2091","2092","2105","2062","2095","1680","1968","2050","2096","2052","2054","2214","1763","1764","1765","1766","1768","1769","1772","1792","1790","1778","1779","1780","1781","1782","1783","1784","1785","1786","1787","1789","1775","1791","1794","1797","1799","2080","2081","1805","2269","2304","1698","2988","1807","1809","2267","2309","2273","1958","2234","1963","2316","1976","1987","1990","1995","2172","1998","2001","2002","2003","2069","2071","2279","2280","2326","2082","2083","1894","2201","1908","2229","2244","1521","1522","1525","1526","1527","1528","1529","1530","1531","1570","1536","2171","2283","2149","2152","2324","1557","1558","2295","2068","1581","2168","1587","1588","1589","1647","3626","4140","3974","3976","4385","4151","1970","1804","1973","1962","2055","2187","2174","2181","1944","2185","1999","2175","2258"]
        # customers_ids = Customers.objects.filter(is_guest=False, sales_type="CASH COUPON")
        # customers_ids.update(sales_type="CASH")
        
        customers_ids = Customers.objects.filter(is_guest=False, routes__route_name="S-08").values_list('pk')
        # for customer in customers:
        #     if customer.user_id:
        #         CustomUser.objects.filter(pk=customer.user_id.pk).delete()
        # customers.delete()
        
        
        Invoice.objects.filter(customer__pk__in=customers_ids).delete()
        CustomerOutstanding.objects.filter(customer__pk__in=customers_ids).delete()
        CustomerOutstandingReport.objects.filter(customer__pk__in=customers_ids).delete()
        CustodyCustom.objects.filter(customer__pk__in=customers_ids).delete()
        CustomerCustodyStock.objects.filter(customer__pk__in=customers_ids).delete()
        CustodyPullOutModel.objects.filter(customer__pk__in=customers_ids).delete()
        CustomerReturn.objects.filter(customer__pk__in=customers_ids).delete()
        Customer_Inhand_Coupons.objects.filter(customer__pk__in=customers_ids).delete()
        CustomerCoupon.objects.filter(customer__pk__in=customers_ids).delete()
        CustomerCouponStock.objects.filter(customer__pk__in=customers_ids).delete()
        CustomerSupply.objects.filter(customer__pk__in=customers_ids).delete()
        CustomerSupplyStock.objects.filter(customer__pk__in=customers_ids).delete()
        CustomerOrders.objects.filter(customer__pk__in=customers_ids).delete()
        NonvisitReport.objects.filter(customer__pk__in=customers_ids).delete()
        CustomerCart.objects.filter(customer__pk__in=customers_ids).delete()
        DialyCustomers.objects.filter(is_guest=False, customer__pk__in=customers_ids).delete()
        
        Vacation.objects.filter(customer__pk__in=customers_ids).delete()
        DiffBottlesModel.objects.filter(customer__pk__in=customers_ids).delete()
        OtherRequirementModel.objects.filter(customer__pk__in=customers_ids).delete()
        CouponPurchaseModel.objects.filter(customer__pk__in=customers_ids).delete()
        CustomerComplaint.objects.filter(customer__pk__in=customers_ids).delete()
        Customer_Order.objects.filter(customer_id__pk__in=customers_ids).delete()
        # ChangeOrReturn.objects.filter(customer__pk__in=customers_ids).delete()
        SaleEntryLog.objects.filter(customer__pk__in=customers_ids).delete()
        OutstandingLog.objects.filter(customer__pk__in=customers_ids).delete()
        Transaction.objects.filter(customer__pk__in=customers_ids).delete()
        CustomerCoupons.objects.filter(customer__pk__in=customers_ids).delete()
        Transactionn.objects.filter(customer__pk__in=customers_ids).delete()
        CollectionPayment.objects.filter(customer__pk__in=customers_ids).delete()
        SalesmanSpendingLog.objects.filter(customer__pk__in=customers_ids).delete()
        CustomerProductReturn.objects.filter(customer__pk__in=customers_ids).delete()
        CustomerProductReplace.objects.filter(customer__pk__in=customers_ids).delete()
        CustomerProductReplace.objects.filter(customer__pk__in=customers_ids).delete()
       
        # coupon_instance = NewCoupon.objects.get(pk="fc4c8f18-dd2d-40a4-a75f-70d01d53a28a")
        # CouponLeaflet.objects.filter(coupon=coupon_instance).update(used=True)
        # FreeLeaflet.objects.filter(coupon=coupon_instance).update(used=True)
        
