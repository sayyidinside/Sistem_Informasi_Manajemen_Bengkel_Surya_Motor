from rest_framework import pagination
from rest_framework.response import Response


class SearchPagination(pagination.PageNumberPagination):
    page_size = 25
    message = ''
    status = None

    def get_paginated_response(self, data):
        return Response({
            'message': self.message,
            'count_item': self.page.paginator.count,
            'total_page':  self.page.paginator.num_pages,
            'current_page': self.page.number,
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'results': data
        }, status=self.status)
