from django.shortcuts import render, redirect     
from django.views import View
from .models import Product, Category, Cart, Message
from .forms import ProductForm,CartForm, UserForm, MessageForm
from django.utils import timezone
import magic

# ALLOWED_MIME = ["application/pdf"]


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


class SingleView(View):
    def get(self, request, pk, *args, **kwargs):
        product = Product.objects.filter(id=pk).first()       # .first() いる？　pk に一致するのは一つだけでは？
                                                              # 配列で取ってくるので、１個でも first が必要、 無いと for ループを回す必要がある？

        # この商品に入札しているCartのデータを取り出す。
        carts = Cart.objects.filter(product=pk).order_by("-price")     #　降順に並べるため
        messages = Message.objects.filter(product=pk).order_by("-dt")
        context = {"product":product, "carts":carts, "messages":messages}     # context = {} 初期化はしなくていいのか？
                                                                              # product の中に image も入っている。
        context["image_numbers"] = list(range(1, 10))    # 仮の画像

        # 現在時刻をコンテキストに入れる。
        context["now"] = timezone.now()

        #　最高値のcartだけ取り出す。order_byとfirstで最高値のデータだけ出せる。
        # TODO: deadlineも参考にする。is_bidがFalseもしくは、deadlineがすぎている場合。OR検索になる。
        # OR検索をするためにはクエリビルダが必要。
        context['highest'] = Cart.objects.filter(product=pk, product__is_bid=False).order_by("-price").first()
                                                                   # ↑アンスコ２つは、外部キー属性にアクセスするショートカット
        return render(request, "market/single.html", context)

    # 入札
    def post(self, request, pk, *args, **kwargs):
        
        # price しか含まれていないので、
        copied = request.POST.copy()            # QueryDict 型らしい  この時点では、price のみ入っている？                      
        copied["user"]      = request.user    # ログイン中の user_name が入ってくる。  

        # 指定した商品は入札できるかどうかをチェックした上で、入札処理をする。
        copied["product"]   = Product.objects.filter(id=pk, is_bid=True).first()

        form = CartForm(copied)

        if form.is_valid():
            form.save()                 # ここで、model に書き込みか？　これが無いと model には書き込み行われない？
        else:
            print(form.errors)

        return redirect("market:single", pk)     # urls の app_name と　name を組み合わせている。
                                                 # render にしてしまうと、再表示時、もう一度 post されてしまう。  
single = SingleView.as_view()                    # .html  は描かなくていいんだっけ？


class MyListView(View):
    def get(self, request, *args, **kwargs):
        products = Product.objects.filter(user=request.user)
        carts = Cart.objects.filter(user=request.user)
        context = {"products":products, "carts":carts}
        context["image_numbers"] = list(range(1, 10))    # 仮の画像
        return render(request, "market/mylist.html", context)
    
mylist = MyListView.as_view()


class MyPostView(View):
    def get(self, request, *args, **kwargs):
        product_id = request.session.get('last_posted_product_id')

        if product_id:
            product = Product.objects.filter(id=product_id).first()
        else:
            default_data = {
                "category": "カテゴリ"
                "name": "商品名",
                "price": 0,
                "image": "noImage.png",       # でいいのかな？
                "description": "商品説明",
                "deadline": timezone.now(),    # 関数入れてもいいんか？
            }
            product = Product(**default_data)

        return render(request, "market/mypost.html", {"product":product})

    # 新規商品の出品
    def post(self, request, *args, **kwargs):
        copied = request.POST.copy()
        copied["user"] = request.user
        form = ProductForm(copied)      # request.FILES 必要？

        if form.is_valid():
            product = form.save()
            request.session['last_posted_product_id'] = product.id
        else:
            print(form.errors)

        return redirect("market:mypost")

mypost = MyPostView.as_view()


"""
class MySingleView(View):                            # 該当商品を一つ取ってくる。 そういえば、最初は商品が無いな。
    def get(self, request, pk, *args, **kwargs):
        product = Product.objects.filter(id=pk).first()  
        carts = Cart.objects.filter(product=pk).order_by("-price") 
        messages = Message.objects.filter(product=pk).order_by("-dt")
        context = {"product":product, "carts":carts, "messages":messages}  # product の中に image も入っている。
        # 現在時刻をコンテキストに入れる。
        context["now"] = timezone.now()

        # 最高値のcartだけ取り出す。order_byとfirstで最高値のデータだけ出せる。
        # TODO: deadlineも参考にする。is_bidがFalseもしくは、deadlineがすぎている場合。OR検索になる。
        # OR検索をするためにはクエリビルダが必要。
        context['highest'] = Cart.objects.filter(product=pk, product__is_bid=False).order_by("-price").first()
                                                                   # ↑アンスコ２つは、外部キー属性にアクセスするショートカット
        return render(request, "market/mysingle.html", context)

    # 出品商品の属性編集    なんか instance の指定が必要になるらしい。
    def post(self, request, pk, *args, **kwargs):
        
        # price しか含まれていないので、
        copied = request.POST.copy()            # QueryDict 型らしい                      
        copied["user"]      = request.user    # ログイン中の user_name が入ってくる。  

        # 指定した商品は入札できるかどうかをチェックした上で、入札処理をする。
        copied["product"]   = Product.objects.filter(id=pk, is_bid=True).first()

        form = ProductForm(copied)

        if form.is_valid():
            form.save()
        else:
            print(form.errors)

        return redirect("market:mysingle", pk)     # urls の app_name と name を組み合わせている。
                                                     
single = MySingleView.as_view()
"""


# 出品した商品を入札できない状態にする。
class ProductBidStatusView(View):
     
     # 商品の入札状態を変更する。pk はProduct.id
     def post(self, request, pk, *args, **kwargs):
        
        # 入札状態を変更したい商品を特定 (自分が出品した商品、指定したpkの商品)         
        product = Product.objects.filter(user=request.user, id=pk).first()
        
        # 指定した商品がない場合はリダイレクト
        if not product:          # これだけで boolean になる ？
            return redirect("market:single", pk)    # pk が無いと、single ページが特定できない ？
        
        # ブーリアン値を反転させる
        product.is_bid = not product.is_bid
        product.save()

        return redirect("market:single", pk)

product_bid_status = ProductBidStatusView.as_view()


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


