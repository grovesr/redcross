from django.conf.urls import patterns, url
from rims import views

urlpatterns = patterns('',
    # ex: /ups/
    url(r'^$', views.home, name='home'),
    # this will display the import
    url(r'^imports$', views.imports, name='imports'),
    # this will display inventory history un-paged with no report without dates
    url(r'^sites/(?P<siteId>\d+)/product/\s*(?P<code>[\w\d\_]+)\s*/page_(?P<page>all)$', views.inventory_history, name='inventory_history'),
    # this will display inventory history un-paged with no report without dates
    url(r'^sites/(?P<siteId>\d+)/product/\s*(?P<code>[\w\d\_]+)\s*/(?P<startDate>\d{2}-\d{2}-\d{4})/(?P<stopDate>\d{2}-\d{2}-\d{4})/page_(?P<page>all)$', views.inventory_history_dates, name='inventory_history_dates'),
    # this will display inventory history paged from page 1 with no report without dates
    url(r'^sites/(?P<siteId>\d+)/product/\s*(?P<code>[\w\d\_]+)\s*/page_(?P<page>\d+)$', views.inventory_history, name='inventory_history'),
     # this will display inventory history paged from paged with no report without dates
    url(r'^sites/(?P<siteId>\d+)/product/\s*(?P<code>[\w\d\_]+)\s*/(?P<startDate>\d{2}-\d{2}-\d{4})/(?P<stopDate>\d{2}-\d{2}-\d{4})/page_(?P<page>\d+)$', views.inventory_history_dates, name='inventory_history_dates'),
    # this will display reports page with no report without dates
    url(r'^reports$', views.reports, name='reports'),
    # this will display reports page with no report with dates
    url(r'^reports/(?P<startDate>\d{2}-\d{2}-\d{4})/(?P<stopDate>\d{2}-\d{2}-\d{4})$', views.reports_dates, name='reports_dates'),
    # this will display reports paged from page 1 with dates
    url(r'^reports/(?P<report>[\w\_]+)/(?P<startDate>\d{2}-\d{2}-\d{4})/(?P<stopDate>\d{2}-\d{2}-\d{4})$', views.reports_dates, name='reports_dates'),
    # this will display reports paged with dates
    url(r'^reports/(?P<report>[\w\_]+)/(?P<startDate>\d{2}-\d{2}-\d{4})/(?P<stopDate>\d{2}-\d{2}-\d{4})/page_(?P<page>\d+)$', views.reports_dates, name='reports_dates'),
    # this will display reports un-paged with dates
    url(r'^reports/(?P<report>[\w\_]+)/(?P<startDate>\d{2}-\d{2}-\d{4})/(?P<stopDate>\d{2}-\d{2}-\d{4})/page_(?P<page>all)$', views.reports_dates, name='reports_dates'),
    # this will display sites, paged from page 1
    url(r'^sites$', views.sites, name='sites'),
    # this will display all sites un-paged
    url(r'^sites/page_(?P<page>all)$', views.sites, name='sites'),
    # this will display sites, paged from the given page
    url(r'^sites/page_(?P<page>\d+)$', views.sites, name='sites'),
    # this will display details of a particular site with all inventory paged from page 1, passing save flags
    url(r'^sites/(?P<siteId>\d+)/s(?P<siteSave>\d)i(?P<inventorySave>\d)$', views.site_detail, name='site_detail'),
    # this will display details of a particular site with all inventory un-paged, passing save flags
    url(r'^sites/(?P<siteId>\d+)/s(?P<siteSave>\d)i(?P<inventorySave>\d)/page_(?P<page>all)$', views.site_detail, name='site_detail'),
    # this will display details of a particular site with inventory paged from the given page, passing save flags
    url(r'^sites/(?P<siteId>\d+)/s(?P<siteSave>\d)i(?P<inventorySave>\d)/page_(?P<page>\d+)$', views.site_detail, name='site_detail'),
     # this will display details of a particular site with all inventory paged from page 1
    url(r'^sites/(?P<siteId>\d+)$', views.site_detail, name='site_detail'),
    # this will display details of a particular site with all inventory un-paged
    url(r'^sites/(?P<siteId>\d+)/page_(?P<page>all)$', views.site_detail, name='site_detail'),
    # this will display details of a particular site with inventory paged from the given page
    url(r'^sites/(?P<siteId>\d+)/page_(?P<page>\d+)$', views.site_detail, name='site_detail'),
    # this is the add site page
    url(r'^sites/site_add$', views.site_add, name='site_add'),
    # this is the add site inventory page with paged products
    url(r'^sites/(?P<siteId>\d+)/site_add_inventory/page_(?P<page>\d+)$', views.site_add_inventory, name='site_add_inventory'),
    # this is the add site inventory page with un-paged
    url(r'^sites/(?P<siteId>\d+)/site_add_inventory/page_(?P<page>all)$', views.site_add_inventory, name='site_add_inventory'),
    # this is the add site inventory confirmation page
    url(r'^sites/(?P<siteId>\d+)/product_add_to_site_inventory$', views.product_add_to_site_inventory, name='product_add_to_site_inventory'),
    # this is the delete site page
    url(r'^sites/delete$', views.site_delete, name='site_delete'),
    # this is the delete all sites page
    url(r'^sites/delete_all$', views.site_delete_all, name='site_delete_all'),
    # this is the sites export page
    url(r'^sites/export$', views.site_export, name='site_export'),
    # this will display products, paged from page 1,
    url(r'^products$', views.products, name='products'),
    # this will display all products un-paged
    url(r'^products/(?P<page>all)$', views.products, name='products'),
    # this will display products, paged from the given page
    url(r'^products/page_(?P<page>\d+)$', views.products, name='products'),
    # this will display details of a particular product paged from page 1, with product save flag
    url(r'^products/product_detail/\s*(?P<code>[\w\d\_]+)\s*/p(?P<productSave>\d)$', views.product_detail, name='product_detail'),
    # this will display details of a particular product un-paged, with product save flag
    url(r'^products/product_detail/\s*(?P<code>[\w\d\_]+)\s*/p(?P<productSave>\d)/page_(?P<page>all)$', views.product_detail, name='product_detail'),
    # this will display details of a particular product paged, with product save flag
    url(r'^products/product_detail/\s*(?P<code>[\w\d\_]+)\s*/p(?P<productSave>\d)/page_(?P<page>\d+)$', views.product_detail, name='product_detail'),
    # this will display details of a particular product paged from page 1
    url(r'^products/product_detail/\s*(?P<code>[\w\d\_]+)\s*$', views.product_detail, name='product_detail'),
    # this will display details of a particular product un-paged
    url(r'^products/product_detail/\s*(?P<code>[\w\d\_]+)\s*/page_(?P<page>all)$', views.product_detail, name='product_detail'),
    # this will display details of a particular product paged
    url(r'^products/product_detail/\s*(?P<code>[\w\d\_]+)\s*/page_(?P<page>\d+)$', views.product_detail, name='product_detail'),
    # this is the add product page
    url(r'^products/product_add$', views.product_add, name='product_add'),
    # this is the delete products page
    url(r'^products/delete$', views.product_delete, name='product_delete'),
    # this is the delete all products page
    url(r'^products/delete_all$', views.product_delete_all, name='product_delete_all'),
    # this is the products export page
    url(r'^products/export$', views.product_export, name='product_export'),
    # this is the delete all inventory page
    url(r'^inventory/delete_all$', views.inventory_delete_all, name='inventory_delete_all'),
    # this is the inventory export page
    url(r'^inventory/export$', views.inventory_export, name='inventory_export'),
    )