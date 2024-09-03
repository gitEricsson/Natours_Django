from rest_framework import permissions

class IsAdminOrGuide(permissions.BasePermission):
    # Custom permission to only allow access to users with roles 'admin', 'lead-guide', or 'guide'.
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['admin', 'lead-guide', 'guide']

class IsAdminOrLeadGuide(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow access only if the user is authenticated and is an admin or lead-guide
        return bool(request.user and request.user.is_authenticated and (request.user.role in ['admin', 'lead-guide']))