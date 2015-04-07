from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.forms.models import inlineformset_factory
from rims.models import Site, Product, ProductInformation
from rims.forms import ProductForm, ProductInformationForm, SiteForm, TitleErrorList
from redcross.settings import PAGE_SIZE

# Helper functions
def bind_formset(formset):
    """
    Bind initial data to a formset
    """
    if formset.is_bound:
        # do nothing if the formset is already bound
        return formset
    
    bindData={}
    # the formset.get_default_prefix() and form.add_prefix() methods add in the 
    # dict keys that uniquely identify the various form fields with the individual 
    # instance data
    
    # add formset management form data
    bindData[formset.get_default_prefix()+"-TOTAL_FORMS"]=str(formset.management_form['TOTAL_FORMS'].value())
    bindData[formset.get_default_prefix()+"-INITIAL_FORMS"]=str(formset.management_form['INITIAL_FORMS'].value())
    bindData[formset.get_default_prefix()+"-MIN_NUM_FORMS"]=str(formset.management_form['MIN_NUM_FORMS'].value())
    bindData[formset.get_default_prefix()+"-MAX_NUM_FORMS"]=str(formset.management_form['MAX_NUM_FORMS'].value())
    for form in formset:
        if form.instance:
            # field data, get these values from the instance
            for fieldName,fieldValue in form.fields.iteritems():
                try:
                    bindData[form.add_prefix(fieldName)]=getattr(form.instance,
                                                                 fieldName)
                except AttributeError:
                    # this is an added field (i.e. DELETE), not derived from the
                    # model, do nothing with it, since we are only binding instance
                    # data to the form
                    pass
            # hidden field data, get these from the field initial values set
            # when the form was created
            for field in form.hidden_fields():
                bindData[form.add_prefix(field.name)]=field.field.initial
    # create a new bound formset by passing in the bindData dict, this looks
    # to the formset constructor like a request.POST dict 
    newFormset=formset.__class__(bindData,instance=formset.instance,
                                 error_class=formset.error_class)
    return newFormset
# Create your views here.
@login_required()
def rims_home(request):
    return render(request,'rims/rims_home.html', {'nav_rims':1,})

@login_required()
def inventory(request):
    return render(request,'rims/inventory.html', {'nav_inventory':1,})

@login_required()
def paged_inventory(request, page='1'):
    return render(request,'rims/inventory.html', {'nav_inventory':1,})

@login_required()
def sites(request):
    sitesList=Site.objects.all().order_by('name')
    numPages=int(sitesList.count()/PAGE_SIZE)
    if sitesList.count()% PAGE_SIZE !=0:
        numPages += 1
    sitesList=sitesList[0:PAGE_SIZE]
    return render(request,'rims/sites.html', {'nav_sites':1,
                                              'pageNo':1,
                                              'previousPageNo':1,
                                              'nextPageNo':min(2,numPages),
                                              'numPages': numPages,
                                             'sitesList':sitesList})

@login_required()
def paged_sites(request, page=1):
    sitesList=Site.objects.all().order_by('name')
    numPages=int(sitesList.count()/PAGE_SIZE)
    if sitesList.count()% PAGE_SIZE !=0:
        numPages += 1
    pageNo = min(numPages,max(1,int(page)))
    sitesList=sitesList[(pageNo-1) * PAGE_SIZE: pageNo * PAGE_SIZE]
    return render(request,'rims/sites.html', {'nav_sites':1,
                                              'pageNo':str(pageNo),
                                              'previousPageNo':str(max(1,pageNo-1)),
                                              'nextPageNo':str(min(pageNo+1,numPages)),
                                              'numPages': numPages,
                                              'sitesList':sitesList})

@login_required()
def site_detail(request, siteId):
    site = Site.objects.all().get(pk=siteId)
    siteInventory=site.product_set.all()
    if request.method == "POST":
        siteForm=SiteForm(request.POST,instance=site, error_class=TitleErrorList)
        if 'Save' in request.POST:
            if siteForm.is_valid():
                siteForm.save()
                return redirect(reverse('rims:site_detail',args=[site.number,]),
                                                {"nav_sites":1,
                                                'site': site,
                                                'inventory':siteInventory,
                                                'siteForm':siteForm,
                                                })
    else:
        siteForm=SiteForm(site.__dict__,instance=site, error_class=TitleErrorList)
    return render(request, 'rims/site_detail.html', {"nav_sites":1,
                                                'site': site,
                                                'inventory':siteInventory,
                                                'siteForm':siteForm,
                                                })
    
@login_required()
def site_inventory(request, siteId):
    site = Site.objects.all().get(pk=siteId)
    siteInventory=site.product_set.all()
    ProductInlineFormset=inlineformset_factory(Site,Product,extra=0, form=ProductForm)
    if request.method == "POST":
        productsForms=ProductInlineFormset(request.POST,instance=site, error_class=TitleErrorList)
        if 'Save' in request.POST:
            if productsForms.is_valid():
                productsForms.save()
                return redirect(reverse('rims:site_inventory',args=[site.number,]),
                                                {"nav_sites":1,
                                                'site': site,
                                                'inventory':siteInventory,
                                                'productsForms':productsForms,
                                                })
    else:
        productsForms=ProductInlineFormset(instance=site, error_class=TitleErrorList)
        productsForms=bind_formset(productsForms)
    return render(request, 'rims/site_inventory.html', {"nav_sites":1,
                                                'site': site,
                                                'inventory':siteInventory,
                                                'productsForms':productsForms,
                                                })

@login_required()
def products(request):
    productsList=ProductInformation.objects.all().order_by('name')
    numPages=int(productsList.count()/PAGE_SIZE)
    if productsList.count()% PAGE_SIZE !=0:
        numPages += 1
    productsList=productsList[0:PAGE_SIZE]
    return render(request,'rims/products.html', {'nav_products':1,
                                                 'pageNo':1,
                                                 'previousPageNo':1,
                                                 'nextPageNo':min(2,numPages),
                                                 'numPages': numPages,
                                                 'productsList':productsList})

@login_required()
def paged_products(request, page='1'):
    productsList=ProductInformation.objects.all().order_by('name')
    numPages=int(productsList.count()/PAGE_SIZE)
    if productsList.count()% PAGE_SIZE !=0:
        numPages += 1
    pageNo = min(numPages,max(1,int(page)))
    productsList=productsList[(pageNo-1) * PAGE_SIZE: pageNo * PAGE_SIZE]
    return render(request,'rims/products.html', {'nav_products':1,
                                              'pageNo':str(pageNo),
                                              'previousPageNo':str(max(1,pageNo-1)),
                                              'nextPageNo':str(min(pageNo+1,numPages)),
                                              'numPages': numPages,
                                              'productsList':productsList})

@login_required()
def product_detail(request, productId):
    product = ProductInformation.objects.all().get(pk=productId)
    if request.method == "POST":
        productForm=ProductInformationForm(request.POST,instance=product, error_class=TitleErrorList)
        if 'Save' in request.POST:
            if productForm.is_valid():
                productForm.save()
                return redirect(reverse('rims:product_detail',args=[product.code,]),
                                                {"nav_products":1,
                                                'product': product,
                                                'productForm':productForm,
                                                })
    else:
        productForm=ProductInformationForm(product.__dict__,instance=product, error_class=TitleErrorList)
    return render(request, 'rims/product_detail.html',
                            {"nav_products":1,
                            'product': product,
                            'productForm':productForm,
                            })
    