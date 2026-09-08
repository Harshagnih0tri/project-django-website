# E-Commerce Website

A full-stack e-commerce platform built with Flask. Users can browse products, add items to a cart, check out, and view order history; an admin role manages the product catalog.

## Features

- **Auth** — registration and login with hashed passwords (Werkzeug), session management via Flask-Login.
- **Product catalog** — product listing and detail pages, backed by a `Product` model (name, description, price, stock, image).
- **Cart** — session-based cart (add, update quantity, remove) that respects available stock.
- **Checkout & orders** — checkout creates an `Order` with snapshotted `OrderItem` rows (product name/price captured at purchase time, so later price changes don't rewrite order history), decrements stock, and shows an order confirmation page. Logged-in users can view their order history.
- **Admin** — an `is_admin`-gated area to create, edit, and (soft-)delete products, guarded by a custom `@admin_required` decorator.

## Tech stack

Python, Flask, Flask-SQLAlchemy (ORM), Flask-Login (auth/session), Flask-WTF (forms + CSRF), SQLite.

## Project structure

```
app.py            Flask app, routes (storefront, auth, cart, checkout, admin)
models.py         SQLAlchemy models: User, Product, Order, OrderItem
forms.py          WTForms: Register, Login, Product, Checkout
templates/        Jinja2 templates
static/style.css  Styling
test_flow.py       End-to-end smoke test (register -> login -> browse -> cart -> checkout -> order -> admin CRUD)
```

## Setup

```bash
git clone https://github.com/Harshagnih0tri/project-django-website.git
cd project-django-website
python -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py
```

Visit `http://localhost:5000`. The app seeds a demo admin account on first run:

- **Admin login:** `admin@example.com` / `admin123`

Three demo products are seeded automatically so the storefront isn't empty on first run.

## Running the tests

```bash
python test_flow.py
```

Runs an end-to-end flow against a disposable test database: registration, login, browsing, add-to-cart, checkout (with stock decrement), order history, and the full admin product-management flow, asserting on the actual page content and database state at each step.
