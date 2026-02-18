from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status


class CustomPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response({
            'StatusCode': 6000,
            'status': status.HTTP_200_OK,
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'data': data
        })
