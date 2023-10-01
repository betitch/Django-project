from django.contrib import admin
from .models import Category, Product, Cart, Message, Order

# modelを管理サイトで操作できるようにする。
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Message)
admin.site.register(Order)

