# E-Commerce Website

A full-stack e-commerce platform built with Django. Users browse a product catalog, add items to a cart, check out, and view order history; staff manage the catalog through both a custom in-app panel and Django's built-in admin site.

## Features

- **Auth** — registration and login backed by Django's built-in `User` model and auth system (hashed passwords, sessions, CSRF protection).
- **Product catalog** — listing and detail pages, backed by a `Product` model (name, description, price, stock, image).
- **Cart** — session-based cart (add, update quantity, remove), capped at available stock.
- **Checkout & orders** — checkout creates an `Order` with snapshotted `OrderItem` rows (product name/price captured at purchase time, so later catalog changes don't rewrite order history), decrements stock, and shows an order confirmation page. Logged-in users see their order history.
- **Admin** — a staff-only in-app product management panel (`@user_passes_test`-guarded), plus the full Django admin site at `/admin/` (product and order management, including inline order-item viewing) for free.

## Tech stack

Python, Django 5, Django ORM, SQLite, Django's auth/sessions/messages/admin frameworks.

## Credits

The front-end layout and CSS (header, footer, product-grid card styling, color palette) are
adapted from the open-source [Anon](https://github.com/codewithsadee/anon-ecommerce-website)
template by [codewithsadee](https://github.com/codewithsadee) (MIT-style, free to use, no
license file). It's used here purely as a visual skin — the templates were rewritten against it
to plug in real data and behavior. Everything else — models, auth, cart/session logic,
checkout, stock tracking, order history, the admin panel, and the test suite — is original
Django work for this project.

## Project structure

```
core/               Django project settings, root URLconf
shop/
  models.py         Product, Order, OrderItem
  views.py          Storefront, auth, cart, checkout, admin panel views
  forms.py          RegisterForm, CheckoutForm, ProductForm
  urls.py           App URL routes
  admin.py          Django admin registration for Product/Order
  templates/shop/   All page templates
  management/commands/seed_demo_data.py   Seeds a demo admin + sample products
  tests.py          End-to-end test suite
static/style.css    Styling
```

## Setup

```bash
git clone https://github.com/Harshagnih0tri/project-django-website.git
cd project-django-website
python -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver
```

Visit `http://localhost:8000`. The seed command creates a demo admin (`admin` / `admin12345`) and three sample products.

- Storefront admin panel: `/manage/products/`
- Django admin site: `/admin/`

## Running the tests

```bash
python manage.py test shop
```

Covers registration/login, the full browse → cart → checkout → stock-decrement → order-history flow, non-admin users being blocked from product management, admin product CRUD (including soft-delete), and that staff can reach the Django admin site.
