from django.utils.text import slugify
import uuid
from rest_framework.test import APITestCase
from rest_framework import status
from catalog.models import Product, Category, ProductVariant

class ProductTests(APITestCase):

    def setUp(self):
        # -------------------------
        # Kategórie
        # -------------------------
        self.cat_electronics = Category.objects.create(name="Electronics", slug="electronics")
        self.cat_clothes = Category.objects.create(name="Clothes", slug="clothes")

        # -------------------------
        # Produkty
        # -------------------------
        self.product1 = Product.objects.create(
            name="Cheap Phone",
            slug=slugify("Cheap Phone") + "-" + str(uuid.uuid4())[:8],
            price=50,
            in_stock=True,
            category=self.cat_electronics
        )
        self.product2 = Product.objects.create(
            name="Expensive Phone",
            slug=slugify("Expensive Phone") + "-" + str(uuid.uuid4())[:8],
            price=500,
            in_stock=True,
            category=self.cat_electronics
        )
        self.product3 = Product.objects.create(
            name="Shirt",
            slug=slugify("Shirt") + "-" + str(uuid.uuid4())[:8],
            price=20,
            in_stock=False,
            category=self.cat_clothes
        )
        self.product4 = Product.objects.create(
            name="Jeans",
            slug=slugify("Jeans") + "-" + str(uuid.uuid4())[:8],
            price=80,
            in_stock=True,
            category=self.cat_clothes
        )

        # -------------------------
        # Variants
        # -------------------------
        self.variant1 = ProductVariant.objects.create(
            product=self.product1,
            sku="CHEAP-PHONE-001",
            price=55,
            stock_quantity=10
        )
        self.variant2 = ProductVariant.objects.create(
            product=self.product4,
            sku="JEANS-001",
            price=85,
            stock_quantity=0
        )

    # -------------------------
    # Produkty dostupné aj bez prihlásenia
    # -------------------------
    def test_products_list_public(self):
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 4)

    # -------------------------
    # Filtery
    # -------------------------
    def test_filter_by_min_price(self):
        response = self.client.get("/api/products/?min_price=100")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for p in response.data['results']:
            self.assertTrue(float(p['price']) >= 100)

    def test_filter_by_max_price(self):
        response = self.client.get("/api/products/?max_price=50")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for p in response.data['results']:
            self.assertTrue(float(p['price']) <= 50)

    def test_filter_in_stock(self):
        response = self.client.get("/api/products/?in_stock=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for p in response.data['results']:
            self.assertTrue(p['in_stock'])

    def test_filter_by_category(self):
        response = self.client.get(f"/api/products/?category={self.cat_clothes.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for p in response.data['results']:
            self.assertEqual(p['category_name'], self.cat_clothes.name)

    # -------------------------
    # Search
    # -------------------------
    def test_search_returns_correct_results(self):
        response = self.client.get("/api/products/?search=Cheap")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(p["name"] == "Cheap Phone" for p in response.data['results']))

    # -------------------------
    # Check variants included
    # -------------------------
    def test_variants_present(self):
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        found_variant = False
        for p in response.data['results']:
            if p['variants']:
                found_variant = True
        self.assertTrue(found_variant)

    # -------------------------
    # Fake checkout / simulácia platby
    # -------------------------
    def test_simulate_checkout_public(self):
        # Verejná cesta – nemusí byť prihlásený
        items = [{"product_id": self.product1.id, "quantity": 1}]
        total_price = 50

        response = self.client.post("/api/checkout/simulate/", {
            "items": items,
            "total_price": total_price
        }, format='json')

        # Očakávame úspech – fake payment
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertIn("order_id", response.data)
        self.assertIn("message", response.data)