import os
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.core.files import File
from catalog.models import Category, Product, ProductVariant, Stock, ProductImage

class Command(BaseCommand):
    help = "Vymaže staré dáta a naseeduje nové produkty s kompletnými variantmi, skladom a obrázkami."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("--- Čistím staré produktové dáta ---"))
        
        # Mazanie v správnom poradí kvôli cudzím kľúčom (Foreign Keys)
        # Sklad a Obrázky musia ísť prvé, potom Varianty, nakoniec Produkty
        Stock.objects.all().delete()
        ProductImage.objects.all().delete()
        ProductVariant.objects.all().delete()
        Product.objects.all().delete()

        self.stdout.write("Začínam vytvárať produkty...")

        # 1. Získanie existujúcich kategórií (predpokladá sa, že seed_categories už bežal)
        categories = list(Category.objects.all())
        if not categories:
            self.stdout.write(self.style.ERROR("❌ Chyba: Žiadne kategórie nenašlo! Spusti najprv: python3 manage.py seed_categories"))
            return

        # 2. Definícia testovacích dát (Názov, Cena, Index kategórie)
        products_data = [
            ("Smartfón Galaxy X", Decimal("599.99"), categories[0]),
            ("Bluetooth slúchadlá", Decimal("129.99"), categories[0]),
            ("Pánske tričko", Decimal("19.99"), categories[1] if len(categories) > 1 else categories[0]),
            ("Dámske šaty", Decimal("49.99"), categories[1] if len(categories) > 1 else categories[0]),
            ("Kávovar EspressoPro", Decimal("299.99"), categories[2] if len(categories) > 2 else categories[0]),
        ]

        # 3. Cesta k tvojmu lokálnemu obrázku na Macu
        image_source_path = "/Users/jasha/Documents/GitHub/eshop-platform-main/media/products/default.jpg"

        for name, base_price, cat in products_data:
            # --- VYTVORENIE PRODUKTU ---
            product = Product.objects.create(
                name=name,
                slug=slugify(name),
                description=f"Skvelý {name}. Tento produkt bol automaticky vygenerovaný pre testovacie účely.",
                short_description=f"Krátky popis pre {name}",
                price=base_price,
                category=cat,
                is_active=True
            )
            
            # --- VYTVORENIE VARIANTOV (Napr. farby/veľkosti) ---
            # Vytvoríme 2 varianty pre každý produkt, aby sme videli pole v API
            variants_to_create = ["Základná verzia", "Limitovaná edícia"]
            
            for i, var_name in enumerate(variants_to_create):
                # SKU musí byť unikátne
                sku_code = f"{product.slug[:5].upper()}-{random.randint(1000, 9999)}-{i}"
                
                variant = ProductVariant.objects.create(
                    product=product,
                    sku=sku_code,
                    price=base_price + Decimal(i * 10), # Druhý variant je o 10 EUR drahší
                    attributes={"label": var_name}
                )
                
                # --- VYTVORENIE SKLADU PRE KAŽDÝ VARIANT ---
                # Toto zabezpečí, že stock_quantity v API nebude 0
                Stock.objects.create(
                    variant=variant, 
                    quantity=random.randint(10, 100),
                    reserved=0
                )

            # --- SEEDOVANIE OBRÁZKA K PRODUKTU ---
            if os.path.exists(image_source_path):
                with open(image_source_path, 'rb') as f:
                    django_file = File(f, name=f"{product.slug}.jpg")
                    ProductImage.objects.create(
                        product=product,
                        image=django_file,
                        is_main=True,
                        alt_text=f"Hlavný obrázok pre {product.name}"
                    )
                self.stdout.write(self.style.SUCCESS(f"✅ Vytvorený: {name} (Varianty: 2, Obrázok: ÁNO)"))
            else:
                self.stdout.write(self.style.ERROR(f"⚠️ Vytvorený: {name} (OBRÁZOK NENÁJDENÝ na ceste: {image_source_path})"))

        self.stdout.write(self.style.SUCCESS("\n🎉 Všetky produkty s variantmi a skladom boli úspešne naseedované!"))