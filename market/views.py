from django.shortcuts import render, redirect
from django.views import View
from .models import Product, Category, Cart, Message
from .forms import CartForm


# Create your views here.
class IndexView(View):
    def get(self, request, *args, **kwargs):

        context = {}

        context["products"] = Product.objects.all()

        # print(context)          #チェック用

        return render(request, "market/index.html", context)
    
index = IndexView.as_view()

class SingleView(View):
    def get(self, request, pk, *args, **kwargs):

        product = Product.objects.filter(id=pk).first()

        # この商品に入札しているCartのデータを取り出す。
        carts = Cart.objects.filter(product=pk).order_by("-price")     #　降順に並べるため

        context = {"product":product, "carts":carts}

        return render(request, "market/single.html", context)
    
    def post(self, request, pk, *args, **kwargs):
        
        # price しか含まれていないので、
        copied = request.POST.copy()            # QueryDict 型らしい
        print(type(copied))                        # チェック用
        copied["user"]      = request.user
        copied["product"]   = pk

        form = CartForm(copied)

        if form.is_valid():
            form.save()
        else:
            print(form.erros)

        return redirect("market:single", pk)

    
single = SingleView.as_view()
