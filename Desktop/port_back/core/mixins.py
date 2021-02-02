from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PaginationWithCurrent(PageNumberPagination):

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('current', self.page.number),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class StandardResultsSetPagination(PaginationWithCurrent):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000
