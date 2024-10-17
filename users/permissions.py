from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow access only if the user is authenticated and is an admin
        return bool(request.user and request.user.is_authenticated and (request.user.role in ['admin']))

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # If the user is an admin, allow any operation
        if request.user.is_staff or request.user.is_superuser or (request.user.role in ['admin']):
            return True

        # Allow users to update only their own data
        return obj == request.user