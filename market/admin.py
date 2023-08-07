from django.contrib import admin
from .models import Category, Product

# Register your models here.
# category と product を管理サイトで操作できるようにする。
admin.site.register(Category)
admin.site.register(Product)
