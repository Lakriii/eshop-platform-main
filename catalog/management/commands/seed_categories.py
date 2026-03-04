from django.core.management.base import BaseCommand
from catalog.models import Category

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        categories = ['Elektronika', 'Oblečenie', 'Dom a záhrada', 'Šport', 'Knihy']
        for name in categories:
            Category.objects.get_or_create(name=name, slug=name.lower())
        self.stdout.write(self.style.SUCCESS(f'Vytvorených {len(categories)} kategórií.'))