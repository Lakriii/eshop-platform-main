from django.core.management.base import BaseCommand
from django.utils.text import slugify
from catalog.models import Category, Product, ProductVariant, Stock
from decimal import Decimal

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Tu už nemažeme (maže seed_all)
        categories = Category.objects.all()
        
        for category in categories:
            for i in range(1, 5):
                # Kľúč k úspechu: Názov obsahuje meno kategórie aj číslo
                # Napr. "Elektronika - Produkt 1"
                product_name = f"{category.name} Produkt {i}"
                product_slug = slugify(product_name)
                
                Product.objects.create(
                    category=category,
                    name=product_name,
                    slug=product_slug,
                    description=f"Skvelý produkt z kategórie {category.name}",
                    price=Decimal("19.99") * i,
                    is_active=True
                )
        
        self.stdout.write(self.style.SUCCESS(f"✅ Produkty úspešne vytvorené."))