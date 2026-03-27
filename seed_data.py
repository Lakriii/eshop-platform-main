import os
import django
import random

# Nastavenie Django prostredia
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eshop.settings')
django.setup()

from catalog.models import Category, Product, ProductVariant, Stock
from django.utils.text import slugify

def seed_db():
    print("🚀 Spúšťam generovanie testovacích dát...")

    # 1. Vytvorenie kategórií
    categories_names = ["Elektronika", "Oblečenie", "Domov a záhrada", "Šport"]
    categories = []
    for name in categories_names:
        cat, created = Category.objects.get_or_create(
            name=name,
            defaults={'slug': slugify(name), 'is_active': True}
        )
        categories.append(cat)
        print(f"✅ Kategória: {name}")

    # 2. Vytvorenie produktov
    product_samples = [
        ("iPhone 15 Pro", 1199.00),
        ("MacBook Air M2", 1350.00),
        ("Tričko Cotton Black", 19.99),
        ("Bežecké tenisky", 85.50),
        ("Kávovar Deluxe", 249.00),
        ("Herná myš", 55.00),
    ]

    for name, price in product_samples:
        product, created = Product.objects.get_or_create(
            name=name,
            defaults={
                'slug': slugify(name),
                'price': price,
                'category': random.choice(categories),
                'description': f"Toto je skvelý produkt {name}.",
                'is_active': True
            }
        )
        
        if created:
            # 3. Vytvorenie variantu
            variant = ProductVariant.objects.create(
                product=product,
                sku=f"{slugify(name).upper()}-001",
                price=product.price
            )
            
            # 4. Nastavenie skladu
            Stock.objects.get_or_create(
                variant=variant,
                defaults={'quantity': random.randint(5, 50)}
            )
            print(f"📦 Produkt pridaný: {name}")

    print("\n✨ Hotovo! Skús teraz spustiť server.")

if __name__ == '__main__':
    seed_db()
