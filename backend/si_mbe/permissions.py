from rest_framework import permissions
from si_mbe.exceptions import NotLogin


class IsLogin(permissions.IsAuthenticated):
    message = {'message': 'Silahkan login terlebih dahulu untuk mengakses fitur ini'}

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        raise NotLogin()


class IsAdminRole(permissions.BasePermission):
    message = {'message': 'Akses ditolak'}

    def has_permission(self, request, view):
        if request.user.extend_user.role_id.name == 'Admin':
            return True
        return False
