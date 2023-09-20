from django.shortcuts import render, redirect     
from django.views import View
from .models import Product, Category, Cart, Message
from .forms import ProductForm,CartForm, UserForm, MessageForm
from django.utils import timezone
import magic
from django.db.models import Q    # Query ビルダを使うため、import

# ALLOWED_MIME = ["application/pdf"]


class IndexView(View):
    def get(self, request, *args, **kwargs):

        context = {}
        context["categories"] = Category.objects.all()
        context["products"] = Product.objects.all()
        # ↓と↑は同じ
        # products = Product.objects.all()
        # context = { "products": products }

        return render(request, "market/index.html", context)     # 第一引数になぜ、request いるんだっけ？
    
index = IndexView.as_view()


class SingleView(View):
    def get(self, request, pk, *args, **kwargs):              # pk は個別ページリンクの html で提供されている？
        product = Product.objects.filter(id=pk).first()       # .first() いる？　pk に一致するのは一つだけでは？
                                                              # 配列で取ってくるので、１個でも first が必要、 無いと for ループを回す必要がある？

        # この商品に入札しているCartのデータを取り出す。
        carts = Cart.objects.filter(product=pk).order_by("-price")     #　降順に並べるため
        messages = Message.objects.filter(product=pk).order_by("-dt")
        context = {"product":product, "carts":carts, "messages":messages}     # context = {} 初期化はしなくていいのか？
                                                                              # product の中に image も入っている。
        # 現在時刻をコンテキストに入れる。
        context["now"] = timezone.now()
        #　最高値のcartだけ取り出す。order_byとfirstで最高値のデータだけ出せる。
        """
        context['highest'] = Cart.objects.filter(product=pk, product__is_bid=False).order_by("-price").first()
                                                                   # ↑アンスコ２つは、外部キー属性にアクセスするショートカット
        """
                                                                                        # less than equal
        query = Q(product=pk, product__is_bid=False) | Q(product=pk, product__deadline__lte=timezone.now())
        context["highest"] = Cart.objects.filter(query).order_by("-price").first()

        # query の使い方例       
        # Qクラスのオブジェクトを作る
        query = Q()
        # query &= Q(条件) でqueryにAND条件を追加する
        # 入札可能で、100円以上
        query &= Q(is_bid=True)
        # greater than or equal
        query &= Q(price__gte=100)
        query = Q(is_bid=True, price__gte=100)   # 同じ結果になる
        # OR 検索の場合
        query = Q()
        # 入札可能または、100円以上
        query |= Q(is_bid=True)
        query = Q(is_bid=True) | Q(price__gte=100)  # 同じ結果になる
    
        return render(request, "market/single.html", context)

    # 入札
    def post(self, request, pk, *args, **kwargs):
        
        # price しか含まれていないので、
        copied = request.POST.copy()          # QueryDict 型らしい  この時点では、price のみ入っている？                      
        copied["user"]      = request.user    # ログイン中の user_name が入ってくる。  

        # 指定した商品は入札できるかどうかをチェックした上で、入札処理をする。
        copied["product"]   = Product.objects.filter(id=pk, is_bid=True, deadline__gte=timezone.now()).first()

        form = CartForm(copied)

        if form.is_valid():
            form.save()                
        else:
            print(form.errors)

        return redirect("market:single", pk)     # urls の app_name と　name を組み合わせている。
                                                 # render にしてしまうと、再表示時、もう一度 post されてしまう。  
single = SingleView.as_view()


class MyListView(View):
    def get(self, request, *args, **kwargs):
        products = Product.objects.filter(user=request.user)
        carts = Cart.objects.filter(user=request.user)
        context = {"products":products, "carts":carts}
        return render(request, "market/mylist.html", context)
    
mylist = MyListView.as_view()

