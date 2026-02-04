# api/views.py
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication # Pridaj toto
from rest_framework.response import Response

@api_view(['GET'])
@authentication_classes([JWTAuthentication]) # Explicitne povieme, že chceme JWT
@permission_classes([IsAuthenticated])
def test_auth(request):
    return Response({
        "status": "Funguje to!",
        "user": request.user.username,
        "message": "Si úspešne overený!"
    })