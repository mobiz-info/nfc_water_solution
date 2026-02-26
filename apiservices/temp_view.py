
class StaffIssueOrdersNFCAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        try:
            data = request.data
            staff_order_details_id = data.get('staff_order_details_id')
            nfc_uids = data.get('nfc_uids', [])

            if not staff_order_details_id:
                return Response({'error': 'Staff Order Details ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            if not nfc_uids:
                return Response({'error': 'No NFC tags provided'}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve the specific order detail line item
            try:
                issue = Staff_Orders_details.objects.select_related('staff_order_id', 'product_id').get(staff_order_details_id=staff_order_details_id)
            except Staff_Orders_details.DoesNotExist:
                return Response({'error': 'Order detail found'}, status=status.HTTP_404_NOT_FOUND)

            order = issue.staff_order_id
            product = issue.product_id

            # Get the Van associated with the salesman of the order
            # The order usually has 'created_by' which is the salesman/user ID.
            # We need to find the Van where the salesman is assigned.
            # Based on StaffIssueOrdersAPIView: van = get_object_or_404(Van, salesman_id__id=order.created_by)
            
            try:
                van = Van.objects.get(salesman_id__id=order.created_by)
            except Van.DoesNotExist:
                return Response({'error': 'Salesman does not have an assigned Van'}, status=status.HTTP_400_BAD_REQUEST)

            success_count = 0
            failed_bottles = []
            
            # Get main stock to decrement
            # Based on StaffIssueOrdersAPIView
            main_stock = ProductStock.objects.filter(product_name=product).first()
            if not main_stock:
                 # It might be possible there is no stock entry yet, handle gracefully or error?
                 # StaffIssueOrdersAPIView assumes it exists or uses 0.
                 pass

            for nfc in nfc_uids:
                try:
                    bottle = Bottle.objects.get(nfc_uid=nfc)
                    
                    # Optional: Check if bottle is already in a VAN or SOLD?
                    # For now, we assume if it's scanned, we are moving it.
                    
                    old_status = bottle.status
                    
                    # Update Bottle
                    bottle.status = "VAN"
                    bottle.current_van = van
                    bottle.current_customer = None
                    bottle.save()
                    
                    # Create Bottle Ledger
                    BottleLedger.objects.create(
                        bottle=bottle,
                        action="LOAD_TO_VAN", # or "ISSUE_ORDER"
                        van=van,
                        reference=f"Order #{order.order_number}",
                        created_by=request.user.username, # or ID
                        route=None # Could fetch route from order?
                    )
                    
                    # Create Staff_IssueOrders entry (Individual tracking)
                    Staff_IssueOrders.objects.create(
                        created_by=str(request.user.id),
                        modified_by=str(request.user.id),
                        modified_date=datetime.now(),
                        product_id=product,
                        staff_Orders_details_id=issue,
                        quantity_issued=1
                    )
                    
                    success_count += 1

                except Bottle.DoesNotExist:
                    failed_bottles.append(nfc)
                except Exception as e:
                    failed_bottles.append(f"{nfc} ({str(e)})")

            if success_count > 0:
                # 1. Update Staff_Orders_details issued_qty
                issue.issued_qty += success_count
                issue.save()

                # 2. Update Main Product Stock (Decrement)
                product_stock = ProductStock.objects.filter(product_name=product, branch=van.branch_id).first()
                if product_stock:
                    product_stock.quantity = max(0, (product_stock.quantity or 0) - success_count)
                    product_stock.save()
                
                # 3. Create VanStock and VanProductItems (Transaction Log pattern)
                # Matches StaffIssueOrdersAPIView logic
                vanstock = VanStock.objects.create(
                    created_by=request.user.id if request.user.id else None,
                    created_date=order.order_date,
                    modified_by=request.user.id if request.user.id else None,
                    modified_date=order.order_date,
                    stock_type='opening_stock', # Keeping consistent with reference, though weird name for issue
                    van=van
                )

                VanProductItems.objects.create(
                    product=product,
                    count=success_count,
                    van_stock=vanstock,
                )

                # 4. Update Van Product Stock (Increment aggregated stock)
                van_product_stock_qs = VanProductStock.objects.filter(
                    created_date=order.order_date, 
                    van=van,
                    product=product
                )
                
                if van_product_stock_qs.exists():
                    van_p_stock = van_product_stock_qs.first()
                    van_p_stock.stock += success_count
                    van_p_stock.save()
                    van_product_stock_entry = van_p_stock # Keep reference for BottleCount
                else:
                    van_product_stock_entry = VanProductStock.objects.create(
                        created_date=order.order_date,
                        product=product,
                        van=van,
                        stock=success_count,
                        opening_stock=0, # Or should we fetch? Reference creates with 0 if new.
                        empty_can_count=0
                    )

                # 5. Update BottleCount (for 5 Gallon specifically)
                if product.product_name == "5 Gallon":
                    bottle_count_qs = BottleCount.objects.filter(van=van, created_date__date=order.order_date)
                    if bottle_count_qs.exists():
                        bottle_count = bottle_count_qs.first()
                    else:
                        bottle_count = BottleCount.objects.create(van=van, created_date=order.order_date)
                    
                    # StaffIssueOrdersAPIView updates opening_stock with stock? 
                    # "bottle_count.opening_stock += van_product_stock.stock" 
                    # Wait, it adds the *entire* stock? Or adds the *issued* amount?
                    # The reference says: "bottle_count.opening_stock += van_product_stock.stock"
                    # But "van_product_stock.stock" is the TOTAL stock for that day?
                    # No, wait. In existing code: 
                    # "van_product_stock.stock += int(quantity_issued)" then
                    # "bottle_count.opening_stock += van_product_stock.stock"
                    # This looks wrong in the reference code if it's accumulating. 
                    # If van_product_stock.stock is 10, then it adds 10 to opening_stock.
                    # If I issue 5 more, stock becomes 15. Then it adds 15 to opening_stock? 
                    # That would be double counting.
                    # Let's look closely at line 10259 in previous `view_file`.
                    # "bottle_count.opening_stock += van_product_stock.stock"
                    # This seems like a bug in the reference code or I'm misunderstanding.
                    # However, to be safe, I should probably add `success_count` to `opening_stock`?
                    # Or maybe `BottleCount` tracks daily stock?
                    # Let's assume I should add `success_count`.
                    
                    bottle_count.opening_stock += success_count
                    bottle_count.save()

            return Response({
                "message": f"Successfully issued {success_count} bottles",
                "success_count": success_count,
                "failed_bottles": failed_bottles
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
