from django.shortcuts import render, redirect
from django.views import View
from .models import Product, Category, Cart, Message
from .forms import CartForm, UserForm


# Create your views here.
class IndexView(View):
    def get(self, request, *args, **kwargs):

        context = {}
        context["categories"] = Category.objects.all()
        context["products"] = Product.objects.all()
        # ↓と↑は同じ
        # products = Product.objects.all()
        # context = { "products": products }
        context["image_numbers"] = list(range(1, 10))    # 仮の画像

        return render(request, "market/index.html", context)     # 第一引数になぜ、request いるんだっけ？
    
index = IndexView.as_view()


class MyListView(View):
    def get(self, request, *args, **kwargs):
        products = Product.objects.filter(user=request.user)
        carts = Cart.objects.filter(user=request.user)
        context = {"products":products, "carts":carts}
        context["image_numbers"] = list(range(1, 10))    # 仮の画像
        return render(request, "market/mylist.html", context)
    
mylist = MyListView.as_view()
    

class SingleView(View):
    def get(self, request, pk, *args, **kwargs):
        product = Product.objects.filter(id=pk).first()       # .first() いる？　pk に一致するのは一つだけでは？

        # この商品に入札しているCartのデータを取り出す。
        carts = Cart.objects.filter(product=pk).order_by("-price")     #　降順に並べるため
        messages = Message.objects.filter(product=pk).order_by("-dt")
        context = {"product":product, "carts":carts, "messages":messages}
        context["image_numbers"] = list(range(1, 10))    # 仮の画像

        return render(request, "market/single.html", context)
    
    def post(self, request, pk, *args, **kwargs):
        
        # price しか含まれていないので、
        copied = request.POST.copy()            # QueryDict 型らしい                       
        copied["user"]      = request.user    # ログイン中の user_name が入ってくる。  
        copied["product"]   = pk

        form = CartForm(copied)

        if form.is_valid():
            form.save()
        else:
            print(form.errors)

        return redirect("market:single", pk)     # urls の app_name と　name を組み合わせている。
                                                 # post の場合は何で redirect でないとダメなんだっけ？

    
single = SingleView.as_view()


# メッセージの保存を受け付けるビューを作る
class MessageView(View):
                          # pk は product の id
    def post(self, request, pk, *args, **kwargs): 
        # 送られたデータをコピー
        copied = request.POST.copy()
        copied["product"] = pk
        copied['user'] = request.user

        form =  MessageForm(copied)

        if form.is_valid():
            form.save()

        return redirect("market:single", pk)
    
message = MessageView.as_view()





class MypageView(View):
    def get(self, request, *args, **kwargs):

        return render(request, "market/mypage.html")  # こっちはパス
    
    
    def post(self, request, *args, **kwargs):


        # 編集対象を instance に指定する。request.user を instance に指定
        form = UserForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
        else:
            print(form.erros)

        return redirect("market:mypage")
    


mypage = MypageView.as_view()

