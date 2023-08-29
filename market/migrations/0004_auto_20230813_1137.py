# Generated by Django 3.2.18 on 2023-08-13 02:37

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0003_remove_product_name2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.IntegerField(verbose_name='希望売却価格'),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=1000, verbose_name='メッセージ')),
                ('dt', models.DateTimeField(default=django.utils.timezone.now, verbose_name='投稿日時')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='market.product', verbose_name='商品')),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.IntegerField(verbose_name='希望売却価格')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='market.product', verbose_name='商品')),
            ],
        ),
    ]