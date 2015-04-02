from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required()
def rims_home(request):
    return render(request,'rims/rims_home.html',{'home':1,})

def inventory(request):
    return render(request,'rims/inventory.html',{'inventory':1,})

def sites(request):
    return render(request,'rims/sites.html',{'sites':1,})

def products(request):
    return render(request,'rims/products.html',{'products':1,})