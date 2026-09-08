"""End-to-end smoke test: register, login, browse, add to cart, checkout, view order,
plus admin product management. Run with: python test_flow.py
"""
import os

# fresh db for the test
if os.path.exists("instance/shop.db"):
    os.remove("instance/shop.db")

from app import app, db  # noqa: E402
from models import User, Product, Order  # noqa: E402

app.config["WTF_CSRF_ENABLED"] = False
app.config["TESTING"] = True

client = app.test_client()

def check(label, condition):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    if not condition:
        raise SystemExit(1)

with app.app_context():
    db.create_all()

# 1. Register a normal user
resp = client.post("/register", data={
    "name": "Test Buyer", "email": "buyer@example.com",
    "password": "secret123", "confirm": "secret123",
}, follow_redirects=True)
check("register renders login page", b"Log In" in resp.data or b"Log In" in resp.data)

# 2. Login as buyer
resp = client.post("/login", data={"email": "buyer@example.com", "password": "secret123"}, follow_redirects=True)
check("login succeeds (nav shows logged-in name)", b"Logout (Test Buyer)" in resp.data)

# 3. Browse products (seeded demo products should exist)
resp = client.get("/")
check("homepage lists seeded products", b"Wireless Mouse" in resp.data)

with app.app_context():
    product = Product.query.filter_by(name="Wireless Mouse").first()
    check("seeded product exists in DB", product is not None)
    product_id = product.id

# 4. Add to cart
resp = client.post(f"/cart/add/{product_id}", data={"quantity": 2}, follow_redirects=True)
check("add to cart redirects OK", resp.status_code == 200)

resp = client.get("/cart")
check("cart page shows item", b"Wireless Mouse" in resp.data)

# 5. Checkout
resp = client.post("/checkout", data={"shipping_address": "123 Test Street, Test City"}, follow_redirects=True)
check("checkout confirms order", b"confirmed" in resp.data)

with app.app_context():
    order = Order.query.first()
    check("order created in DB", order is not None)
    check("order total matches 2x product price", order.total_cents == 79900 * 2)
    check("stock decremented", db.session.get(Product, product_id).stock == 25 - 2)

# 6. Cart should be empty after checkout
resp = client.get("/cart")
check("cart is empty after checkout", b"empty" in resp.data)

# 7. My orders page
resp = client.get("/orders")
check("my orders lists the order", str(order.id).encode() in resp.data)

client.get("/logout")

# 8. Non-admin cannot access admin
client.post("/login", data={"email": "buyer@example.com", "password": "secret123"})
resp = client.get("/admin/products")
check("non-admin blocked from admin (403)", resp.status_code == 403)
client.get("/logout")

# 9. Admin login and product management
resp = client.post("/login", data={"email": "admin@example.com", "password": "admin123"}, follow_redirects=True)
check("admin login succeeds", b"Logout (Admin)" in resp.data)

resp = client.get("/admin/products")
check("admin can view product management", b"Manage Products" in resp.data)

resp = client.post("/admin/products/new", data={
    "name": "Test Widget", "description": "A widget for testing",
    "price": "9.99", "stock": "5", "image_url": "",
}, follow_redirects=True)
check("admin can create a product", b"Test Widget" in resp.data)

with app.app_context():
    widget = Product.query.filter_by(name="Test Widget").first()
    check("new product persisted with correct price", widget.price_cents == 999)

resp = client.post(f"/admin/products/{widget.id}/delete", follow_redirects=True)
check("admin can soft-delete a product", resp.status_code == 200)

with app.app_context():
    check("soft-deleted product is inactive", db.session.get(Product, widget.id).is_active is False)

resp = client.get("/")
check("soft-deleted product no longer on storefront", b"Test Widget" not in resp.data)

print("\nAll checks passed.")
