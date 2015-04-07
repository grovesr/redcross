from django.conf.urls import patterns, url
from rims import views

urlpatterns = patterns('',
    # ex: /ups/
    url(r'^$', views.rims_home, name='rims_home'),
    url(r'^inventory/(?P<page>\d+)$', views.paged_inventory, name='inventory'),
    url(r'^inventory$', views.paged_inventory, name='inventory'),
    url(r'^sites/(?P<page>\d+)$', views.paged_sites, name='paged_sites'),
    url(r'^sites$', views.sites, name='sites'),
    url(r'^sites/site_detail/(?P<siteId>\d+)$', views.site_detail, name='site_detail'),
    url(r'^sites/site_inventory/(?P<siteId>\d+)$', views.site_inventory, name='site_inventory'),
    url(r'^products/(?P<page>\d+)$', views.paged_products, name='paged_products'),
    url(r'^products$', views.products, name='products'),
    url(r'^products/product_detail/(?P<productId>[\w\d_]+)$', views.product_detail, name='product_detail'),
    )