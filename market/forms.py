from django import forms

from .models import Cart, Message
from django.contrib.auth.models import User 


class CartForm(forms.ModelForm):
    class Meta:                           # Meta クラス ？
        model = Cart
        fields = ["product", "price", "user"]


class UserForm(forms.ModelForm):

    class Meta:     # このフォームグラスの基本仕様
        # 何のモデルのフィールドをバリデーションするのか？
        model = User
        fields = ["first_name", "last_name"]


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["product", "content", "user"]