from rest_framework.permissions import BasePermission

class IsRole(BasePermission):
    allowed_roles = ()
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_active
                    and request.user.role in self.allowed_roles)

class IsAdmin(IsRole):
    allowed_roles = ('ADMIN',)

class IsStudent(IsRole):
    allowed_roles = ('STUDENT',)

class IsAdminOrMonitor(IsRole):
    allowed_roles = ('ADMIN', 'MONITOR')
