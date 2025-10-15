from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.catalog.models import Category, Product, ProductVariant, Stock, ProductImage
from decimal import Decimal
import random
import os
from django.conf import settings


class Command(BaseCommand):
    help = "Naplní databázu testovacími kategóriami, produktmi, variantmi a priradí im default obrázok z media/products/."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Začínam seedovanie databázy..."))

        # Vyčistenie existujúcich dát
        ProductImage.objects.all().delete()
        Stock.objects.all().delete()
        ProductVariant.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()

        # === DEFAULT IMAGE PATH ===
        default_image_path = os.path.join(settings.MEDIA_ROOT, "products", "default.jpg")

        if not os.path.exists(default_image_path):
            self.stdout.write(self.style.ERROR(f"⚠️ Súbor {default_image_path} neexistuje!"))
            self.stdout.write(self.style.WARNING("Pokračujem bez obrázkov..."))
            default_image_path = None
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ Našiel som default obrázok: {default_image_path}"))

        # === KATEGÓRIE ===
        categories = [
            ("Elektronika", "Moderné zariadenia a príslušenstvo"),
            ("Oblečenie", "Štýlové a pohodlné oblečenie pre každého"),
            ("Domácnosť", "Všetko pre váš domov"),
        ]

        category_objs = [
            Category.objects.create(name=name, slug=slugify(name), description=desc, is_active=True)
            for name, desc in categories
        ]
        self.stdout.write(self.style.SUCCESS(f"✅ Vytvorených {len(category_objs)} kategórií."))

        # === PRODUKTY ===
        products_data = [
            ("Smartfón Galaxy X", "Výkonný smartfón s AMOLED displejom", "Rýchly a štýlový telefón", Decimal("599.99"), category_objs[0]),
            ("Bluetooth slúchadlá", "Bezdrôtové slúchadlá s potlačením hluku", "Perfektný zvuk bez káblov", Decimal("129.99"), category_objs[0]),
            ("Pánske tričko", "Tričko z kvalitnej bavlny", "Pohodlné tričko pre každý deň", Decimal("19.99"), category_objs[1]),
            ("Dámske šaty", "Elegantné šaty vhodné na príležitosť", "Štýlové a moderné", Decimal("49.99"), category_objs[1]),
            ("Kávovar EspressoPro", "Profesionálny kávovar pre domácnosť", "Silná a voňavá káva", Decimal("299.99"), category_objs[2]),
            ("Vysávač TurboClean", "Výkonný bezvreckový vysávač", "Ľahký a tichý chod", Decimal("179.99"), category_objs[2]),
        ]

        product_objs = [
            Product.objects.create(
                name=name,
                slug=slugify(name),
                description=desc,
                short_description=short,
                price=price,
                category=cat,
                is_active=True,
            )
            for name, desc, short, price, cat in products_data
        ]
        self.stdout.write(self.style.SUCCESS(f"✅ Vytvorených {len(product_objs)} produktov."))

        # === PRIPOJENIE DEFAULT OBRAZKU ===
        if default_image_path:
            rel_path = os.path.relpath(default_image_path, settings.MEDIA_ROOT).replace("\\", "/")
            for product in product_objs:
                ProductImage.objects.create(
                    product=product,
                    image=rel_path,
                    alt_text=f"Default image for {product.name}",
                    order=0,
                )
            self.stdout.write(self.style.SUCCESS(f"✅ Default obrázok priradený ku {len(product_objs)} produktom."))
        else:
            self.stdout.write(self.style.WARNING("⚠️ Žiadny default obrázok nebol priradený."))

        # === VARIANTY & SKLAD ===
        for product in product_objs:
            for size in ["S", "M", "L"]:
                sku = f"{slugify(product.name)}-{size}"
                variant = ProductVariant.objects.create(
                    product=product,
                    sku=sku,
                    attributes={"size": size, "color": random.choice(["red", "blue", "black", "white"])},
                    price=product.price + Decimal(random.randint(-10, 20))
                )
                Stock.objects.create(
                    variant=variant,
                    quantity=random.randint(5, 50),
                    reserved=random.randint(0, 3)
                )

        self.stdout.write(self.style.SUCCESS("✅ Varianty a skladové zásoby vytvorené."))
        self.stdout.write(self.style.SUCCESS("🎉 Seedovanie databázy dokončené úspešne!"))
