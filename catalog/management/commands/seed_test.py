# catalog/management/commands/seed_test.py
import os
from django.core.management.base import BaseCommand
from django.core.files import File
from catalog.models import Product, ProductVariant, Stock, ProductImage

class Command(BaseCommand):
    def handle(self, *args, **options):
        img_path = "/Users/jasha/Documents/GitHub/eshop-platform-main/media/products/default.jpg"
        
        # Vymažeme všetko, aby sme začali na čisto
        Product.objects.all().delete()
        
        p = Product.objects.create(name="MacBook Air", price=1200)
        
        # Vytvoríme variant
        v = ProductVariant.objects.create(product=p, sku="MAC-AIR-01", price=1200)
        Stock.objects.create(variant=v, quantity=5)
        
        # Vytvoríme obrázok
        if os.path.exists(img_path):
            with open(img_path, 'rb') as f:
                ProductImage.objects.create(product=p, image=File(f, name="test.jpg"))
            self.stdout.write("Hotovo: Produkt s variantom a obrázkom je v DB!")
        else:
            self.stdout.write("CHYBA: Obrázok na disku neexistuje!")