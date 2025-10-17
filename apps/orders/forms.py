# apps/orders/forms.py
from django import forms

class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=255, label="Full Name")
    email = forms.EmailField(label="Email")
    phone = forms.CharField(max_length=20, label="Phone")
    billing_address = forms.CharField(widget=forms.Textarea, label="Billing Address")
    shipping_address = forms.CharField(widget=forms.Textarea, label="Shipping Address")
