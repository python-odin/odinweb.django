"""
OdinWeb.Django API
~~~~~~~~~~~~~~~~~~

Django implementation of the OdinWeb API interface.

"""
from __future__ import absolute_import

from django.conf import settings
from django.conf.urls import url
from django.http import HttpRequest, HttpResponse

from odinweb.containers import ApiInterfaceBase
from odinweb.constants import Type, Method
from odinweb.data_structures import PathNode


TYPE_MAP = {
    Type.String: '[-_.%\w]+',
    Type.Number: r'[.\d]+',
    Type.Integer: r'\d+',
    Type.Boolean: r'0|1|true|false|yes|no|on|off',
    # Type.Array: 'list',
    # Type.File: 'string',
}


class RequestProxy(object):
    def __init__(self, r):
        # type: (HttpRequest) -> None
        self.GET = r.GET
        self.POST = r.POST
        self.headers = r.META
        # self.session = r.
        self.request = r

        try:
            method = Method[r.method]
        except KeyError:
            method = None
        self.method = method

    @property
    def body(self):
        return self.request.body

    @property
    def host(self):
        return self.request.get_host()


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
        # type: (PathNode) -> str
        """
        Format a node to be consumable by the `UrlPath.parse`.
        """
        node_type = TYPE_MAP.get(path_node.type, '\w+')  # Generic string default
        return r"(?P<{}>{})".format(path_node.name, node_type)

    def _bound_callback(self, operation):
        def callback(request, **path_args):
            response = self.dispatch(operation, RequestProxy(request), **path_args)
            django_response = HttpResponse(response.body, response.status)
            for key, value in response.headers.items():
                django_response[key] = value
            return django_response
        return callback

    def urls(self):
        """
        URLs to be integrated into Django url_patterns lists.
        """
        results = []
        for url_path, operation in self.op_paths():
            # Generate path and apply regex wrapping.
            path = r'^{}$'.format(
                url_path.format(self.node_formatter)[1:]
            )

            # Let framework handle unknown method.
            # for method in tuple(m.value for m in operation.methods):
            results.append(url(path, self._bound_callback(operation)))
        return results