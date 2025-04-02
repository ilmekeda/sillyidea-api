'''
Views for the user API
'''
from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)

from rest_framework import authentication, generics, permissions
from rest_framework.authtoken.views import ObtainAuthToken as ObtainAuthTokenView  # noqa
from rest_framework.settings import api_settings


class CreateUserView(generics.CreateAPIView):
    '''Create a new endpoint user in the system'''
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthTokenView):
    '''Create a new authentication token for endpoint user'''
    serializer_class = AuthTokenSerializer
    # following is an odd exception needed for swagger, uncommon
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    '''Manage the authenticated endpoint used'''
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]  # authentication # noqa
    permission_classes = [permissions.IsAuthenticated]  # authorization

    def get_object(self):
        '''Retrieve and return the authenticated endpoint user'''
        return self.request.user
