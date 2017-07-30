from odinweb.django import Api
from odinweb.django.api.middleware import LoginRequired

from .api import api_v1

urlpatterns = Api(
    api_v1,
    middleware=[LoginRequired()]
).urls()
