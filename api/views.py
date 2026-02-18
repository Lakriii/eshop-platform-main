from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status, viewsets, filters
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django.db.models import Q
# IMPORTY TVOJICH MODELOV - skontroluj, či sa priečinky volajú 'catalog'
from catalog.models import Product 
from catalog.serializers import ProductSerializer 

User = get_user_model()

# --- 1. STRÁNKOVANIE (Pre tisíce produktov) ---
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

# --- 2. PRODUKTY (Verejné, vyhľadávanie, filtrovanie) ---
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    
    # TIETO DVA RIADKY SÚ KĽÚČOVÉ:
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description'] 

    def list(self, request, *args, **kwargs):
        # Ak si prepísala metódu list kvôli "suggestions", 
        # musíš zavolať filter_queryset, inak search parameter nebude fungovať
        queryset = self.filter_queryset(self.get_queryset())
        
        search_query = request.query_params.get('search', None)
        
        # Klasické stránkovanie z DRF
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            response = Response({'results': serializer.data})

        # LOGIKA PRE NÁVRHY (Did you mean)
        if search_query and not response.data['results']:
            suggestions = Product.objects.filter(
                Q(name__icontains=search_query[:3])
            ).filter(is_active=True)[:3]
            
            response.data['suggestions'] = [p.name for p in suggestions]
            response.data['message'] = f"Pre výraz '{search_query}' sme nič nenašli."
        
        return response
# --- 3. PROFIL (Získanie a Úprava mena/hesla) ---
class UserProfileUpdateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "username": user.username,
            "first_name": user.first_name,
            "email": user.email,
            "date_joined": user.date_joined.strftime("%d.%m.%Y")
        })

    def patch(self, request):
        user = request.user
        data = request.data

        if 'first_name' in data:
            user.first_name = data.get('first_name')
        if 'username' in data:
            user.username = data.get('username')
        if 'password' in data:
            user.set_password(data.get('password'))
            
        user.save()
        return Response({"status": "success", "message": "Profil upravený"})

# --- 4. CHECKOUT (Simulácia platby) ---
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def simulate_checkout(request):
    user = request.user
    cart_items = request.data.get('items', [])
    total_price = request.data.get('total_price', 0)

    if not cart_items:
        return Response({"status": "error", "message": "Košík je prázdny"}, status=400)

    # Tu by sa v reálnej appke vytvoril záznam v tabuľke Orders
    print(f"Objednávka od {user.username} v hodnote {total_price}€")

    return Response({
        "status": "success",
        "order_id": 999,
        "message": "Platba úspešná!"
    })

# --- 5. REGISTRÁCIA A TEST ---
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    data = request.data
    username = data.get('username')
    password = data.get('password')
    email = data.get('email', '')

    if not username or not password:
        return Response({"error": "Chýba meno alebo heslo"}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Meno je obsadené"}, status=400)

    User.objects.create_user(username=username, password=password, email=email)
    return Response({"message": "Používateľ vytvorený"}, status=201)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def test_auth(request):
    return Response({"status": "OK", "user": request.user.username})