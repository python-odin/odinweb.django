import odin

from odinweb import api, doc
from odinweb.django.api.models import ModelResourceApi, Listing, Create, Detail, Update, Delete
from odinweb.swagger import SwaggerSpec

from my_app.models import Group


class User(odin.Resource):
    """
    User resource
    """
    id = odin.IntegerField()
    username = odin.StringField()
    name = odin.StringField()
    email = odin.EmailField()
    role = odin.StringField(choices=('a', 'b', 'c'))

USERS = [
    User(1, 'pimpstar24', 'Bender', 'Rodreges', 'bender@ilovebender.com'),
    User(2, 'zoidberg', 'Zoidberg', '', 'zoidberg@freemail.web'),
    User(3, 'amylove79', 'Amy', 'Wong', 'awong79@marslink.web'),
]
USER_ID = len(USERS)


class UserApi(api.ResourceApi):
    resource = User
    tags = ['user']

    @doc.deprecated
    @api.collection(path='find', methods=api.Method.POST)
    def operation_test(self, request):
        pass

    @api.listing
    def get_user_list(self, request, offset, limit):
        return USERS[offset:offset+limit], len(USERS)

    @api.create
    def create_user(self, request, user):
        global USER_ID

        # Add user to list
        USER_ID += 1
        user.id = USER_ID
        USERS.append(user)

        return user

    @api.detail
    def get_user(self, request, resource_id):
        """
        Get a user object
        """
        for user in USERS:
            if user.id == resource_id:
                return user

        raise api.HttpError(api.HTTPStatus.NOT_FOUND)

    @api.update
    def update_user(self, request, user, resource_id):
        return user

    @api.patch
    def patch_user(self, request, user, resource_id):
        return user

    @api.delete
    def delete_user(self, request, resource_id):
        for idx, user in enumerate(USERS):
            if user.id == resource_id:
                USERS.remove(user)
                return

        raise api.HttpError(api.HTTPStatus.NOT_FOUND)


class GroupApi(Listing, Create, Detail, Update, Delete, ModelResourceApi):
    """
    Endpoint to managing groups.
    """
    model = Group
    tags = ['group']


sample_api = api.ApiCollection(name='sample')


@sample_api.operation('foo/bar')
def sample(request):
    return {}


api_v1 = api.ApiVersion(
    SwaggerSpec("Flask Example Swaggerspec", enable_ui=True),
    sample_api,
    UserApi(),
    GroupApi(),
)
