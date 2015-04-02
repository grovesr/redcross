from django.conf.urls import patterns, url
from rims import views

urlpatterns = patterns('',
    # ex: /ups/
    url(r'^$', views.rims_home, name='rims_home'),
    url(r'^inventory$', views.inventory, name='inventory'),
    url(r'^sites$', views.sites, name='sites'),
    url(r'^products$', views.products, name='products'),
    )