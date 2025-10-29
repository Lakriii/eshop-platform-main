from django.db import models
from django.utils.text import slugify

# -------------------
# Category
# -------------------
class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# -------------------
# Product
# -------------------
class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=512, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

# -------------------
# Product Variant
# -------------------
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    sku = models.CharField(max_length=64, unique=True)
    attributes = models.JSONField(default=dict, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)

    def get_price(self):
        return self.price if self.price is not None else self.product.price

    @property
    def available_stock(self):
        if hasattr(self, "stock") and self.stock:
            return self.stock.available
        return self.stock_quantity

    def __str__(self):
        return f"{self.product.name} - {self.sku}"

# -------------------
# Product Image
# -------------------
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/%Y/%m/%d')
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.product.name}"

# -------------------
# Stock
# -------------------
class Stock(models.Model):
    variant = models.OneToOneField(ProductVariant, related_name='stock', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    reserved = models.IntegerField(default=0)

    @property
    def available(self):
        return max(self.quantity - self.reserved, 0)

    def __str__(self):
        return f"{self.variant} — {self.available} ks dostupné"
