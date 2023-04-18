from rest_framework import permissions


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAdminOrSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.is_admin or request.user.is_superuser)
        )


class IsCanChangeOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        is_safe_method = request.method in permissions.SAFE_METHODS
        is_correct_user = (
            request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.is_admin
                or request.user.is_moderator
                or obj.author == request.user
            )
        )
        return is_safe_method or is_correct_user