# 新規投稿用
class MyPostView(View):
    # 投稿したらすぐに、投稿した商品の個別ページを表示させる。
    def get(self, request, *args, **kwargs):
        context = {}               # 初期化する時としない時があるのは何故？
        context["categories"] = Category.objects.all()   # get した時、category が不足してるんだっけ？

        return render(request, 'market/mypost.html', context)
    
    def post(self, request, *args, **kwargs):
        copied = request.POST.copy()
        copied["user"] = request.user

        form = ProductForm(copied, request.FILES)

        if form.is_valid():
            # 今作ったproduct(モデルオブジェクト)で参照できるのは、Productモデルのフィールドだけ
            product = form.save()
            # 商品の個別ページへリダイレクト
            return redirect("market:single", product.id)
        else:
            print(form.errors)
            # バリデーションエラーの場合は元のページへリダイレクト
            return redirect("market:mypost")                         


    """ 修正前の MyPostView の get, post

    def get(self, request, *args, **kwargs):   # 初回 Post 後の pk を *kwargs に処理させる
        
        if "pk" in kwargs:                     # pk というキー名はどこかでデフォルトで、決められている？
            exist_pk = True                   
            product = Product.objects.filter(id=kwargs["pk"]).first() 
        else:
            exist_pk = False
            tmp_category = Category(name="カテゴリ")
            default_data = {                   # 初回 Post 前に存在するデータを入れないと表示されない
                "category": tmp_category,        
                "name":"商品名",
                "price": 0,
                "user": request.user,
                "image": "noImage.png",       # でいいのかな？  
                "description": "商品説明",
                "deadline": timezone.now(),    # 関数入れてもいいんか？
                "is_bid": None,
            }
            product = Product(**default_data)
        categories = Category.objects.all()
        context = {"product": product, "categories": categories}
        context["does_exist"] = exist_pk

        return render(request, "market/mypost.html", context)    # render には pk は不要？

    # 新規商品の出品
    def post(self, request, *args, **kwargs):   # post も同様に、初回 post 時は pk が無い
        copied = request.POST.copy()
        copied["user"] = request.user
        form = ProductForm(copied, request.FILES)      # image データを読むために、request.FILES 必要

        if form.is_valid():
            product = form.save()                      # ここで、初めて、pk が付与される
        else:
            print(form.errors)

        return redirect("market:mypost_single", product.pk)   # 引数は product.pk になるのか。
                                                              # product.id = product.pk らしい pk はエイリアス
    """    

mypost = MyPostView.as_view()


""" 編集用 Viwe とするか？ MySingleEditView ?
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
            return redirect("market:single",pk)    # pk が無いとページが特定できない ？
        
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


# 購入処理を行うビューを作る。
import stripe      # import をここで書く？
# settings.pyに書いておいたStripeのAPIを読み込み
from django.conf import settings
from django.urls import reverse_lazy    # 何か逆引き用 class 内では reverse_lazy を使う？

import os


class SessionCreateView(View):
    # このpkはCartのid
    def get(self, request, pk, *args, **kwargs):
        context = {}

        STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
        STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY")
        print(STRIPE_PUBLISHABLE_KEY)
        print(STRIPE_API_KEY)


        # APIキーをセット
        stripe.api_key = settings.STRIPE_API_KEY
        # 決済したい商品のデータをDBから取り出す。
        cart = Cart.objects.filter(id=pk, user=request.user).first()
        # 決済したい商品のデータ
        items = []
        items.append({'price_data': {'currency':'jpy', 'product_data': {'name':cart.product.name,},
                                     'unit_amount':cart.price,}, 'quantity': 1,})     
        # TODO: 配送料 + 手数料などを上乗せしておく。

        context['cart'] = cart

        # 決済したい商品データをStripeセッション作成時に与える。 ？
        session = stripe.checkout.Session.create(
            payment_method_types = ['card'],
            line_items = items,
            mode = 'payment',
            #決済成功した後のリダイレクト先。セッションidを使って、決済したかDjango側でチェックする。
            success_url = request.build_absolute_uri(reverse_lazy("market:checkout")) + "?session_id={CHECKOUT_SESSION_ID}",
                                                # uri ？                               # ?session_id クエリストリング
            #決済キャンセルしたときのリダイレクト先
            cancel_url = request.build_absolute_uri(reverse_lazy("market:index")),
        )

        #この公開鍵を使ってテンプレート上のJavaScriptにセットする。顧客が入力する情報を暗号化させるための物
        context["public_key"] = settings.STRIPE_PUBLISHABLE_KEY

        #このStripeのセッションIDをテンプレート上のJavaScriptにセットする。上記のビューで作ったセッションを顧客に渡し>て決済させるための物
        context["session_id"] = session["id"]

        return render(request, "market/session_create.html" ,context)

session_create = SessionCreateView.as_view()


# 本当にStripeで決済を済ませたのか、確認するビュー
class CheckoutView(View):
    def get(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_API_KEY

        #セッションIDがパラメータに存在するかチェック。なければエラー画面へ
        if "session_id" not in request.GET:
            return redirect("market:index")
        
        #ここでセッションの存在チェック(存在しないセッションIDを適当に入力した場合、ここでエラーが出る。)
        try:
            session = stripe.checkout.Session.retrieve(request.GET["session_id"])  # retrieve ？
            print(session)
        except:
            return redirect("market:index")
        
        #ここで決済完了かどうかチェック。(何らかの方法でセッションIDを取得し、URLに直入力した場合、ここでエラーが出る。)
        print(session.payment_status)
        if session.payment_status != "paid":
            return redirect("market:index")
        
        print("決済完了")
        #TODO: Productと決済した人を1対多で紐付ける。誰がこの商品を決済したか記録するため  Product と決済した人は１対１では？
        #TODO:できればこのページは注文完了のレンダリングを
        return redirect("market:index")
    
checkout = CheckoutView.as_view()


