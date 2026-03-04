from django.core.management.base import BaseCommand
from django.utils.text import slugify
from catalog.models import Category, Product, ProductVariant, Stock, ProductImage
from decimal import Decimal
import random

class Command(BaseCommand):
    help = "Vymaže staré dáta a naseeduje nové produkty."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Čistím staré dáta z databázy..."))
        
        # Dôležité: Mažeme v poradí od potomkov k rodičom
        Stock.objects.all().delete()
        ProductVariant.objects.all().delete()
        ProductImage.objects.all().delete()
        Product.objects.all().delete()
        # Category nemažeme tu, ak ich seeduješ v inom súbore, 
        # alebo ich vymaž aj tu, ak chceš úplne čistý štít:
        # Category.objects.all().delete()

        self.stdout.write("Začínam vytvárať produkty...")

        # Získame kategórie (predpokladáme, že už existujú zo seed_categories)
        categories = list(Category.objects.all())
        if not categories:
            self.stdout.write(self.style.ERROR("Žiadne kategórie nenašlo! Spusti najprv seed_categories."))
            return

        # Dáta pre seed
        products_data = [
            ("Smartfón Galaxy X", Decimal("599.99"), categories[0]),
            ("Bluetooth slúchadlá", Decimal("129.99"), categories[0]),
            ("Pánske tričko", Decimal("19.99"), categories[1]),
            ("Dámske šaty", Decimal("49.99"), categories[1]),
            ("Kávovar EspressoPro", Decimal("299.99"), categories[2] if len(categories) > 2 else categories[0]),
        ]

        for name, price, cat in products_data:
            product = Product.objects.create(
                name=name,
                slug=slugify(name),
                description=f"Skvelý {name}",
                short_description="Krátky popis produktu",
                price=price,
                category=cat,
                is_active=True
            )
            
            # Vytvoríme variant pre produkt, aby to nebolo prázdne
            variant = ProductVariant.objects.create(
                product=product,
                sku=f"{slugify(name)}-DEF",
                price=price
            )
            
            Stock.objects.create(variant=variant, quantity=random.randint(1, 50))

        self.stdout.write(self.style.SUCCESS("🎉 Produkty úspešne naseedované!"))