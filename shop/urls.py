from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.index, name="index"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),

    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.ShopLoginView.as_view(), name="login"),
    path("logout/", views.ShopLogoutView.as_view(), name="logout"),

    path("cart/", views.view_cart, name="view_cart"),
    path("cart/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:pk>/", views.update_cart, name="update_cart"),
    path("cart/remove/<int:pk>/", views.remove_from_cart, name="remove_from_cart"),

    path("checkout/", views.checkout, name="checkout"),
    path("orders/", views.my_orders, name="my_orders"),
    path("orders/<int:pk>/", views.order_confirmation, name="order_confirmation"),

    path("manage/products/", views.admin_products, name="admin_products"),
    path("manage/products/new/", views.admin_new_product, name="admin_new_product"),
    path("manage/products/<int:pk>/edit/", views.admin_edit_product, name="admin_edit_product"),
    path("manage/products/<int:pk>/delete/", views.admin_delete_product, name="admin_delete_product"),
]
