from django.core.management import call_command
from django.core.management.base import BaseCommand
from catalog.models import Category, Product, ProductVariant, Stock, ProductImage

class Command(BaseCommand):
    help = 'Úplne vymaže databázu a spustí všetky seed skripty'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('⚠️ MAŽEM CELÚ DATABÁZU...'))

        # 1. KROK: Vymazanie všetkého v správnom poradí (od potomkov k rodičom)
        # Týmto sa vyhneš chybám s cudzími kľúčmi a unikátnymi slugmi
        ProductImage.objects.all().delete()
        Stock.objects.all().delete()
        ProductVariant.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('✅ Databáza je prázdna.'))

        # 2. KROK: Spustenie tvojich seed skriptov
        self.stdout.write('Spúšťam opätovné napĺňanie dát...')
        
        try:
            call_command('seed_categories')
            call_command('seed_products')
            self.stdout.write(self.style.SUCCESS('🎉 Všetko bolo úspešne naseedované od nuly!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Chyba počas seedovania: {e}'))