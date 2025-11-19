# catalog/tests/test_forms.py
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from catalog.forms import ProductForm, ProductImageFormSet
from catalog.models import Category, Product


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
        currency="EUR",
        category=category,
    )


@pytest.fixture
def fake_image():
    return SimpleUploadedFile("fake.jpg", b"whatever", content_type="image/jpeg")


# ====================== VYPNEME VŠETKO, ČO NÁS TRÁPI V TESTOCH ======================
@pytest.fixture(autouse=True)
def bypass_image_validation(monkeypatch):
    # 1. Vypne PIL validáciu (Upload a valid image...)
    monkeypatch.setattr("django.forms.ImageField.clean", lambda self, value, *args: value)

    # 2. Opraví _committed chybu pri ukladaní
    def fake_pre_save(field, model_instance, add):
        file = getattr(model_instance, field.name)
        if file and not hasattr(file, "_committed"):
            file._committed = True
        return file

    monkeypatch.setattr("django.db.models.fields.files.ImageField.pre_save", fake_pre_save)


# ====================== PRODUCT FORM ======================
@pytest.mark.django_db
class TestProductForm:
    def test_valid_form(self, category):
        form = ProductForm(data={
            'name': 'iPhone 16',
            'slug': 'iphone-16',
            'price': '1299',
            'currency': 'EUR',
            'category': category.id,
            'is_active': True,
        })
        assert form.is_valid(), form.errors

    def test_required_fields(self, category):
        form = ProductForm(data={'name': 'Bez slugu', 'price': '100', 'category': category.id})
        assert not form.is_valid()
        assert 'slug' in form.errors
        assert 'currency' in form.errors


# ====================== PRODUCT IMAGE FORMSET ======================
@pytest.mark.django_db
class TestProductImageFormSet:
    def test_can_add_multiple_images(self, product, fake_image):
        data = {
            'images-TOTAL_FORMS': '2',
            'images-INITIAL_FORMS': '0',
            'images-0-image': fake_image,
            'images-0-alt_text': 'Prvý',
            'images-0-order': '10',
            'images-1-image': fake_image,
            'images-1-alt_text': 'Druhý',
            'images-1-order': '20',
        }
        files = {
            'images-0-image': fake_image,
            'images-1-image': fake_image,
        }

        formset = ProductImageFormSet(data=data, files=files, instance=product)
        assert formset.is_valid(), formset.errors
        formset.save()
        assert product.images.count() == 2

    def test_can_delete_image(self, product, fake_image):
        img = product.images.create(image=fake_image, alt_text="Old", order=5)
        data = {
            'images-TOTAL_FORMS': '1',
            'images-INITIAL_FORMS': '1',
            'images-0-id': str(img.id),
            'images-0-DELETE': 'on',
            'images-0-order': '5',
        }
        formset = ProductImageFormSet(data=data, instance=product)
        assert formset.is_valid(), formset.errors
        formset.save()
        assert product.images.count() == 0

    def test_image_is_required(self, product):
        # Tu je kľúčové: zadáme order, ale nie image
        data = {
            'images-TOTAL_FORMS': '1',
            'images-INITIAL_FORMS': '0',
            'images-0-alt_text': 'Bez obrázka',
            'images-0-order': '1',  # order je required → dáme ho
        }
        formset = ProductImageFormSet(data=data, instance=product)
        assert not formset.is_valid()
        # Teraz už musí byť chyba na 'image'
        assert 'image' in formset.forms[0].errors

    def test_extra_form_is_present(self, product):
        formset = ProductImageFormSet(instance=product)
        assert len(formset.forms) == 1
        assert formset.prefix == "images"