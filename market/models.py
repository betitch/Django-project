from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(verbose_name="カテゴリ名",max_length=20)

    def __str__(self):
        return self.name                        # 管理サイトでの表示がわかりやすいようにする。


class Product(models.Model):
    # Category モデルの id を記録する
    # on_delete は紐付く Category が消された時の挙動 mocels.CASCADE カテゴリが消された時 Producut も消される。
    category = models.ForeignKey(Category,verbose_name="カテゴリ",on_delete=models.CASCADE)
    name = models.CharField(verbose_name="商品名", max_length=20)  # verbose_name は管理サイト表示用
    price = models.IntegerField(verbose_name='価格')


