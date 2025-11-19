# catalog/tests/test_models.py
import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from catalog.models import Category, Product, ProductVariant, ProductImage, Stock


# ====================== FIXTURES ======================
@pytest.fixture
def category():
    return Category.objects.create(name="Electronics", slug="electronics")


@pytest.fixture
def product(category):
    return Product.objects.create(
        name="Super Phone",
        slug="super-phone",
        price=999,
        category=category,
    )


# ====================== CATEGORY ======================
@pytest.mark.django_db
class TestCategory:
    def test_name_max_length_is_200(self):
        Category(name="A" * 200, slug="ok").full_clean()  # OK
        with pytest.raises(ValidationError):
            Category(name="A" * 201, slug="bad").full_clean()

    def test_slug_is_auto_generated_when_blank(self):
        cat = Category.objects.create(name="Gaming PCs", slug="")
        assert cat.slug == "gaming-pcs"   # ← funguje

    def test_slug_is_not_changed_when_provided(self):
        cat = Category.objects.create(name="Laptops", slug="my-custom-slug")
        assert cat.slug == "my-custom-slug"

    def test_str_returns_name(self):
        cat = Category.objects.create(name="Accessories", slug="acc")
        assert str(cat) == "Accessories"


# ====================== PRODUCT ======================
@pytest.mark.django_db
class TestProduct:
    def test_requires_price(self, category):
        with pytest.raises(IntegrityError):
            Product.objects.create(name="iPhone", category=category)

    def test_slug_can_be_blank_or_manual(self, category):
        # Tvoj Product NEMÁ auto-slug → musíš ho dať ručne alebo nechať prázdny
        product = Product.objects.create(
            name="iPhone 15",
            price=1200,
            slug="",
            category=category
        )
        assert product.slug == ""  # ← očakávané správanie

    def test_str_returns_name(self, category):
        product = Product.objects.create(name="MacBook Pro", price=1500, category=category)
        assert str(product) == "MacBook Pro"


# ====================== PRODUCT VARIANT ======================
@pytest.mark.django_db
class TestProductVariant:
    def test_get_price_uses_variant_price_when_set(self, product):
        variant = ProductVariant.objects.create(product=product, sku="XYZ", price=899)
        assert variant.get_price() == 899

    def test_get_price_falls_back_to_product_price(self, product):
        variant = ProductVariant.objects.create(product=product, sku="ABC")
        assert variant.get_price() == 999

    def test_available_stock_uses_stock_object(self, product):
        variant = ProductVariant.objects.create(product=product, sku="TEST")
        Stock.objects.create(variant=variant, quantity=20, reserved=5)
        assert variant.available_stock == 15

    def test_available_stock_falls_back_to_stock_quantity(self, product):
        variant = ProductVariant.objects.create(product=product, sku="TEST2", stock_quantity=8)
        assert variant.available_stock == 8

    def test_str_shows_product_and_sku(self, product):
        variant = ProductVariant.objects.create(product=product, sku="RED-256")
        assert str(variant) == "Super Phone - RED-256"


# ====================== PRODUCT IMAGE ======================
@pytest.mark.django_db
class TestProductImage:
    def test_str(self, product):
        img = ProductImage.objects.create(
            product=product,
            image=SimpleUploadedFile("test.jpg", b"fake")
        )
        assert str(img) == "Image for Super Phone"

    def test_ordering_by_order_field(self, product):
        img2 = ProductImage.objects.create(product=product, image=SimpleUploadedFile("a.jpg", b""), order=2)
        img1 = ProductImage.objects.create(product=product, image=SimpleUploadedFile("b.jpg", b""), order=1)
        assert list(product.images.all())[:2] == [img1, img2]


# ====================== STOCK ======================
@pytest.mark.django_db
class TestStock:
    def test_available_never_negative(self, product):
        variant = ProductVariant.objects.create(product=product, sku="X")
        stock = Stock.objects.create(variant=variant, quantity=5, reserved=10)
        assert stock.available == 0

    def test_str(self, product):
        variant = ProductVariant.objects.create(product=product, sku="CHAIR-01")
        stock = Stock.objects.create(variant=variant, quantity=25, reserved=7)
        assert str(stock) == "Super Phone - CHAIR-01 — 18 ks dostupné"

    def test_one_stock_per_variant_constraint(self, product):
        variant = ProductVariant.objects.create(product=product, sku="UNIQUE")
        Stock.objects.create(variant=variant, quantity=10)
        with pytest.raises(IntegrityError):
            Stock.objects.create(variant=variant, quantity=5)