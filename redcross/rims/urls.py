from django.conf.urls import patterns, url
from rims import views

urlpatterns = patterns('',
    # ex: /ups/
    url(r'^$', views.rims_home, name='rims_home'),
    url(r'^inventory/(?P<page>\d+)$', views.paged_inventory, name='inventory'),
    url(r'^inventory$', views.paged_inventory, name='inventory'),
    # this will display sites, paged from page 1
    url(r'^sites$', views.sites, name='sites'),
    # this will display all sites un-paged
    url(r'^sites/page_(?P<page>all)$', views.sites, name='sites'),
    # this will display sites, paged from the given page
    url(r'^sites/page_(?P<page>\d+)$', views.sites, name='sites'),
    # this will display details of a particular site with all inventory paged from page 1
    url(r'^sites/(?P<siteId>\d+)$', views.site_detail, name='site_detail'),
    # this will display details of a particular site with all inventory un-paged
    url(r'^sites/(?P<siteId>\d+)/page_(?P<page>all)$', views.site_detail, name='site_detail'),
    # this will display details of a particular site with inventory paged from the given page
    url(r'^sites/(?P<siteId>\d+)/page_(?P<page>\d+)/$', views.site_detail, name='site_detail'),
    # this is the add site page
    url(r'^sites/site_add$', views.site_add, name='site_add'),
    # this will display products, paged from page 1,
    url(r'^products$', views.products, name='products'),
    # this will display all products un-paged
    url(r'^products/(?P<page>all)$', views.products, name='products'),
    # this will display products, paged from the given page
    url(r'^products/page_(?P<page>\d+)$', views.products, name='products'),
    # this will display details of a particular product
    url(r'^products/product_detail/\s*(?P<code>[\w\d\_]+)\s*$', views.product_detail, name='product_detail'),
    )