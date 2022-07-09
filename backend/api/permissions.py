from rest_framework import permissions


# class IsAuthorStaffOrReadOnly(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return request.user.is_admin or request.user.is_staff

#     def has_object_permission(self, request, view, obj):
#         return request.user.is_admin or request.user.is_staff


# class IsAuthorAdminOrReadOnly(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         return (
#             request.method in permissions.SAFE_METHODS
#             or request.user.is_authenticated == request.user.is_admin
#         )


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )


class UserAndAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (
                request.user.is_authenticated
                and (
                    obj.author == request.user
                    or request.user.is_admin
                    or request.user.is_staff
                )
            )
        )
