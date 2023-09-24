from django.urls import path
from . import views

app_name = "market"
urlpatterns = [
    path("", views.index),
    path("index/", views.index, name="index"),
    path("mylist/", views.mylist, name="mylist"),                   #　mylistにpkはいらない。request.userでできる
    path("single/<int:pk>/", views.single, name="single"),          # single ページには primary key で飛ぶ前提？
    path("product_bid_status/<int:pk>/", views.product_bid_status, name="product_bid_status"),
    path("message/<int:pk>/", views.message, name="message"),       # ページとしては single が表示されて、url は
    path("mypage/", views.mypage, name="mypage"),                   # product_bid_status/<int:pk>/ になる ？
    path("mypost/", views.mypost, name="mypost"),  
    #path("mypost/<int:pk>/", views.mypost, name="mypost_single"),    
    path("nyedit/<int:pk>", views.myedit, name="myedit"),           # url に対応する表示されるページは無くてOK？
    path("delete/<int:pk>/", views.mydelete, name="mydelete"),
    path("session_create/<int:pk>/", views.session_create, name="session_create"),
    path("checkout/", views.checkout, name="checkout"),
]