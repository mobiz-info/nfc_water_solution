import requests
import datetime
from decimal import Decimal
from datetime import datetime

from django.contrib.auth.models import User
from django.db.models import Q, Sum, Min, Max
from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError

from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, renderer_classes

from api_erp.v1.master.custom_pagination import CustomPagination
from master.models import BranchMaster, DesignationMaster, EmirateMaster, LocationMaster, RouteMaster
from accounts.models import CustomUser, Customers
from client_management.models import *
from van_management.models import *
from sales_management.models import *

from api_erp.v1.master.serializers import *


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def routes(request):
    route_id = request.GET.get('route_id')
    many=True
    
    instances = RouteMaster.objects.all()
    
    if route_id:
        instances = instances.filter(pk=route_id).first()
        many=False
        
    serializer = RouteMasterSerializer(instances,many=many)
    
    status_code = status.HTTP_200_OK
    response_data = {
        "StatusCode": 6000,
        "status": status_code,
        "data": serializer.data
    }

    return Response(response_data, status_code)


@api_view(['POST'])
def sync_erp_route(request):
    if isinstance(request.data, list):  
        serializer = RouteSerializer(data=request.data, many=True)
        if serializer.is_valid():
            instances = serializer.save()

            route_ids = [instance.route.route_id for instance in instances]
            print("route_ids",route_ids)
            RouteMaster.objects.filter(route_id__in=route_ids).update(is_exported=True)
            
            return Response({"message": "Data stored successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid data format"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def branch(request):
    branch_id = request.GET.get('branch_id')
    many=True
    
    instances = BranchMaster.objects.all()
    
    if branch_id:
        instances = instances.filter(pk=branch_id).first()
        many=False
        
    serializer = BranchMasterSerializer(instances,many=many)
    
    status_code = status.HTTP_200_OK
    response_data = {
        "StatusCode": 6000,
        "status": status_code,
        "data": serializer.data
    }

    return Response(response_data, status_code)


@api_view(['POST'])
def sync_erp_branch(request):
    if isinstance(request.data, list):  
        serializer = BranchSerializer(data=request.data, many=True)
        if serializer.is_valid():
            instances = serializer.save()

            branch_ids = [instance.branch.branch_id for instance in instances]
            print("branch_ids",branch_ids)
            BranchMaster.objects.filter(branch_id__in=branch_ids).update(is_exported=True)
            
            return Response({"message": "Data stored successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid data format"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def emirate(request):
    emirate_id = request.GET.get('emirate_id')
    many=True
    
    instances = EmirateMaster.objects.all()
    
    if emirate_id:
        instances = instances.filter(pk=emirate_id).first()
        many=False
        
    serializer = EmirateMasterSerializer(instances,many=many)
    
    status_code = status.HTTP_200_OK
    response_data = {
        "StatusCode": 6000,
        "status": status_code,
        "data": serializer.data
    }

    return Response(response_data, status_code)


@api_view(['POST'])
def sync_erp_emirate(request):
    if isinstance(request.data, list):  
        serializer = EmirateSerializer(data=request.data, many=True)
        if serializer.is_valid():
            instances = serializer.save()

            emirate_ids = [instance.emirate.emirate_id for instance in instances]
            print("emirate_ids",emirate_ids)
            EmirateMaster.objects.filter(emirate_id__in=emirate_ids).update(is_exported=True)
            
            return Response({"message": "Data stored successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid data format"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def designation(request):
    designation_id = request.GET.get('designation_id')
    many=True
    
    instances = DesignationMaster.objects.all()
    
    if designation_id:
        instances = instances.filter(pk=designation_id).first()
        many=False
        
    serializer = DesignationMasterSerializer(instances,many=many)
    
    status_code = status.HTTP_200_OK
    response_data = {
        "StatusCode": 6000,
        "status": status_code,
        "data": serializer.data
    }

    return Response(response_data, status_code)


@api_view(['POST'])
def sync_erp_designation(request):
    if isinstance(request.data, list):  
        serializer = DesignationSerializer(data=request.data, many=True)
        if serializer.is_valid():
            instances = serializer.save()

            designation_ids = [instance.designation.designation_id for instance in instances]
            print("designation_ids",designation_ids)
            DesignationMaster.objects.filter(designation_id__in=designation_ids).update(is_exported=True)
            
            return Response({"message": "Data stored successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid data format"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def location(request):
    location_id = request.GET.get('location_id')
    many=True
    
    instances = LocationMaster.objects.all()
    
    if location_id:
        instances = instances.filter(pk=location_id).first()
        many=False
        
    serializer = LocationMasterSerializer(instances,many=many)
    
    status_code = status.HTTP_200_OK
    response_data = {
        "StatusCode": 6000,
        "status": status_code,
        "data": serializer.data
    }

    return Response(response_data, status_code)

@api_view(['POST'])
def sync_erp_locations(request):
    if isinstance(request.data, list):  
        serializer = LocationSerializer(data=request.data, many=True)
        if serializer.is_valid():
            instances = serializer.save()

            location_ids = [instance.location.location_id for instance in instances]
            print("location_ids",location_ids)
            LocationMaster.objects.filter(location_id__in=location_ids).update(is_exported=True)
            
            return Response({"message": "Data stored successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid data format"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])
def user_list(request):
    user_id = request.GET.get('user_id')
    many = True

    users = CustomUser.objects.all()

    if user_id:
        users = users.filter(pk=user_id).first()
        many = False

    serializer = CustomUserSerializer(users, many=many)

    response_data = {
        "StatusCode": 6000,
        "status": status.HTTP_200_OK,
        "data": serializer.data
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def sync_erp_user_list(request):
    if isinstance(request.data, list):  
        serializer = CustomUserListSerializer(data=request.data, many=True)
        if serializer.is_valid():
            instances = serializer.save()

            user_list_ids = [instance.id for instance in instances]
            print("user_list_ids",user_list_ids)
            CustomUser.objects.filter(id__in=user_list_ids).update(is_exported=True)
            
            return Response({"message": "Data stored successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid data format"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def customer(request):
    customer_id = request.GET.get('customer_id')

    if customer_id:
        try:
            instance = Customers.objects.get(pk=customer_id)
            serializer = CustomersSerializer(instance)
            return Response({
                "StatusCode": 6000,
                "status": status.HTTP_200_OK,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Customers.DoesNotExist:
            return Response({
                "StatusCode": 6001,
                "message": "Customer not found"
            }, status=status.HTTP_404_NOT_FOUND)

    # Apply filtering only for active and not deleted customers
    queryset = Customers.objects.filter(is_guest=False, is_active=True, is_deleted=False).order_by('-created_date')

    paginator = CustomPagination()
    result_page = paginator.paginate_queryset(queryset, request)
    serializer = CustomersSerializer(result_page, many=True)

    return paginator.get_paginated_response({
        "StatusCode": 6000,
        "status": status.HTTP_200_OK,
        "data": serializer.data
    })
# @api_view(['GET'])
# @permission_classes((AllowAny,))
# @renderer_classes((JSONRenderer,))
# def customer(request):
#     customer_id = request.GET.get('customer_id')
#     many=True
    
#     instances = Customers.objects.all()
#     if customer_id:
#         instances = instances.filter(pk=customer_id).first()
#         many=False
       
#     serializer = CustomersSerializer(instances,many=many)
#     status_code = status.HTTP_200_OK
#     response_data = {
#         "StatusCode": 6000,
#         "status": status_code,
#         "data": serializer.data
#     }

#     return Response(response_data, status_code)


@api_view(['POST'])
def sync_erp_customer(request):
    if isinstance(request.data, list):  
        serializer = CustomerSerializer(data=request.data, many=True)
        if serializer.is_valid():
            instances = serializer.save()

            customer_ids = [instance.customer.customer_id for instance in instances]
            print("customer_ids",customer_ids)
            Customers.objects.filter(is_guest=False, customer_id__in=customer_ids).update(is_exported=True)
            
            return Response({"message": "Data stored successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid data format"}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])
def product_item_list(request):
    product_id = request.GET.get('product_id')
    many = True

    products = ProdutItemMaster.objects.all()

    if product_id:
        products = products.filter(pk=product_id).first()
        many = False

    serializer = ProdutItemMasterSerializer(products, many=many)

    response_data = {
        "StatusCode": 6000,
        "status": status.HTTP_200_OK,
        "data": serializer.data
    }

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['POST'])
def sync_erp_product(request):
    if isinstance(request.data, list):  
        serializer = ProdutSerializer(data=request.data, many=True)
        if serializer.is_valid():
            instances = serializer.save()

            product_ids = [instance.product.product_id for instance in instances]
            print("product_ids",product_ids)
            ProdutItemMaster.objects.filter(product_id__in=product_ids).update(is_exported=True)
            
            return Response({"message": "Data stored successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid data format"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])
def van(request):
    van_id = request.GET.get('van_id')
    many = True

    vans = Van.objects.all()

    if van_id:
        vans = vans.filter(van_id=van_id).first()
        many = False

    serializer = VanSerializers(vans, many=many)

    response_data = {
        "StatusCode": 6000,
        "status": status.HTTP_200_OK,
        "data": serializer.data
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def sync_erp_van(request):
    if isinstance(request.data, list):  
        serializer = VansSerializer(data=request.data, many=True)
        if serializer.is_valid():
            instances = serializer.save()

            van_ids = [instance.van.van_id for instance in instances]
            print("van_ids",van_ids)
            Van.objects.filter(van_id__in=van_ids).update(is_exported=True)
            
            return Response({"message": "Data stored successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid data format"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def payment_methods(request):
    payment_methods = dict(CollectionPayment.PAYMENT_TYPE_CHOICES)

    status_code = status.HTTP_200_OK
    response_data = {
        "StatusCode": 6000,
        "status": status_code,
        "payment_methods": payment_methods
    }

    return Response(response_data, status=status_code)
