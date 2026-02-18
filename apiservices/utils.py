from django.db.models import Sum
from datetime import timedelta
from product.models import Staff_IssueOrders
from van_management.models import OffloadRequestItems,VanProductStock

def recalculate_van_closing_stock(van, product, date):
    vps = VanProductStock.objects.filter(
        van=van,
        product=product,
        created_date=date
    ).first()

    if not vps:
        return

    # issued today
    issued = Staff_IssueOrders.objects.filter(
        van=van,
        product_id=product,
        created_date__date=date
    ).aggregate(q=Sum('quantity_issued'))['q'] or 0

    # offload today
    offload = OffloadRequestItems.objects.filter(
        offload_request__van=van,
        product=product,
        offload_request__date=date
    ).aggregate(q=Sum('quantity'))['q'] or 0

    # calculate closing
    vps.closing_count = (
        vps.opening_count
        + issued
        - vps.sold_count
        - vps.foc
        - vps.damage_count
        - offload
        + vps.return_count
    )

    # keep real stock in sync
    vps.stock = vps.closing_count
    vps.save()
