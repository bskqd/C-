from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict

from rest_framework.utils.urls import replace_query_param, remove_query_param


class PaginationWithCurrent(PageNumberPagination):

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('current', self.page.number),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class PaginationWithoutFullUrl(PageNumberPagination):

    def get_next_link(self):
        if not self.page.has_next():
            return None
        url = self.request.get_full_path()[1:]
        page_number = self.page.next_page_number()
        return replace_query_param(url, self.page_query_param, page_number)

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        url = self.request.get_full_path()[1:]
        page_number = self.page.previous_page_number()
        if page_number == 1:
            return remove_query_param(url, self.page_query_param)
        return replace_query_param(url, self.page_query_param, page_number)

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('current', self.page.number),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))