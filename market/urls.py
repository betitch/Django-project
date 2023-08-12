from django.urls import path
from . import views

app_name = "market"
urlpatterns = [
    path("", views.index),
    path("single/<int:pk>/", views.single, name="single"),
]