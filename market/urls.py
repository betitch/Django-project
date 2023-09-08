from django.urls import path
from . import views

app_name = "market"
urlpatterns = [
    path("", views.index),
    path("index/", views.index, name="index"),
    path("mylist/<int:pk>/", views.mylist, name="mylist"),
    path("single/<int:pk>/", views.single, name="single"),    # single ページには primary key で飛ぶ前提？
    path("message/<int:pk>/", views.message, name="message"),
    path("mypage/", views.mypage, name="mypage"),
]