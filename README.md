# E-Commerce Website (Django)

A full-stack e-commerce platform built with Django, featuring user authentication, product listings, cart functionality, and admin management.

## Features
- User registration and authentication
- Product listing and browsing
- Shopping cart functionality
- Admin panel for product and order management
- Secure backend logic with database-driven operations

## Tech Stack
- Python
- Django
- HTML, CSS, JavaScript
- SQLite / MySQL (Django ORM)

## How It Works
1. Users register/log in through the authentication system
2. Products are displayed on listing pages with details
3. Users add products to a cart and proceed through checkout
4. Admins manage products, inventory, and orders through Django's admin panel

## Setup
\`\`\`bash
git clone <your-repo-url>
cd <repo-folder-name>
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
\`\`\`

## Project Structure
\`\`\`
ecommerce_project/
├── manage.py
├── requirements.txt
├── <app_name>/          # main app (models, views, urls)
├── templates/            # HTML templates
├── static/                # CSS, JS, images
└── ecommerce_project/    # settings, urls, wsgi
\`\`\`
