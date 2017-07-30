from odinweb.exceptions import PermissionDenied


class LoginRequired(object):
    """
    A login is required for this API.
    """
    def pre_dispatch(self, request, _):
        if not request.request.user.is_authenticated:
            raise PermissionDenied(message="Login is required")
