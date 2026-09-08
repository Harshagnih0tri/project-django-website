import os
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from models import db, User, Product, Order, OrderItem
from forms import RegisterForm, LoginForm, ProductForm, CheckoutForm

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "instance", "shop.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return view_func(*args, **kwargs)
    return wrapper


# ---------------------------------------------------------------------------
# Cart helpers — cart is stored in the session as {product_id (str): quantity}
# ---------------------------------------------------------------------------

def get_cart():
    return session.setdefault("cart", {})


def cart_contents():
    """Returns list of (product, quantity, line_total) for items still in stock/active."""
    cart = get_cart()
    items = []
    for product_id, qty in cart.items():
        product = db.session.get(Product, int(product_id))
        if product and product.is_active:
            items.append((product, qty, product.price * qty))
    return items


# ---------------------------------------------------------------------------
# Storefront
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    products = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).all()
    return render_template("index.html", products=products)


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product_detail.html", product=product)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash("An account with that email already exists.", "danger")
            return render_template("register.html", form=form)
        user = User(name=form.name.data, email=form.email.data.lower())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Account created. Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Cart
# ---------------------------------------------------------------------------

@app.route("/cart")
def view_cart():
    items = cart_contents()
    total = sum(line_total for _, _, line_total in items)
    return render_template("cart.html", items=items, total=total)


@app.route("/cart/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    qty = max(1, int(request.form.get("quantity", 1)))
    cart = get_cart()
    current_qty = cart.get(str(product_id), 0)
    new_qty = min(current_qty + qty, product.stock) if product.stock else current_qty + qty
    cart[str(product_id)] = new_qty
    session.modified = True
    flash(f"Added {product.name} to your cart.", "success")
    return redirect(request.referrer or url_for("index"))


@app.route("/cart/update/<int:product_id>", methods=["POST"])
def update_cart(product_id):
    cart = get_cart()
    qty = int(request.form.get("quantity", 0))
    if qty <= 0:
        cart.pop(str(product_id), None)
    else:
        cart[str(product_id)] = qty
    session.modified = True
    return redirect(url_for("view_cart"))


@app.route("/cart/remove/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart = get_cart()
    cart.pop(str(product_id), None)
    session.modified = True
    return redirect(url_for("view_cart"))


# ---------------------------------------------------------------------------
# Checkout
# ---------------------------------------------------------------------------

@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    items = cart_contents()
    if not items:
        flash("Your cart is empty.", "info")
        return redirect(url_for("index"))

    form = CheckoutForm()
    total = sum(line_total for _, _, line_total in items)

    if form.validate_on_submit():
        for product, qty, _ in items:
            if qty > product.stock:
                flash(f"Not enough stock for {product.name} (only {product.stock} left).", "danger")
                return render_template("checkout.html", form=form, items=items, total=total)

        order = Order(
            user_id=current_user.id,
            status="paid",
            total_cents=int(round(total * 100)),
            shipping_address=form.shipping_address.data,
        )
        db.session.add(order)
        db.session.flush()  # assign order.id before creating order items

        for product, qty, _ in items:
            db.session.add(OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                unit_price_cents=product.price_cents,
                quantity=qty,
            ))
            product.stock -= qty

        db.session.commit()
        session["cart"] = {}
        session.modified = True
        flash("Order placed successfully!", "success")
        return redirect(url_for("order_confirmation", order_id=order.id))

    return render_template("checkout.html", form=form, items=items, total=total)


@app.route("/orders/<int:order_id>")
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return render_template("order_confirmation.html", order=order)


@app.route("/orders")
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template("my_orders.html", orders=orders)


# ---------------------------------------------------------------------------
# Admin — product management
# ---------------------------------------------------------------------------

@app.route("/admin/products")
@admin_required
def admin_products():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template("admin_products.html", products=products)


@app.route("/admin/products/new", methods=["GET", "POST"])
@admin_required
def admin_new_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price_cents=int(round(float(form.price.data) * 100)),
            stock=form.stock.data,
            image_url=form.image_url.data or None,
        )
        db.session.add(product)
        db.session.commit()
        flash("Product created.", "success")
        return redirect(url_for("admin_products"))
    return render_template("admin_product_form.html", form=form, title="New Product")


@app.route("/admin/products/<int:product_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    if request.method == "GET":
        form.price.data = product.price
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price_cents = int(round(float(form.price.data) * 100))
        product.stock = form.stock.data
        product.image_url = form.image_url.data or None
        db.session.commit()
        flash("Product updated.", "success")
        return redirect(url_for("admin_products"))
    return render_template("admin_product_form.html", form=form, title="Edit Product")


@app.route("/admin/products/<int:product_id>/delete", methods=["POST"])
@admin_required
def admin_delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = False  # soft delete so past orders keep a valid reference
    db.session.commit()
    flash("Product removed.", "success")
    return redirect(url_for("admin_products"))


def seed_if_empty():
    """Create tables and a demo admin + a few products on first run."""
    db.create_all()
    if not User.query.filter_by(email="admin@example.com").first():
        admin = User(name="Admin", email="admin@example.com", is_admin=True)
        admin.set_password("admin123")
        db.session.add(admin)
    if Product.query.count() == 0:
        demo_products = [
            Product(name="Wireless Mouse", description="Ergonomic 2.4GHz wireless mouse.", price_cents=79900, stock=25),
            Product(name="Mechanical Keyboard", description="Hot-swappable mechanical keyboard, blue switches.", price_cents=349900, stock=15),
            Product(name="USB-C Hub", description="7-in-1 USB-C hub with HDMI and SD card reader.", price_cents=189900, stock=30),
        ]
        db.session.add_all(demo_products)
    db.session.commit()


with app.app_context():
    seed_if_empty()


if __name__ == "__main__":
    app.run(debug=True)
