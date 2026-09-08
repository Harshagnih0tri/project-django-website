from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from shop.models import Product


class Command(BaseCommand):
    help = "Creates a demo admin user and a catalog of sample products if none exist yet."

    def handle(self, *args, **options):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin12345")
            self.stdout.write(self.style.SUCCESS("Created demo admin: admin / admin12345"))
        else:
            self.stdout.write("Demo admin already exists.")

        if Product.objects.count() == 0:
            Product.objects.bulk_create([
                Product(
                    name="Wireless Mouse",
                    description="Ergonomic 2.4GHz wireless mouse with a 1600 DPI sensor.",
                    price=799, stock=25,
                ),
                Product(
                    name="Mechanical Keyboard",
                    description="Hot-swappable mechanical keyboard, blue switches, RGB backlight.",
                    price=3499, stock=15,
                ),
                Product(
                    name="USB-C Hub",
                    description="7-in-1 USB-C hub with HDMI, ethernet, and an SD card reader.",
                    price=1899, stock=30,
                ),
                Product(
                    name="Running Shoes",
                    description="Lightweight running shoes with breathable mesh upper and cushioned sole.",
                    price=2499, stock=40, image_url="images/products/shoe-1.jpg",
                ),
                Product(
                    name="Canvas Sneakers",
                    description="Everyday canvas sneakers, unisex fit, machine washable.",
                    price=1799, stock=35, image_url="images/products/shoe-2.jpg",
                ),
                Product(
                    name="Men's Bomber Jacket",
                    description="Water-resistant bomber jacket with ribbed cuffs, built for layering.",
                    price=3299, stock=18, image_url="images/products/jacket-1.jpg",
                ),
                Product(
                    name="Denim Jacket",
                    description="Classic washed-denim jacket with button-front closure.",
                    price=2899, stock=20, image_url="images/products/jacket-3.jpg",
                ),
                Product(
                    name="Analog Wrist Watch",
                    description="Stainless steel analog watch, 5 ATM water resistance.",
                    price=1999, stock=22, image_url="images/products/watch-1.jpg",
                ),
                Product(
                    name="Chronograph Watch",
                    description="Multi-dial chronograph watch with a genuine leather strap.",
                    price=4499, stock=12, image_url="images/products/watch-3.jpg",
                ),
                Product(
                    name="Gold-Plated Earrings",
                    description="Lightweight gold-plated drop earrings, nickel-free.",
                    price=899, stock=30, image_url="images/products/jewellery-1.jpg",
                ),
                Product(
                    name="Eau de Parfum",
                    description="Long-lasting unisex eau de parfum, 100ml bottle.",
                    price=1299, stock=25, image_url="images/products/perfume.jpg",
                ),
                Product(
                    name="Herbal Shampoo",
                    description="Sulphate-free herbal shampoo for daily use, 340ml.",
                    price=349, stock=60, image_url="images/products/shampoo.jpg",
                ),
                Product(
                    name="Sports Duffel Bag",
                    description="Water-resistant duffel bag with a dedicated shoe compartment.",
                    price=1599, stock=20, image_url="images/products/sports-1.jpg",
                ),
                Product(
                    name="Relaxed Fit T-Shirt",
                    description="100% cotton relaxed-fit t-shirt, pre-shrunk fabric.",
                    price=599, stock=50, image_url="images/products/clothes-1.jpg",
                ),
                Product(
                    name="Cotton Formal Shirt",
                    description="Wrinkle-resistant cotton formal shirt, tailored fit.",
                    price=1199, stock=28, image_url="images/products/shirt-1.jpg",
                ),
            ])
            self.stdout.write(self.style.SUCCESS("Seeded 15 demo products."))
        else:
            self.stdout.write("Products already exist, skipping seed.")
