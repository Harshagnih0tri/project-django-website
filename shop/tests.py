from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Product, Order


class ShopFlowTests(TestCase):
    """End-to-end smoke test: register, login, browse, cart, checkout,
    order history, plus admin-guarded product management."""

    def setUp(self):
        self.mouse = Product.objects.create(name="Wireless Mouse", price=799, stock=25)
        self.admin = User.objects.create_superuser("admin", "admin@example.com", "admin12345")
        self.admin.is_staff = True
        self.admin.save()

    def test_register_and_login(self):
        resp = self.client.post(reverse("shop:register"), {
            "username": "buyer", "email": "buyer@example.com",
            "password1": "s3cretpass123", "password2": "s3cretpass123",
        })
        self.assertEqual(resp.status_code, 302, "registration should redirect to login")
        self.assertTrue(User.objects.filter(username="buyer").exists())

        logged_in = self.client.login(username="buyer", password="s3cretpass123")
        self.assertTrue(logged_in)

    def test_full_purchase_flow(self):
        self.client.post(reverse("shop:register"), {
            "username": "buyer2", "email": "buyer2@example.com",
            "password1": "s3cretpass123", "password2": "s3cretpass123",
        })
        self.client.login(username="buyer2", password="s3cretpass123")

        # browse
        resp = self.client.get(reverse("shop:index"))
        self.assertContains(resp, "Wireless Mouse")

        # add to cart
        resp = self.client.post(reverse("shop:add_to_cart", args=[self.mouse.pk]), {"quantity": 2})
        self.assertEqual(resp.status_code, 302)

        resp = self.client.get(reverse("shop:view_cart"))
        self.assertContains(resp, "Wireless Mouse")

        # checkout
        resp = self.client.post(reverse("shop:checkout"), {"shipping_address": "123 Test Street"})
        self.assertEqual(resp.status_code, 302)

        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.total, self.mouse.price * 2)

        self.mouse.refresh_from_db()
        self.assertEqual(self.mouse.stock, 23, "stock should decrement by purchased quantity")

        # cart empty after checkout
        resp = self.client.get(reverse("shop:view_cart"))
        self.assertContains(resp, "empty")

        # order shows in history
        resp = self.client.get(reverse("shop:my_orders"))
        self.assertContains(resp, str(order.id))

    def test_non_admin_blocked_from_product_management(self):
        User.objects.create_user("plainuser", "plain@example.com", "pass12345")
        self.client.login(username="plainuser", password="pass12345")
        resp = self.client.get(reverse("shop:admin_products"))
        self.assertEqual(resp.status_code, 302, "non-admin should be redirected (login/permission), not shown the page")

    def test_admin_can_manage_products(self):
        self.client.login(username="admin", password="admin12345")

        resp = self.client.get(reverse("shop:admin_products"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Manage Products")

        resp = self.client.post(reverse("shop:admin_new_product"), {
            "name": "Test Widget", "description": "A widget", "price": "9.99", "stock": "5", "image_url": "",
        })
        self.assertEqual(resp.status_code, 302)
        widget = Product.objects.get(name="Test Widget")
        self.assertEqual(str(widget.price), "9.99")

        resp = self.client.post(reverse("shop:admin_delete_product", args=[widget.pk]))
        self.assertEqual(resp.status_code, 302)
        widget.refresh_from_db()
        self.assertFalse(widget.is_active, "delete should soft-delete, not hard-delete")

        resp = self.client.get(reverse("shop:index"))
        self.assertNotContains(resp, "Test Widget", msg_prefix="soft-deleted product should not appear on storefront")

    def test_django_admin_site_accessible_to_staff(self):
        self.client.login(username="admin", password="admin12345")
        resp = self.client.get("/admin/shop/product/")
        self.assertEqual(resp.status_code, 200)
