from django.core.exceptions import ValidationError


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
