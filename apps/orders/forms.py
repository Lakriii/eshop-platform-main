from django import forms
from django.core.validators import RegexValidator, EmailValidator
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Fieldset

phone_validator = RegexValidator(
    regex=r'^\+?\d{7,15}$',
    message="Telefónne číslo musí obsahovať len čísla a môže začínať +, dĺžka 7-15 číslic."
)

postcode_validator = RegexValidator(
    regex=r'^\d{3,10}$',
    message="PSČ musí obsahovať 3-10 číslic."
)

class CheckoutForm(forms.Form):
    full_name = forms.CharField(label="Meno a priezvisko", max_length=100)
    email = forms.EmailField(label="E-mail", validators=[EmailValidator(message="Neplatný e-mail.")])
    phone = forms.CharField(label="Telefónne číslo", max_length=20, validators=[phone_validator])
    
    billing_street = forms.CharField(label="Ulica a číslo", max_length=150)
    billing_city = forms.CharField(label="Mesto", max_length=100)
    billing_postcode = forms.CharField(label="PSČ", max_length=10, validators=[postcode_validator])
    billing_country = forms.CharField(label="Štát", max_length=100)
    
    shipping_street = forms.CharField(label="Ulica a číslo", max_length=150)
    shipping_city = forms.CharField(label="Mesto", max_length=100)
    shipping_postcode = forms.CharField(label="PSČ", max_length=10, validators=[postcode_validator])
    shipping_country = forms.CharField(label="Štát", max_length=100)
    
    coupon_code = forms.CharField(
        label="Kupón (ak máte)", max_length=50, required=False,
        help_text="Zadajte kód kupónu pre zľavu (voliteľné)."
    )
    
    # Nové pole: použiť body
    use_loyalty_points = forms.BooleanField(
        label="Chcem použiť moje vernostné body na zľavu",
        required=False
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user  # prístup k aktuálnemu používateľovi
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Fieldset(
                "🧍‍ Osobné údaje",
                Row(
                    Column("full_name", css_class="col-md-6"),
                    Column("email", css_class="col-md-6"),
                ),
                Row(Column("phone", css_class="col-md-6")),
            ),
            Fieldset(
                "🧾 Fakturačná adresa",
                Row(
                    Column("billing_street", css_class="col-md-6"),
                    Column("billing_city", css_class="col-md-6"),
                ),
                Row(
                    Column("billing_postcode", css_class="col-md-3"),
                    Column("billing_country", css_class="col-md-3"),
                ),
            ),
            Fieldset(
                "📦 Doručovacia adresa",
                Row(
                    Column("shipping_street", css_class="col-md-6"),
                    Column("shipping_city", css_class="col-md-6"),
                ),
                Row(
                    Column("shipping_postcode", css_class="col-md-3"),
                    Column("shipping_country", css_class="col-md-3"),
                ),
            ),
            Fieldset(
                "🎟️ Kupón",
                Row(Column("coupon_code", css_class="col-md-6")),
            ),
            Fieldset(
                "💎 Vernostné body",
                Row(Column("use_loyalty_points", css_class="col-md-6")),
            ),
            Submit("submit", "Uložiť a prejsť k platbe", css_class="btn btn-success btn-lg mt-3 w-100")
        )

    def get_loyalty_discount(self):
        """Vypočíta % zľavu podľa vernostných bodov"""
        if self.cleaned_data.get("use_loyalty_points") and self.user and hasattr(self.user, "profile"):
            points = self.user.profile.loyalty_points
            discount = points * 0.1  # 1 bod = 0.1 %
            return min(discount, 20)  # max 20 %
        return 0
