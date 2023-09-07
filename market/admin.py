from django.contrib import admin
from .models import Category, Product, Cart, Message

# category と product を管理サイトで操作できるようにする。
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Message)

