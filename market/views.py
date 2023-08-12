from django.shortcuts import render
from django.views import View
from .models import Product,Category


# Create your views here.
class IndexView(View):
    def get(self, request, *args, **kwargs):

        context = {}

        context["products"] = Product.objects.all()



        return render(request, "market/index.html", context)
    
index = IndexView.as_view()

class SingleView(View):
    def get(self, request, pk, *args, **kwargs):

        product = Product.objects.filter(id=pk).first()
        context = {"products":product}

        return render(request, "market/single.html", context)
    
single = SingleView.as_view()
