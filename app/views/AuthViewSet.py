from rest_framework import generics
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from app.serializers import UserRegistrationSerializer

User = get_user_model()

@extend_schema(tags=['Autenticação'])
class RegisterView(generics.CreateAPIView):
    """
    Endpoint público para registo de novos utilizadores no sistema.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer
