from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """Only the admin can edit"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"

class IsSelfOrAdmin(BasePermission):
    """Only the admin or a user can edit self"""
    def has_object_permission(self, request, view, obj):
        return request.user.role == "admin" or obj == request.user

class IsCommunityAdminOrAdmin(BasePermission):
    """Only the community's admin or a platform admin can edit community"""
    def has_object_permission(self, request, view, obj):
        return request.user.role == "admin" or obj.admin == request.user
    
class IsBusinessOwnerOrAdmin(BasePermission):
    """Only the business owner or platform admin can edit/delete a business"""
    def has_object_permission(self, request, view, obj):
        return request.user.role == "admin" or obj.owner == request.user

class IsCommunityAdmin(BasePermission):
    """Only community admins can access this"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "community admin"