from rest_framework.exceptions import NotAuthenticated, NotFound


class NotLogin(NotAuthenticated):
    default_detail = {'message': 'Silahkan login terlebih dahulu untuk mengakses fitur ini'}


class SparepartNotFound(NotFound):
    default_detail = {'message': 'Data sparepart tidak ditemukan'}


class SalesNotFound(NotFound):
    default_detail = {'message': 'Data penjualan tidak ditemukan'}


class RestockNotFound(NotFound):
    default_detail = {'message': 'Data pengadaan tidak ditemukan'}


class SupplierNotFound(NotFound):
    default_detail = {'message': 'Data supplier tidak ditemukan'}


class AdminNotFound(NotFound):
    default_detail = {'message': 'Data admin tidak ditemukan'}


class ServiceNotFound(NotFound):
    default_detail = {'message': 'Data servis tidak ditemukan'}


class StorageNotFound(NotFound):
    default_detail = {'message': 'Data lokasi penyimpanan tidak ditemukan'}


class BrandNotFound(NotFound):
    default_detail = {'message': 'Data merek / brand tidak ditemukan'}


class CategoryNotFound(NotFound):
    default_detail = {'message': 'Data kategori tidak ditemukan'}


class CustomerNotFound(NotFound):
    default_detail = {'message': 'Data pelanggan tidak ditemukan'}


class MechanicNotFound(NotFound):
    default_detail = {'message': 'Data mekanik tidak ditemukan'}
