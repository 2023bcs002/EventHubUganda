from django import forms
from .models import Product, Order
from django.core.validators import MinValueValidator

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'stock', 'image', 'is_available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'min': '0'}),
        }

    def clean_price(self):
        price = self.cleaned_data['price']
        if price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price

    def clean_stock(self):
        stock = self.cleaned_data['stock']
        if stock < 0:
            raise forms.ValidationError("Stock cannot be negative.")
        return stock

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_address', 'phone_number']
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your shipping address...'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Enter your phone number...'}),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        if not phone.isdigit():
            raise forms.ValidationError("Phone number should contain only digits.")
        if len(phone) < 10:
            raise forms.ValidationError("Phone number should be at least 10 digits long.")
        return phone

class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'value': 1, 'min': 1})
    )
    product_id = forms.IntegerField(widget=forms.HiddenInput())

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        return quantity 