from django.conf import settings
from django.db import models
from django.urls import reverse


class Product(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image_url = models.CharField(
        max_length=300,
        blank=True,
        help_text="A full image URL (https://...), or a path under static/, e.g. images/products/shoe-1.jpg",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("shop:product_detail", args=[self.pk])

    @property
    def image_src(self):
        """Resolve image_url for use in an <img src>: pass absolute URLs
        through unchanged, treat anything else as a path under STATIC_URL,
        and fall back to None (templates show a placeholder) if unset."""
        if not self.image_url:
            return None
        if self.image_url.startswith(("http://", "https://", "/")):
            return self.image_url
        return f"{settings.STATIC_URL}{self.image_url}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} ({self.user})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=150)  # snapshot at purchase time
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot at purchase time
    quantity = models.PositiveIntegerField(default=1)

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"
