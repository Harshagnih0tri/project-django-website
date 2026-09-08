from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import RegisterForm, CheckoutForm, ProductForm
from .models import Product, Order, OrderItem

CART_SESSION_KEY = "cart"


def is_admin(user):
    return user.is_active and user.is_staff


# ---------------------------------------------------------------------------
# Cart helpers — cart is stored in the session as {product_id (str): quantity}
# ---------------------------------------------------------------------------

def _get_cart(request):
    return request.session.setdefault(CART_SESSION_KEY, {})


def _cart_contents(request):
    cart = _get_cart(request)
    items = []
    for product_id, qty in cart.items():
        try:
            product = Product.objects.get(pk=int(product_id), is_active=True)
        except Product.DoesNotExist:
            continue
        items.append({"product": product, "qty": qty, "line_total": product.price * qty})
    return items


# ---------------------------------------------------------------------------
# Storefront
# ---------------------------------------------------------------------------

def index(request):
    products = Product.objects.filter(is_active=True)
    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(name__icontains=query)
    return render(request, "shop/index.html", {"products": products, "query": query})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "shop/product_detail.html", {"product": product})


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "shop/register.html"
    success_url = reverse_lazy("shop:login")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Account created. Please log in.")
        return response


class ShopLoginView(LoginView):
    template_name = "shop/login.html"
    redirect_authenticated_user = True


class ShopLogoutView(LogoutView):
    next_page = reverse_lazy("shop:index")


# ---------------------------------------------------------------------------
# Cart
# ---------------------------------------------------------------------------

def view_cart(request):
    items = _cart_contents(request)
    total = sum((item["line_total"] for item in items), Decimal("0"))
    return render(request, "shop/cart.html", {"items": items, "total": total})


def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    qty = max(1, int(request.POST.get("quantity", 1)))
    cart = _get_cart(request)
    current_qty = cart.get(str(pk), 0)
    new_qty = min(current_qty + qty, product.stock) if product.stock else current_qty + qty
    cart[str(pk)] = new_qty
    request.session.modified = True
    messages.success(request, f"Added {product.name} to your cart.")
    return redirect(request.META.get("HTTP_REFERER", "shop:index"))


def update_cart(request, pk):
    cart = _get_cart(request)
    qty = int(request.POST.get("quantity", 0))
    if qty <= 0:
        cart.pop(str(pk), None)
    else:
        cart[str(pk)] = qty
    request.session.modified = True
    return redirect("shop:view_cart")


def remove_from_cart(request, pk):
    cart = _get_cart(request)
    cart.pop(str(pk), None)
    request.session.modified = True
    return redirect("shop:view_cart")


# ---------------------------------------------------------------------------
# Checkout
# ---------------------------------------------------------------------------

@login_required
def checkout(request):
    items = _cart_contents(request)
    if not items:
        messages.info(request, "Your cart is empty.")
        return redirect("shop:index")

    total = sum((item["line_total"] for item in items), Decimal("0"))

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            for item in items:
                if item["qty"] > item["product"].stock:
                    messages.error(request, f"Not enough stock for {item['product'].name}.")
                    return render(request, "shop/checkout.html", {"form": form, "items": items, "total": total})

            order = Order.objects.create(
                user=request.user,
                status="paid",
                total=total,
                shipping_address=form.cleaned_data["shipping_address"],
            )
            for item in items:
                product = item["product"]
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    unit_price=product.price,
                    quantity=item["qty"],
                )
                product.stock -= item["qty"]
                product.save()

            request.session[CART_SESSION_KEY] = {}
            request.session.modified = True
            messages.success(request, "Order placed successfully!")
            return redirect("shop:order_confirmation", pk=order.pk)
    else:
        form = CheckoutForm()

    return render(request, "shop/checkout.html", {"form": form, "items": items, "total": total})


@login_required
def order_confirmation(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.user_id != request.user.id and not request.user.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    return render(request, "shop/order_confirmation.html", {"order": order})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, "shop/my_orders.html", {"orders": orders})


# ---------------------------------------------------------------------------
# Admin — product management (custom storefront-side panel; Django's own
# /admin/ site also manages these models via shop/admin.py)
# ---------------------------------------------------------------------------

@user_passes_test(is_admin)
def admin_products(request):
    products = Product.objects.all()
    return render(request, "shop/admin_products.html", {"products": products})


@user_passes_test(is_admin)
def admin_new_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Product created.")
            return redirect("shop:admin_products")
    else:
        form = ProductForm()
    return render(request, "shop/admin_product_form.html", {"form": form, "title": "New Product"})


@user_passes_test(is_admin)
def admin_edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated.")
            return redirect("shop:admin_products")
    else:
        form = ProductForm(instance=product)
    return render(request, "shop/admin_product_form.html", {"form": form, "title": "Edit Product"})


@user_passes_test(is_admin)
def admin_delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_active = False
    product.save()
    messages.success(request, "Product removed.")
    return redirect("shop:admin_products")
