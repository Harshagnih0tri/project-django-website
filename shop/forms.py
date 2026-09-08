from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), max_length=300)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "price", "stock", "image_url"]
        widgets = {
            "image_url": forms.TextInput(attrs={
                "placeholder": "https://example.com/photo.jpg or images/products/shoe-1.jpg",
            }),
        }
