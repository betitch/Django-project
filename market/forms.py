from django import forms                         # データベースへの保存に関してバリデーションを行う
from .models import Product, Cart, Message
from django.contrib.auth.models import User 


class ProductForm(forms.ModelForm):
    class Meta:                           # Meta クラス ？
        model = Product
        fields = [
                    "category",
                    "name",
                    "price", 
                    "user",
                    "image", 
                    "description", 
                    "deadline"
                ]  


class CartForm(forms.ModelForm):
    class Meta:                           
        model = Cart
        fields = ["product", "price", "user"]   # product, user 外部キーだが、バリデートする必要あり？
                                                # ↑ views.py の post メソッドで、product と user をコピーしているが。

class UserForm(forms.ModelForm):

    class Meta:        # このフォームグラスの基本仕様
        # 何のモデルのフィールドをバリデーションするのか？
        model = User
        fields = ["first_name", "last_name"]


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["product", "content", "user"]