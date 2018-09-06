"""
OdinWeb.Django API
~~~~~~~~~~~~~~~~~~

Django implementation of the OdinWeb API interface.

"""
from __future__ import absolute_import

from django.conf import settings
from django.conf.urls import url
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt

from odin.utils import lazy_property
from odinweb.containers import ApiInterfaceBase
from odinweb.constants import Type, Method, PATH_STRING_RE
from odinweb.data_structures import PathParam, BaseHttpRequest


TYPE_MAP = {
    Type.Integer: r'\d+',
    Type.Long: r'\d+',
    Type.Float:  r'[.\d]+',
    Type.Double:  r'[.\d]+',
    Type.String: PATH_STRING_RE,
    Type.Byte: '',
    Type.Binary: '',
    Type.Boolean: r'0|1|true|false|yes|no|on|off',
    Type.Date: r'\d{4}-\d{2}-\d{2}',
    Type.Time: r'\d{2}:\d{2}',
    Type.DateTime: r'[-:\d]+',
    Type.Password: PATH_STRING_RE,
}


class RequestProxy(BaseHttpRequest):
    def __init__(self, r):
        # type: (HttpRequest) -> None
        self.request = r

    @lazy_property
    def environ(self):
        return self.request.META

    @lazy_property
    def method(self):
        try:
            return Method(self.request.method)
        except KeyError:
            pass

    @lazy_property
    def scheme(self):
        return self.request.scheme

    @lazy_property
    def host(self):
        return self.request.get_host()

    @lazy_property
    def path(self):
        return self.request.path

    @lazy_property
    def query(self):
        return self.request.GET

    @lazy_property
    def headers(self):
        return self.request.META

    @lazy_property
    def cookies(self):
        return self.request.COOKIES

    @lazy_property
    def session(self):
        return self.request.scheme

    @lazy_property
    def body(self):
        return self.request.body
    
    @lazy_property
    def form(self):
        return self.request.POST

    @lazy_property
    def content_type(self):
        return self.request.content_type


class Api(ApiInterfaceBase):
    """
    An API base for Django::

        from odinweb.django import Api

        url_patterns = Api(
            ApiVersion(
                UserApi(),
                version='v1
            )
        ).urls()

    """
    def __init__(self, *containers, **options):
        options.setdefault('debug_enabled', settings.DEBUG)
        super(Api, self).__init__(*containers, **options)

    @staticmethod
    def node_formatter(path_node):
        # type: (PathParam) -> str
        """
        Format a node to be consumable by the `UrlPath.parse`.
        """
        if path_node.type == Type.Regex:
            node_type = path_node.type_args  # Regex
        else:
            node_type = TYPE_MAP.get(path_node.type, '\w+')  # Generic string default
        return r"(?P<{}>{})".format(path_node.name, node_type)

    def _bound_callback(self, methods):
        @csrf_exempt
        def callback(request, **path_args):
            request = RequestProxy(request)

            operation = methods.get(request.method)
            if operation:
                # Dispatch request to framework
                response = self.dispatch(operation, request, **path_args)

                # Build Django response
                django_response = HttpResponse(response.body, status=response.status)
                for key, value in response.headers.items():
                    django_response[key] = value
                return django_response

            else:
                return HttpResponseNotAllowed(m.value for m in methods)
        return callback

    def urls(self):
        """
        URLs to be integrated into Django url_patterns lists.
        """
        # Build URLs
        results = []
        for url_path, methods in self.op_paths(collate_methods=True).items():
            # Generate path and apply regex wrapping.
            path = r'^{}$'.format(
                url_path.format(self.node_formatter)[1:]
            )

            # Let framework handle unknown method.
            # for method in tuple(m.value for m in operation.methods):
            results.append(url(path, self._bound_callback(methods)))
        return results
