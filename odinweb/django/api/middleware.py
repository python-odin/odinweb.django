from odinweb import _compat
from odinweb.exceptions import PermissionDenied, AccessDenied


class LoginRequired(object):
    """
    A login is required for this API.
    """
    def pre_dispatch(self, request, _):
        user = request.user = request.request.user

        if not user.is_authenticated():
            raise PermissionDenied(message="Login is required")


class PermissionRequired(object):
    """
    Certain permission is required for this API.
    """
    def __init__(self, perm):
        if isinstance(perm, _compat.string_types):
            self.perms = (perm, )
        else:
            self.perms = perm

    def pre_dispatch(self, request, _):
        if not request.user.has_perms(self.perms):
            raise AccessDenied(message="User doesn't have required permissions.")
