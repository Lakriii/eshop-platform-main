import os
from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subcategories'
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=512, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL, related_name='products'
    )
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def in_stock(self):
        return any(v.stock.quantity > 0 for v in self.variants.all() if hasattr(v, 'stock'))

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    sku = models.CharField(max_length=64, unique=True)
    attributes = models.JSONField(default=dict, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    @property
    def stock_quantity(self):
        if hasattr(self, 'stock'):
            return self.stock.quantity
        return 0

    def __str__(self):
        return f"{self.product.name} ({self.sku})"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/%Y/%m/%d')
    alt_text = models.CharField(max_length=255, blank=True)
    is_main = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-is_main']

class Stock(models.Model):
    variant = models.OneToOneField(ProductVariant, related_name='stock', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    reserved = models.PositiveIntegerField(default=0)

    @property
    def available(self):
        return max(self.quantity - self.reserved, 0)