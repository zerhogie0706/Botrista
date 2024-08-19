from rest_framework import permissions


class ManangerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.userprofile.role == 'Manager'
