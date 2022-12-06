# from django.shortcuts import render
from rest_framework import filters, generics, status
from rest_framework.response import Response
from si_mbe.models import Sparepart
from si_mbe.paginations import CustomPagination
from si_mbe.serializers import SearchSparepartSerializers


class Home(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)


class SearchSparepart(generics.ListAPIView):
    queryset = Sparepart.objects.all().order_by('name')
    serializer_class = SearchSparepartSerializers
    pagination_class = CustomPagination

    lookup_field = 'sparepart_id'

    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'partnumber', 'motor_type', 'sparepart_type', 'brand_id__name']

    def get_paginated_response(self, data):
        if len(data) == 0:
            self.pagination_class.message = 'Sparepart yang dicari tidak ditemukan'
            self.pagination_class.status = status.HTTP_200_OK
        else:
            self.pagination_class.message = 'Pencarian sparepart berhasil'
            self.pagination_class.status = status.HTTP_200_OK
        return super().get_paginated_response(data)


class Dashboard(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return Response({'message': 'Silahkan login terlebih dahulu untuk mengakses fitur ini'},
                            status=status.HTTP_403_FORBIDDEN)
        elif not self.request.user.extend_user.role_id.name == 'Admin':
            return Response({'message': 'Akses ditolak'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'message': 'Berhasil mengkases dashboard'}, status=status.HTTP_200_OK)
