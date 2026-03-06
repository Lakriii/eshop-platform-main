from django.core.management import call_command
from django.core.management.base import BaseCommand
from catalog.models import Category, Product, ProductVariant, Stock, ProductImage

class Command(BaseCommand):
    help = 'Úplne vymaže databázu a spustí všetky seed skripty v správnom poradí'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('⚠️ MAŽEM CELÚ DATABÁZU...'))

        # Mazanie od potomkov k rodičom (Foreign Key safe)
        Stock.objects.all().delete()
        ProductImage.objects.all().delete()
        ProductVariant.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('✅ Databáza je prázdna.'))

        try:
            # 1. Najprv kategórie (inak produkty nebudú mať kam patriť)
            self.stdout.write('Krok 1: Seedujem kategórie...')
            call_command('seed_categories')
            
            # 2. Potom produkty (ktoré vytvoria aj VARIANTY a OBRÁZKY)
            self.stdout.write('Krok 2: Seedujem produkty s variantmi a obrázkami...')
            call_command('seed_products') # Použi ten skript, ktorý má v sebe logiku pre obrázky
            
            self.stdout.write(self.style.SUCCESS('🎉 Všetko bolo úspešne naseedované!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Chyba počas seedovania: {e}'))