from rest_framework.exceptions import NotAuthenticated


class NotLogin(NotAuthenticated):
    default_detail = {'message': 'Silahkan login terlebih dahulu untuk mengakses fitur ini'}
