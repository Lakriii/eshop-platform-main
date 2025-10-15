import stripe
from django.conf import settings


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_payment_intent(amount_cents: int, currency='EUR', metadata=None):
    return stripe.PaymentIntent.create(
    amount=amount_cents,
    currency=currency.lower(),
    metadata=metadata or {},
)