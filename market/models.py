from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User     # Django デフォルトの User クラスがある 


class Category(models.Model):
    name = models.CharField(verbose_name="カテゴリ名",max_length=20)

    def __str__(self):
        return self.name                        # 管理サイトでの表示がわかりやすいようにする。


class Product(models.Model):
    # Category モデルの id （プライマリーキー？）を記録する
    # on_delete は紐付く Category が消された時の挙動 mocels.CASCADE カテゴリが消された時 Producut も消される。
    category = models.ForeignKey(Category,verbose_name="カテゴリ",on_delete=models.CASCADE, blank=True)  # blank=True にするものは通常？
    name = models.CharField(verbose_name="商品名", max_length=20, blank=True)  # verbose_name は管理サイト表示用
    price = models.IntegerField(verbose_name='希望売却価格', blank=True)   

    # １対多でユーザーモデルと紐つける。 ユーザーはクラスを作らなくて良い。
    user = models.ForeignKey(User, verbose_name='出品者', on_delete=models.SET_NULL, null=True, blank=True)  # 最初 on_delete=models.SET_NULL　になっていたが何故？
                                                                                                
    image = models.ImageField(verbose_name="商品画像", blank=True, default='noImage.png')
    description = models.CharField(verbose_name="商品説明", max_length=200, blank=True)

    # 入札期限を投稿時に入れる。入札期限を設けない場合にも対応させる。
    # 現在時刻と比較して、過ぎていれば、入札できないようにする。
    deadline = models.DateTimeField(verbose_name="入札期限", blank=True)

    # Trueで入札できる、Falseで入札できない(Falseの状態で落札できるようにする)
    # これがFalseのとき、最高値で入札したユーザーの落札が決定。
    is_bid  = models.BooleanField(verbose_name="入札できる", default=False)


    def __str__(self):            # これがあるから、index.html で product 変数を出力させると
        return self.name          # name が出力されるのか。     ← どうもそうらしい。      


    # TODO:このProductに紐付いているCartを取り出したい場合、モデルメソッドを作って、テンプレートで呼び出す。   
    def carts(self):
        return Cart.objects.filter(product=self.id)
    
    
class Cart(models.Model):
    product = models.ForeignKey(Product, verbose_name="商品", on_delete=models.CASCADE)  # 外部キー
    price = models.IntegerField(verbose_name='希望購入価格')

    # １対多でユーザーモデルと紐つける。
    user = models.ForeignKey(User, verbose_name='購入希望者', on_delete=models.CASCADE, null=True, blank=True)


class Message(models.Model):
    product = models.ForeignKey(Product, verbose_name="商品", on_delete=models.CASCADE)
    content = models.CharField(verbose_name="メッセージ", max_length=1000)

    dt = models.DateTimeField(verbose_name="投稿日時", default=timezone.now)
    # １対多でユーザーモデルと紐つける。
    user = models.ForeignKey(User, verbose_name='投稿者', on_delete=models.SET_NULL, null=True, blank=True)


# 注文とセッションidを記録する
class Order(models.Model):
    dt = models.DateTimeField(verbose_name="注文日時", default=timezone.now)
    # 1対1 フィールド (商品1つに対して、注文は1個)
    product = models.OneToOneField(Product, verbose_name="商品", on_delete=models.CASCADE)
    # 1対多 フィールド
    user = models.ForeignKey(User, verbose_name="購入希望者", on_delete=models.CASCADE)
    session_id = models.TextField(verbose_name="session id")
    payment_dt = models.DateTimeField(verbose_name="支払い日時", null=True, blank=True)
    delivery_dt = models.DateTimeField(verbose_name="配送日時", null=True, blank=True)

