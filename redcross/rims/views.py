from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.forms.models import inlineformset_factory, modelformset_factory
from rims.models import Site, InventoryItem, ProductInformation
from rims.forms import InventoryItemForm, ProductInformationForm, SiteForm, SiteListForm,ProductListForm, TitleErrorList
from redcross.settings import PAGE_SIZE

# Helper functions
def bind_inline_formset(formset):
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
def sites(request, page=1):
    sitesList=Site.objects.all().order_by('name')
    SiteFormset=modelformset_factory( Site, form=SiteListForm, fields=['Delete'], extra=0)
    if page == 'all':
        page_size = sitesList.count()
        pageNum = 1
    else:
        page_size = PAGE_SIZE
        pageNum = page
    numPages=int(sitesList.count()/page_size)
    if sitesList.count()% page_size !=0:
        numPages += 1
    if page == 'all':
        numPagesIndicator = 'all'
    else:
        numPagesIndicator = numPages
    pageNo = min(numPages,max(1,int(pageNum)))
    slicedSitesList=sitesList[(pageNo-1) * page_size: pageNo * page_size]
    numSiteErrors=0
    for site in slicedSitesList:
        if not site.check_site():
            numSiteErrors += 1
    if request.method == "POST":
        siteForms=SiteFormset(request.POST,queryset=slicedSitesList, error_class=TitleErrorList)
        if 'Delete' in request.POST:
            for siteForm in siteForms:
                if siteForm.prefix+'-'+'Delete' in request.POST:
                    sitesList = sitesList.exclude(pk=siteForm.instance.pk)
                    slicedSitesList=sitesList[(pageNo-1) * page_size: pageNo * page_size]
                    siteForm.instance.delete()
                    siteForms=SiteFormset(request.POST,queryset=slicedSitesList, error_class=TitleErrorList)
            return redirect(reverse('rims:sites',args=[page,]),
                                            {'pageNo':str(pageNo),
                                             'previousPageNo':str(max(1,pageNo-1)),
                                             'nextPageNo':str(min(pageNo+1,numPages)),
                                             'numPages': numPagesIndicator,
                                             'sitesList':slicedSitesList,
                                             'numSiteErrors':numSiteErrors,
                                             'siteForms':siteForms,
                                            })
        if 'Add' in request.POST:
            return redirect(reverse('rims:site_add'))
    else:
        siteForms=SiteFormset(queryset=slicedSitesList, error_class=TitleErrorList)
    return render(request,'rims/sites.html', {'nav_sites':1,
                                              'pageNo':str(pageNo),
                                              'previousPageNo':str(max(1,pageNo-1)),
                                              'nextPageNo':str(min(pageNo+1,numPages)),
                                              'numPages': numPagesIndicator,
                                              'sitesList':slicedSitesList,
                                              'numSiteErrors':numSiteErrors,
                                              'siteForms':siteForms,
                                              })

@login_required()
def site_detail(request, siteId=1, page=1):
    site = Site.objects.all().get(pk=siteId)
    siteInventory=site.inventoryitem_set.all().order_by('information__name')
    inventoryForms=[]
    InventoryInlineFormset=inlineformset_factory(Site,InventoryItem,extra=0, form=InventoryItemForm)
    if page == 'all':
        page_size = siteInventory.count()
        pageNum = 1
    else:
        page_size = PAGE_SIZE
        pageNum = str(page)
    numPages=max(1,int(siteInventory.count()/page_size))
    if numPages > 1 and siteInventory.count()% page_size !=0:
        numPages += 1
    pageNo = min(numPages,max(1,int(pageNum)))
    if page == 'all':
        numPagesIndicator = 'all'
        pageIndicator='all'
    else:
        numPagesIndicator = numPages
        pageIndicator=pageNo
    slicedInventory=siteInventory[(pageNo-1) * page_size: pageNo * page_size]
    slicedInventoryQueryset=site.inventoryitem_set.all().order_by('information__name')
    for inventoryItem in siteInventory:
        if inventoryItem not in slicedInventory:
            slicedInventoryQueryset=slicedInventoryQueryset.exclude(pk=inventoryItem.pk)
    if request.method == "POST":
        siteForm=SiteForm(request.POST,instance=site, error_class=TitleErrorList)
        if siteInventory.count() > 0:
            inventoryForms=InventoryInlineFormset(request.POST, queryset=slicedInventoryQueryset, instance=site, error_class=TitleErrorList)
        if 'Save Site' or 'Save Inventory' in request.POST:
            if 'Save Site' in request.POST and siteForm.is_valid():
                siteForm.save()
            if 'Save Inventory' in request.POST and inventoryForms.is_valid():
                inventoryForms.save()
            if siteForm.is_valid() or (siteInventory.count()> 0 and inventoryForms.is_valid()):
                return redirect(reverse('rims:site_detail',args=[site.number, pageIndicator]),
                                                {"nav_sites":1,
                                                'site': site,
                                                'siteForm':siteForm,
                                                'pageNo':str(pageIndicator),
                                                'previousPageNo':str(max(1,pageNo-1)),
                                                'nextPageNo':str(min(pageNo+1,numPages)),
                                                'numPages': numPagesIndicator,
                                                'inventoryForms':inventoryForms,
                                                })
    else:
        siteForm=SiteForm(site.__dict__,instance=site, error_class=TitleErrorList)
        inventoryForms=InventoryInlineFormset(instance=site, queryset=slicedInventoryQueryset, error_class=TitleErrorList)
    return render(request, 'rims/site_detail.html', {"nav_sites":1,
                                                'site': site,
                                                'siteForm':siteForm,
                                                'pageNo':str(pageIndicator),
                                                'previousPageNo':str(max(1,pageNo-1)),
                                                'nextPageNo':str(min(pageNo+1,numPages)),
                                                'numPages': numPagesIndicator,
                                                'inventoryForms':inventoryForms,
                                                })

