from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status, viewsets, filters
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter, BooleanFilter
from catalog.models import Product
from catalog.serializers import ProductSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

User = get_user_model()

# --- Custom Token Auth Endpoint ---
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username
        })


# --- Pagination ---
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# --- Filters ---
class ProductFilter(FilterSet):
    min_price = NumberFilter(field_name="price", lookup_expr='gte')
    max_price = NumberFilter(field_name="price", lookup_expr='lte')
    category = NumberFilter(field_name="category_id")
    in_stock = BooleanFilter(method='filter_in_stock')

    class Meta:
        model = Product
        fields = ['category', 'min_price', 'max_price']

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(variants__stock__quantity__gt=0).distinct()
        return queryset


# --- Product ViewSet ---
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'id']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        search_query = request.query_params.get('search', None)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            response = Response({'results': serializer.data})

        # "Did you mean" suggestions ak nenájde výsledky
        if search_query and not response.data['results']:
            suggestions = Product.objects.filter(
                Q(name__icontains=search_query[:3]), is_active=True
            ).distinct()[:3]
            response.data['suggestions'] = [p.name for p in suggestions]
            response.data['message'] = f"Pre výraz '{search_query}' sme nič nenašli."
        return response


# --- User Profile ---
class UserProfileUpdateView(APIView):
    authentication_classes = [TokenAuthentication]
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


# --- Checkout Simulation (Public) ---
@api_view(['POST'])
@permission_classes([AllowAny])
def simulate_checkout(request):
    user = request.user if request.user.is_authenticated else None
    cart_items = request.data.get('items', [])
    total_price = request.data.get('total_price', 0)

    if not cart_items:
        return Response({"status": "error", "message": "Košík je prázdny"}, status=400)

    if user:
        print(f"DEBUG: Objednávka od {user.username} v hodnote {total_price}€ prijatá.")
    else:
        print(f"DEBUG: Verejná objednávka v hodnote {total_price}€ prijatá.")

    return Response({
        "status": "success",
        "order_id": 999,
        "message": "Platba úspešná!"
    })


# --- Register User ---
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


# --- Test Auth ---
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_auth(request):
    return Response({"status": "OK", "user": request.user.username})