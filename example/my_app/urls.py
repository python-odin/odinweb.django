from odinweb.django import Api

from .api import api_v1

urlpatterns = Api(
    api_v1
).urls()
