import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from catalog.models import Order, OrderItem, Product

User = get_user_model()

class Command(BaseCommand):
    help = 'Vygeneruje testovacie objednávky pre vývoj profilu'

    def handle(self, *args, **kwargs):
        user = User.objects.filter(is_staff=True).first() or User.objects.first()
        products = list(Product.objects.all())

        if not user or not products:
            self.stdout.write(self.style.ERROR('Musíš mať aspoň jedného užívateľa a produkty v DB!'))
            return

        statuses = ['pending', 'paid', 'shipped', 'delivered']
        
        for i in range(5):
            order = Order.objects.create(
                user=user,
                status=random.choice(statuses),
                is_paid=random.choice([True, False]),
                total_price=0,
                address="Hlavná 10, 811 01 Bratislava"
            )
            
            total = 0
            # Pridáme 1 až 3 náhodné produkty
            for _ in range(random.randint(1, 3)):
                p = random.choice(products)
                qty = random.randint(1, 2)
                item_price = p.price
                OrderItem.objects.create(
                    order=order,
                    product=p,
                    quantity=qty,
                    price=item_price
                )
                total += (item_price * qty)
            
            order.total_price = total
            order.save()

        self.stdout.write(self.style.SUCCESS(f'Vytvorených 5 objednávok pre užívateľa: {user.username}'))