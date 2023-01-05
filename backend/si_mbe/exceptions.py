from rest_framework.exceptions import NotAuthenticated, NotFound, ValidationError


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


class SalesmanNotFound(NotFound):
    default_detail = {'message': 'Data salesman tidak ditemukan'}


class CustomerValidationError(ValidationError):
    def __init__(self, customer_name=None, customer_contact=None, serializer=None):
        detail = {}
        if customer_name is None:
            detail['customer_name'] = ['Baris ini harus diisi jika mengisi baris customer_contact']
        if customer_contact is None:
            detail['customer_contact'] = ['Baris ini harus diisi jika mengisi baris customer_name']
        # Call the parent class constructor
        super().__init__(detail)
        self.serializer = serializer


class CustomerConflictError(ValidationError):
    def __init__(self, serializer=None):
        detail = {
            'customer': 'Anda tidak dapat mengisi baris kedua tipe pelanggan secara bersamaan\n'
            'Pelanggan lama = customer_id\n'
            'Pelanggan baru = customer_name dan customer_contact'}
        # Call the parent class constructor
        super().__init__(detail)
        self.serializer = serializer
