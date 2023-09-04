from django import forms

from .models import Cart

class CartForm(forms.ModelForm):
    class Meta:                           # Meta クラス ？
        model = Cart
        fields = ["product", "price", "user"]