@login_required()
def site_add(request):
    if request.method == "POST":
        if 'Save' in request.POST:
            siteForm=SiteForm(request.POST,Site(), error_class=TitleErrorList)
            if siteForm.is_valid():
                siteForm.save()
                site=siteForm.instance
                siteInventory=site.product_set.all()
                return redirect(reverse('rims:site_detail', args=[site.number,]),
                                                {"nav_sites":1,
                                                'site': site,
                                                'inventory':siteInventory,
                                                'siteForm':siteForm,
                                                })
    else:
        siteForm=SiteForm(instance=Site(), error_class=TitleErrorList)
    return render(request, 'rims/site_detail.html', {"nav_sites":1,
                                                'siteForm':siteForm,
                                                })

@login_required()
def products(request, page=1):
    productsList=ProductInformation.objects.all().order_by('name')
    ProductFormset=modelformset_factory( ProductInformation, form=ProductListForm, fields=['Delete'], extra=0)
    if page == 'all':
        page_size = productsList.count()
        pageNum = 1
    else:
        page_size = PAGE_SIZE
        pageNum = page
    numPages=int(productsList.count()/page_size)
    if productsList.count()% page_size !=0:
        numPages += 1
    if page == 'all':
        numPagesIndicator = 'all'
    else:
        numPagesIndicator = numPages
    pageNo = min(numPages,max(1,int(pageNum)))
    slicedProductsList=productsList[(pageNo-1) * page_size: pageNo * page_size]
    numProductErrors=0
    for product in slicedProductsList:
        if not product.check_product():
            numProductErrors += 1
    if request.method == 'POST':
        productForms=ProductFormset(request.POST,queryset=productsList, error_class=TitleErrorList)
        slicedProductForms=productForms[(pageNo-1) * page_size: pageNo * page_size]
        if 'Delete' in request.POST:
            for productForm in productForms:
                if productForm.prefix+'-'+'Delete' in request.POST:
                    productsList = productsList.exclude(pk=productForm.instance.pk)
                    slicedProductsList=productsList[(pageNo-1) * page_size: pageNo * page_size]
                    productForm.instance.delete()
                    productForms=ProductFormset(request.POST,queryset=slicedProductsList, error_class=TitleErrorList)
            return redirect(reverse('rims:products',args=[page,]),
                                            {'pageNo':str(pageNo),
                                             'previousPageNo':str(max(1,pageNo-1)),
                                             'nextPageNo':str(min(pageNo+1,numPages)),
                                             'numPages': numPagesIndicator,
                                             'productsList':slicedProductsList,
                                             'numProductErrors':numProductErrors,
                                             'productForms':productForms,
                                             'slicedProductForms':slicedProductForms,
                                            })
        if 'Add' in request.POST:
            return redirect(reverse('rims:product_add'))
    else:
        productForms=ProductFormset(queryset=productsList, error_class=TitleErrorList)
        slicedProductForms=productForms[(pageNo-1) * page_size: pageNo * page_size]
    return render(request,'rims/products.html', {'nav_products':1,
                                              'pageNo':str(pageNo),
                                              'previousPageNo':str(max(1,pageNo-1)),
                                              'nextPageNo':str(min(pageNo+1,numPages)),
                                              'numPages': numPagesIndicator,
                                              'productsList':slicedProductsList,
                                              'numProductErrors':numProductErrors,
                                              'productForms':productForms,
                                              'slicedProductForms':slicedProductForms,
                                              })

@login_required()
def product_detail(request, code='-1'):
    product = ProductInformation.objects.all().get(pk=code)
    productInventory=product.inventoryitem_set.all()
    InventoryInlineFormset=inlineformset_factory(Site,InventoryItem,extra=0, form=InventoryItemForm)
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

@login_required()
def product_add(request):
    if request.method == "POST":
        if 'Save' in request.POST:
            productForm=ProductInformationForm(request.POST,ProductInformation(), error_class=TitleErrorList)
            if productForm.is_valid():
                productForm.save()
                product=productForm.instance
                return redirect(reverse('rims:product_detail', args=[product.code,]),
                                                {"nav_products":1,
                                                'product': product,
                                                'productForm':productForm,
                                                })
    else:
        productForm=ProductInformationForm(instance=ProductInformation(), error_class=TitleErrorList)
    return render(request, 'rims/product_detail.html', {"nav_products":1,
                                                'productForm':productForm,
                                                })