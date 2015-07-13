from django.conf.urls import patterns, include, url
from django.contrib import admin
from . import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'redcross.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^ims/',include('ims.urls',namespace='ims')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',name='login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout',name='logout'),
    url(r'^$', views.home,name='home'),
    url(r'^redcross_help$',views.redcross_help, name='redcross_help')
)
