from rest_framework import permissions

class IsSubscribedOrHasTokens(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.user == request.user:
            return True
        else:
            return False