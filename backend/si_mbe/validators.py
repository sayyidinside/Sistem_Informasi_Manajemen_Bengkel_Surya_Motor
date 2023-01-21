from django.core.exceptions import ValidationError


class CustomerValidationError(ValidationError):
    def __init__(self, name=None, contact=None, address=None,
                 status=None, serializer=None):
        detail = {}
        if name is None:
            detail['customer_name'] = ['Baris ini harus diisi jika mengisi data pelanggan baru']
        if contact is None:
            detail['customer_contact'] = ['Baris ini harus diisi jika mengisi data pelanggan baru']
        if address is None:
            detail['customer_address'] = ['Baris ini harus diisi jika mengisi data pelanggan baru']
        if status is None:
            detail['is_workshop'] = ['Baris ini harus diisi jika mengisi data pelanggan baru']
        # Call the parent class constructor
        super().__init__(detail)
        self.serializer = serializer


class CustomerConflictError(ValidationError):
    def __init__(self, serializer=None):
        detail = {
            'customer': 'Anda tidak dapat mengisi baris kedua tipe pelanggan secara bersamaan\n'
            'Pelanggan lama = customer_id\n'
            'Pelanggan baru = customer_name, customer_contact, customer_addres, and is_workshop'}
        # Call the parent class constructor
        super().__init__(detail)
        self.serializer = serializer
