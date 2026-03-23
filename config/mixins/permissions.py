from django.core.exceptions import PermissionDenied

class RoleRequiredMixin:

    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):

        if self.allowed_roles and request.user.role not in self.allowed_roles:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)
