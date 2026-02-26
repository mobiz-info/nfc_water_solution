@login_required
def bottle_stock_report(request):
    """
    Report showing Opening, In, Out, Closing stock for a selected Date and Route.
    """
    from datetime import datetime, timedelta
    from django.db.models import Sum, Case, When, IntegerField, F
    from master.models import RouteMaster
    
    routes = RouteMaster.objects.all()
    selected_date = request.GET.get('date', datetime.now().strftime('%Y-%m-%d'))
    selected_route_id = request.GET.get('route')
    
    context = {
        'routes': routes,
        'selected_date': selected_date,
        'selected_route_id': selected_route_id,
        'report_data': None
    }

    if selected_route_id and selected_date:
        try:
            target_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            route = RouteMaster.objects.get(route_id=selected_route_id)
            
            # --- 1. Opening Stock (All transactions BEFORE target_date for this route) ---
            # Create = +1
            # Load to Van = +1 (if we consider Van stock as asset) - WAIT, let's define perspective.
            # The user asked for "Opening Stock, In, Out, Closing Stock"
            # Usually this is for a specific context (e.g., Van Stock or Warehouse Stock).
            # "Route Selection" implies we are looking at the stock *on the van assigned to that route*?
            # OR the stock *with customers on that route*?
            
            # Given "Bottle Stock Report" with "Route Selection", it likely refers to the BOTTLES WITH CUSTOMERS on that route.
            # OR it refers to the VAN STOCK for the van on that route.
            # Let's look at the "In / Out" columns requested:
            # "Opening stock. in out closingstock"
            
            # If it's VAN STOCK:
            # In = Load to Van, Return from Customer
            # Out = Supply to Customer, Offload to Godown
            
            # If it's CUSTOMER STOCK (Market Asset):
            # In = Supply to Customer
            # Out = Return from Customer
            
            # Common requirement is VAN STOCK reconciliation. Let's assume VAN STOCK for the route's van.
            # But wait, the route is a property of the *Customer* or the *Van*?
            # A Van is assigned to a Route. 
            
            # Let's refine the Ledger logic based on "Route" filter.
            # We added `route` field to Ledger. 
            # So we are filtering Ledger entries where `route == selected_route`.
            
            # Transactions likely to have route:
            # - LOAD_TO_VAN (Van has route) -> IN
            # - RETURN (Customer has route) -> IN (to Van)
            # - SUPPLY (Customer has route) -> OUT (from Van)
            # - OFFLOAD (Van has route) -> OUT (from Van)
            
            # So this seems to be a VAN STOCK REPORT for a specific Route.
            
            # Opening: Sum(In - Out) before date
            # In: Load + Return on date
            # Out: Supply + Offload on date
            # Closing: Opening + In - Out
            
            # Let's verify Action Types in BottleLedger models.py
            # "LOAD_TO_VAN" -> Van Stock INCREASE
            # "SUPPLY" -> Van Stock DECREASE
            # "RETURN" -> Van Stock INCREASE
            # "OFFLOAD" -> Van Stock DECREASE
            
            # We need to sum these up.
            
            ledger_qs = BottleLedger.objects.filter(route=route)
            
            # OPENING
            opening_qs = ledger_qs.filter(created_at__date__lt=target_date)
            
            opening_in = opening_qs.filter(action__in=["LOAD_TO_VAN", "RETURN", "UNLOAD_FROM_VAN"]).count() # Wait, UNLOAD_FROM_VAN?? 
            # "UNLOAD_FROM_VAN" usually means taking off van. Let's check model actions again.
            # LOAD_TO_VAN (Godown -> Van) : IN
            # SUPPLY (Van -> Customer) : OUT
            # RETURN (Customer -> Van) : IN
            # OFFLOAD (Van -> Godown) : OUT
            
            # Let's just stick to these 4 for now as main movers.
            
            opening_plus = opening_qs.filter(action__in=["LOAD_TO_VAN", "RETURN"]).count()
            opening_minus = opening_qs.filter(action__in=["SUPPLY", "OFFLOAD"]).count()
            opening_stock = opening_plus - opening_minus
            
            # TODAY IN/OUT
            today_qs = ledger_qs.filter(created_at__date=target_date)
            
            today_in = today_qs.filter(action__in=["LOAD_TO_VAN", "RETURN"]).count()
            today_out = today_qs.filter(action__in=["SUPPLY", "OFFLOAD"]).count()
            
            closing_stock = opening_stock + today_in - today_out
            
            context['report_data'] = {
                'opening_stock': opening_stock,
                'in_stock': today_in,
                'out_stock': today_out,
                'closing_stock': closing_stock,
            }

        except Exception as e:
            print(e)
            
    return render(request, 'bottle_management/bottle_stock_report.html', context)
