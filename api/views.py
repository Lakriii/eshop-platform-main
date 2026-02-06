from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status

# 1. TESTOVACÍ ENDPOINT (ten, čo ti hádzal chybu)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def test_auth(request):
    return Response({
        "status": "Funguje to!",
        "user": request.user.username,
        "message": "Si úspešne overený cez JWT!"
    })

# 2. PROFIL POUŽÍVATEĽA
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    return Response({
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name
    })

# 3. REGISTRÁCIA
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')

    if not username or not password:
        return Response({"error": "Meno a heslo sú povinné"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Používateľ už existuje"}, status=status.HTTP_400_BAD_REQUEST)

    User.objects.create_user(username=username, password=password, email=email)
    return Response({"message": "Používateľ úspešne vytvorený"}, status=status.HTTP_201_CREATED)