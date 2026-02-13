from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
# Namiesto from django.contrib.auth.models import User daj:
from django.contrib.auth import get_user_model
User = get_user_model()

# ----------------------------------------------------------------
# 1. TESTOVACÍ ENDPOINT (Overenie tokenu a spojenia)
# ----------------------------------------------------------------
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def test_auth(request):
    """
    Slúži na rýchle overenie, či tvoj JWT token z Macu funguje
    a či sa Mac vie spojiť s Windowsom.
    """
    return Response({
        "status": "Funguje to!",
        "user": request.user.username,
        "message": "Si úspešne overený cez JWT!"
    })

# ----------------------------------------------------------------
# 2. PROFIL POUŽÍVATEĽA (S upravenými kľúčmi pre tvoj Swift model)
# ----------------------------------------------------------------
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Vráti detailné informácie o prihlásenom používateľovi.
    Kľúče sú upravené tak, aby si ich videla v Swift debug okne.
    """
    user = request.user
    return Response({
        "prihlasovacie_meno": user.username,
        "emailova_adresa": user.email,
        "je_aktivny": user.is_active,
        "datum_pripojenia": user.date_joined.strftime("%d.%m.%Y")
    })

# ----------------------------------------------------------------
# 3. REGISTRÁCIA NOVÉHO POUŽÍVATEĽA
# ----------------------------------------------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Umožní vytvoriť nového používateľa cez POST požiadavku.
    """
    data = request.data
    username = data.get('username')
    password = data.get('password')
    email = data.get('email', '')

    # Základná validácia dát
    if not username or not password:
        return Response(
            {"error": "Meno a heslo sú povinné"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Kontrola, či meno už nie je obsadené
    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Používateľ s týmto menom už existuje"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Samotné vytvorenie používateľa v databáze
    try:
        User.objects.create_user(
            username=username, 
            password=password, 
            email=email
        )
        return Response(
            {"message": "Používateľ úspešne vytvorený"}, 
            status=status.HTTP_201_CREATED
        )
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )