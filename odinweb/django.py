"""
OdinWeb.Django API
~~~~~~~~~~~~~~~~~~

Django implementation of the OdinWeb API interface.

"""
from __future__ import absolute_import

from django.conf.urls import url
from django.http import HttpRequest

from odinweb.containers import ApiInterfaceBase
from odinweb.constants import Type, Method
from odinweb.data_structures import PathNode


# TYPE_MAP = {
#     Type.String: 'string',
#     Type.Number: 'number',
#     Type.Integer: 'int',
#     Type.Boolean: 'bool',
#     # Type.Array: 'list',
#     # Type.File: 'string',
# }


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


class ApiUrls(ApiInterfaceBase):
    """
    A Flask Blueprint for an API::

        from flask import Flask
        from odinweb.flask.api import ApiBlueprint

        app = Flask(__name__)

        app.register_blueprint(
            ApiBlueprint(
                ApiVersion(
                    UserApi(),
                    version='v1
                )
            )
        )

    """
    _got_registered_once = False

    def __init__(self, *containers, **options):
        self.subdomain = options.pop('subdomain', None)
        super(ApiBlueprint, self).__init__(*containers, **options)

    @staticmethod
    def node_formatter(path_node):
        # type: (PathNode) -> str
        """
        Format a node to be consumable by the `UrlPath.parse`.
        """
        if path_node.type:
            node_type = TYPE_MAP.get(path_node.type, 'str')
            if path_node.type_args:
                return "<{}({}):{}>".format(node_type, ', '.join(path_node.type_args), path_node.name)
            return "<{}:{}>".format(node_type, path_node.name)
        return "<{}>".format(path_node.name)

    def _bound_callback(self, operation):
        def callback(**path_args):
            response = self.dispatch(operation, RequestProxy(request), **path_args)
            return make_response(response.body or ' ', response.status, response.headers)
        return callback

    def register(self, app, options, first_registration):
        # type: (Flask, dict, bool) -> None
        """
        Register interface

        :param app: Instance of flask.
        :param options: Options for blueprint
        :param first_registration: First registration of blueprint

        """
        self._got_registered_once = True
        state = ApiBlueprintSetupState(self, app, options, first_registration)

        for url_path, operation in self.op_paths():
            path = url_path.format(self.node_formatter)
            methods = tuple(m.value for m in operation.methods)
            state.add_url_rule(path, operation.operation_id, self._bound_callback(operation), methods=methods)
