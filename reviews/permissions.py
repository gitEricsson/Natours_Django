from rest_framework import permissions

class IsUser(permissions.BasePermission):
    # Custom permission to only allow access to users with roles 'user'.
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in ['user'])
    
class IsUserOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow access only if the user is authenticated and is an admin or lead-guide
        return bool(request.user and request.user.is_authenticated and (request.user.role in ['user', 'admin']))