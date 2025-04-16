from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to edit objects.
    Read access is allowed to anyone (authenticated or not).
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the admin user.
        # Ensure user is authenticated first.
        if not request.user or not request.user.is_authenticated:
            return False

        # Check if the authenticated user has the 'admin' role.
        # Assumes the User model has a 'role' attribute.
        return request.user.role == 'admin'

    # has_object_permission could be added later for finer-grained control if needed
    # def has_object_permission(self, request, view, obj):
    #     # Read permissions are allowed to any request,
    #     # so we'll always allow GET, HEAD or OPTIONS requests.
    #     if request.method in permissions.SAFE_METHODS:
    #         return True
    #
    #     # Write permissions are only allowed to the admin user.
    #     if not request.user or not request.user.is_authenticated:
    #         return False
    #     return request.user.role == 'admin'


class IsAuthenticatedCreateOrAdminReadUpdateDelete(permissions.BasePermission):
    """
    Allows authenticated users to create (POST).
    Allows admin users to read, update, and delete (GET, PUT, PATCH, DELETE).
    """

    def has_permission(self, request, view):
        # Allow POST requests for any authenticated user.
        if request.method == 'POST':
            return request.user and request.user.is_authenticated

        # For any other method (GET, PUT, PATCH, DELETE, HEAD, OPTIONS),
        # require the user to be an authenticated admin.
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'admin'

    # Optional: Add has_object_permission if needed for instance-level checks later
    # def has_object_permission(self, request, view, obj):
    #     # Allow POST (handled by has_permission)
    #     if request.method == 'POST':
    #          return request.user and request.user.is_authenticated # Or True if has_permission handles it

    #     # For other methods, only allow admin
    #     if not request.user or not request.user.is_authenticated:
    #         return False
    #     return request.user.role == 'admin'