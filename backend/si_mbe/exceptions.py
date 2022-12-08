from rest_framework.exceptions import NotAuthenticated, NotFound


class NotLogin(NotAuthenticated):
    default_detail = {'message': 'Silahkan login terlebih dahulu untuk mengakses fitur ini'}


class SparepartNotFound(NotFound):
    default_detail = {'message': 'Data sparepart tidak ditemukan'}
