from django.shortcuts import render

def home(request):
    return render(request,'base/base.html',{'nav_home':1})

def redcross_help(request):
    return render(request,'base/redcross_help.html',{'nav_help':1})