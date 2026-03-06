import os
import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.core.files import File
from catalog.models import Category, Product, ProductVariant, Stock, ProductImage

class Command(BaseCommand):
    help = "Vymaže staré dáta a naseeduje nové produkty s obrázkami."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("--- Čistím staré dáta z databázy ---"))
        
        # Mazanie v správnom poradí kvôli cudzím kľúčom
        Stock.objects.all().delete()
        ProductVariant.objects.all().delete()
        ProductImage.objects.all().delete()
        Product.objects.all().delete()

        self.stdout.write("Začínam vytvárať produkty...")

        # Získanie kategórií
        categories = list(Category.objects.all())
        if not categories:
            self.stdout.write(self.style.ERROR("Chyba: Žiadne kategórie nenašlo! Spusti najprv seed_categories."))
            return

        # Definícia produktov
        products_data = [
            ("Smartfón Galaxy X", Decimal("599.99"), categories[0]),
            ("Bluetooth slúchadlá", Decimal("129.99"), categories[0]),
            ("Pánske tričko", Decimal("19.99"), categories[1]),
            ("Dámske šaty", Decimal("49.99"), categories[1]),
            ("Kávovar EspressoPro", Decimal("299.99"), categories[2] if len(categories) > 2 else categories[0]),
        ]

        # Cesta k tvojmu lokálnemu obrázku
        image_source_path = "/Users/jasha/Documents/GitHub/eshop-platform-main/media/products/default.jpg"

        for name, price, cat in products_data:
            # 1. Vytvorenie produktu
            product = Product.objects.create(
                name=name,
                slug=slugify(name),
                description=f"Skvelý {name}. Tento produkt bol automaticky vygenerovaný pre testovacie účely.",
                short_description=f"Krátky popis pre {name}",
                price=price,
                category=cat,
                is_active=True
            )
            
            # 2. Vytvorenie variantu (predpokladáme, že SKU musí byť unikátne)
            variant = ProductVariant.objects.create(
                product=product,
                sku=f"{slugify(name)}-{random.randint(100, 999)}",
                price=price
            )
            
            # 3. Vytvorenie skladu
            Stock.objects.create(
                variant=variant, 
                quantity=random.randint(5, 100)
            )

            # 4. SEEDOVANIE OBRÁZKA
            if os.path.exists(image_source_path):
                with open(image_source_path, 'rb') as f:
                    django_file = File(f, name=os.path.basename(image_source_path))
                    ProductImage.objects.create(
                        product=product,
                        image=django_file,
                        # is_main=True  # Odkomentuj, ak máš v modeli pole pre hlavný obrázok
                    )
                self.stdout.write(f"Vytvorený produkt: {name} (s obrázkom)")
            else:
                self.stdout.write(self.style.ERROR(f"Vytvorený produkt: {name} (OBRÁZOK NENÁJDENÝ: {image_source_path})"))

        self.stdout.write(self.style.SUCCESS("\n🎉 Všetky produkty boli úspešne naseedované!"))