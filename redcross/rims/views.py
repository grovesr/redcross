from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory
from django.utils.dateparse import parse_datetime, parse_date, date_re
from rims.models import Site, InventoryItem, ProductInformation,\
    parse_product_information_from_xls,\
    parse_sites_from_xls, parse_inventory_from_xls
from rims.forms import InventoryItemFormNoSite,\
ProductInformationForm, ProductInformationFormWithQuantity, SiteForm, \
SiteFormReadOnly, SiteListForm,ProductListFormWithDelete, TitleErrorList, \
DateSpanQueryForm, ProductListFormWithAdd, UploadFileForm
from redcross.settings import PAGE_SIZE
from collections import OrderedDict
import datetime
import pytz
import re

def reorder_date_mdy_to_ymd(dateString,sep):
    parts=dateString.split(sep)
    return parts[2]+"-"+parts[0]+"-"+parts[1]

# Helper functions
def parse_datestr_tz(dateTimeString,hours=0,minutes=0):
    if date_re.match(dateTimeString):
        naive=datetime.datetime.combine(parse_date(dateTimeString), datetime.time(hours,minutes))
    else:
        naive=parse_datetime(dateTimeString)
    return pytz.utc.localize(naive)

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
def home(request):
    # display most recently edited sites and inventory
    recentSites=Site.objects.filter(inventoryitem__deleted=False).order_by('-inventoryitem__modified')
    sitesList=OrderedDict()
    siteObjectsList=[]
    for recentSite in recentSites:
        sitesList[recentSite.pk]=None
        if len(sitesList)>PAGE_SIZE:
            break
    for site in sitesList.keys():
        siteObjectsList.append(Site.objects.get(pk=site))
    recentInventory=InventoryItem.objects.filter(deleted=False).order_by('-modified')
    productInformation=recentInventory.values('information')
    productInformation=productInformation.distinct()
    latestProducts=[]
    for information in productInformation:
        latestProducts.append(recentInventory.filter(information=information['information']).latest())
    for inventoryItem in recentInventory:
        if inventoryItem not in latestProducts:
            recentInventory=recentInventory.exclude(pk=inventoryItem.pk)
    inventoryList=OrderedDict()
    inventoryObjectsList=[]
    for inventoryItem in recentInventory:
        inventoryList[inventoryItem.pk]=None
        if len(inventoryList)>PAGE_SIZE:
            break
    for item in inventoryList.keys():
        inventoryObjectsList.append(InventoryItem.objects.get(pk=item))
    return render(request,'rims/home.html', {'nav_rims':1,
                                             'sitesList':siteObjectsList,
                                             'inventoryList':inventoryObjectsList
                                             })

@login_required()
def imports(request):
    warningMessage=''
    if request.method == 'POST':
        if 'Delete Sites' in request.POST:
                return site_delete_all(request)
        elif 'Delete Products' in request.POST:
                return product_delete_all(request)
        elif 'Delete Inventory' in request.POST:
                return inventory_delete_all(request)
        if 'Export Sites' in request.POST:
                return site_export(request)
        elif 'Export Products' in request.POST:
                return product_export(request)
        elif 'Export Inventory' in request.POST:
                return inventory_export(request)
        if 'file' in request.FILES:
            fileSelectForm = UploadFileForm(request.POST, request.FILES)
            if fileSelectForm.is_valid():
                if 'Import Sites' in request.POST:
                    parse_sites_from_xls(file_contents=request.FILES['file'].file.read())
                    return redirect(reverse('rims:sites', kwargs={'page':1}))
                elif 'Delete Sites' in request.POST:
                    return site_delete_all(request)
                elif 'Import Products' in request.POST:
                    parse_product_information_from_xls(file_contents=request.FILES['file'].file.read())
                    return redirect(reverse('rims:products', kwargs={'page':1}))
                elif 'Import Inventory' in request.POST:
                    parse_inventory_from_xls(file_contents=request.FILES['file'].file.read())
                    return redirect(reverse('rims:sites', kwargs={'page':1}))
                else:
                    warningMessage='Problem with input. Try again'
                    return render(request,'rims/imports.html', {'nav_imports':1,
                                                'warningMessage':warningMessage,
                                                'fileSelectForm':fileSelectForm})
        else:
            warningMessage='No file selected'
    fileSelectForm = UploadFileForm()
    return render(request,'rims/imports.html', {'nav_imports':1,
                                                'warningMessage':warningMessage,
                                                'fileSelectForm':fileSelectForm})

@login_required()
def reports_dates(request, region=None, report=None, page=1, startDate=None, stopDate=None):
    dateSpanForm=DateSpanQueryForm()
    regions=Site.objects.values('region').distinct()
    regionList=[]
    for region in regions:
        regionList.append(region['region'])
    warningMessage=''
    sitesList=None
    inventoryList=None
    if report and region and startDate and stopDate:
        parsedStartDate=parse_datestr_tz(reorder_date_mdy_to_ymd(startDate,'-'),0,0)
        parsedStopDate=parse_datestr_tz(reorder_date_mdy_to_ymd(stopDate,'-'),23,59)
        sites=Site.objects.all().order_by('name')
        sitesList = OrderedDict()
        inventoryList = {}
        for site in sites:
            siteInventory = get_latest_site_inventory(site=site, stopDate=parsedStopDate)
            sitesList[site]=siteInventory
            if re.match('inventory_detail',report) or re.match('inventory_status',report):
                for item in siteInventory:
                    if item.information not in inventoryList:
                        # accumulation list
                        inventoryList[item.information]=(list(),(0,0))
                    print inventoryList
                    siteQuantityList=inventoryList[item.information][0]
                    siteQuantityList.append((site,item.quantity,item.quantity * item.information.quantityOfMeasure))
                    newSiteQuantity = (inventoryList[item.information][1][0] + item.quantity,
                                       inventoryList[item.information][1][1] + item.quantity * item.information.quantityOfMeasure)
                    inventoryList[item.information] = (siteQuantityList, newSiteQuantity)
    if request.method == 'POST':
        beginDate=request.POST.get('startDate').replace('/','-')
        endDate=request.POST.get('stopDate').replace('/','-')
        region=request.POST.get('region')
        if 'Site Inventory Print' in request.POST:
            return redirect(reverse('rims:reports_dates',
                             kwargs={'region':region,
                                     'report':'site_inventory_print',
                                     'page':page,
                                     'startDate':beginDate,
                                     'stopDate':endDate}))
        elif 'Site Inventory XLS' in request.POST:
            return redirect(reverse('rims:reports_dates',
                             kwargs={'region':region,
                                     'report':'site_inventory_xls',
                                     'page':page,
                                     'startDate':beginDate,
                                     'stopDate':endDate}))
        elif 'Inventory Detail Print' in request.POST:
            return redirect(reverse('rims:reports_dates',
                             kwargs={'region':region,
                                     'report':'inventory_detail_print',
                                     'page':page,
                                     'startDate':beginDate,
                                     'stopDate':endDate}))
        elif 'Inventory Detail XLS' in request.POST:
            return redirect(reverse('rims:reports_dates',
                             kwargs={'region':region,
                                     'report':'inventory_detail_xls',
                                     'page':page,
                                     'startDate':beginDate,
                                     'stopDate':endDate}))
        elif 'Inventory Status Print' in request.POST:
            return redirect(reverse('rims:reports_dates',
                             kwargs={'region':region,
                                     'report':'inventory_status_print',
                                     'page':page,
                                     'startDate':beginDate,
                                     'stopDate':endDate}))
        elif 'Inventory Status XLS' in request.POST:
            return redirect(reverse('rims:reports_dates',
                             kwargs={'region':region,
                                     'report':'inventory_status_xls',
                                     'page':page,
                                     'startDate':beginDate,
                                     'stopDate':endDate}))
    return render(request,'rims/reports.html', {'nav_reports':1,
                                                'warningMessage':warningMessage,
                                                'region':region,
                                                'report':report,
                                                'dateSpanForm':dateSpanForm,
                                                'startDate':startDate,
                                                'stopDate':stopDate,
                                                'pageNo':page,
                                                'regionList':regionList,
                                                'sitesList':sitesList,
                                                'inventoryList':inventoryList,})

@login_required()
def reports(request):
    today=timezone.now()
    startDate=today.strftime('%m-%d-%Y')
    stopDate=today.strftime('%m-%d-%Y')
    return reports_dates(request, startDate=startDate, stopDate=stopDate)


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
    numPages=(max(1,numPages))
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
            sitesToDelete={}
            for siteForm in siteForms:
                if siteForm.prefix+'-'+'Delete' in request.POST:
                    sitesToDelete[siteForm.instance]=siteForm.instance.inventoryitem_set.all()
            if len(sitesToDelete) > 0:
                return site_delete(request,sitesToDelete=sitesToDelete, page=page)
            return redirect(reverse('rims:sites',kwargs={'page':page,}))
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
    site=Site.objects.get(pk=siteId)
    siteInventory=get_latest_site_inventory(site)
    InventoryFormset=modelformset_factory(InventoryItem,extra=0, can_delete=False,
                                                 form=InventoryItemFormNoSite)
    inventoryForms=InventoryFormset(queryset=siteInventory, error_class=TitleErrorList)
    siteForm=SiteForm(site.__dict__,instance=site, error_class=TitleErrorList)
    if page == 'all':
        pageSize = siteInventory.count()
        pageNum = 1
    else:
        pageSize = PAGE_SIZE
        pageNum = str(page)
    numPages=max(1,int(siteInventory.count()/pageSize))
    if numPages > 1 and siteInventory.count()% pageSize !=0:
        numPages += 1
    numPages=(max(1,numPages))
    pageNo = min(numPages,max(1,int(pageNum)))
    if page == 'all':
        numPagesIndicator = 'all'
        pageIndicator='all'
    else:
        numPagesIndicator = numPages
        pageIndicator=pageNo
    startRow=(pageNo-1) * pageSize
    stopRow=startRow+pageSize
    if request.method == "POST":
        siteForm=SiteForm(request.POST,instance=site, error_class=TitleErrorList)
        if siteInventory.count() > 0:
            inventoryForms=InventoryFormset(request.POST, queryset=siteInventory, error_class=TitleErrorList)
        if 'Save Site' or 'Save Changes' in request.POST:
            if 'Save Site' in request.POST and siteForm.is_valid():
                siteForm.save()
                return redirect(reverse('rims:site_detail',kwargs={'siteId':site.pk, 
                                                            'page':pageIndicator,}))
            if ('Save Changes' in request.POST) and inventoryForms.is_valid():
                for inventoryForm in inventoryForms:
                    inventoryForm.instance.modifier=request.user.username
                    if inventoryForm.prefix+'-'+'deleteItem' in request.POST:
                        inventoryForm.instance.deleted=True
                inventoryItems=inventoryForms.save(commit=False)
                for inventoryItem in inventoryItems:
                    newItem=inventoryItem.copy()
                    newItem.save()
                return redirect(reverse('rims:site_detail',kwargs={'siteId':site.pk, 
                                                            'page':pageIndicator,}))
            if 'Add New Inventory' in request.POST:
                return redirect(reverse('rims:site_add_inventory',kwargs={'siteId':site.pk, 'page':1}))
    return render(request, 'rims/site_detail.html', {"nav_sites":1,
                                                'site': site,
                                                'siteForm':siteForm,
                                                'startRow':startRow,
                                                'stopRow':stopRow,
                                                'pageNo':str(pageIndicator),
                                                'previousPageNo':str(max(1,pageNo-1)),
                                                'nextPageNo':str(min(pageNo+1,numPages)),
                                                'numPages': numPagesIndicator,
                                                'inventoryForms':inventoryForms,
                                                })

@login_required()
def site_add(request):
    if request.method == "POST":
        if 'Save Site' in request.POST:
            siteForm=SiteForm(request.POST,Site(), error_class=TitleErrorList)
            if siteForm.is_valid():
                siteForm.save()
                site=siteForm.instance
                return redirect(reverse('rims:site_detail', kwargs={'siteId':site.pk,
                                                                    'page': 1}))
    else:
        siteForm=SiteForm(instance=Site(), error_class=TitleErrorList)
    return render(request, 'rims/site_detail.html', {"nav_sites":1,
                                                'siteForm':siteForm,
                                                })
    
@login_required()
def site_add_inventory(request, siteId=1, page=1):
    site=Site.objects.get(pk=siteId)
    productsList=ProductInformation.objects.all().order_by('name')
    ProductFormset=modelformset_factory( ProductInformation, form=ProductListFormWithAdd, extra=0)
    if page == 'all':
        pageSize = productsList.count()
        pageNum = 1
    else:
        pageSize = PAGE_SIZE
        pageNum = page
    numPages=int(productsList.count()/pageSize)
    if productsList.count()% pageSize !=0:
        numPages += 1
    numPages=(max(1,numPages))
    if page == 'all':
        numPagesIndicator = 'all'
    else:
        numPagesIndicator = numPages
    pageNo = min(numPages,max(1,int(pageNum)))
    startRow=(pageNo-1) * pageSize
    stopRow=startRow+pageSize
    if request.method == "POST":
        productForms=ProductFormset(request.POST,queryset=productsList, error_class=TitleErrorList)
        if 'Add Products' in request.POST:
            # current inventory at this site
            siteInventory=InventoryItem.objects.filter(site=site.pk)
            productToAdd=[]
            productList=[]
            for productForm in productForms:
                if productForm.prefix+'-'+'Add' in request.POST:
                    if siteInventory.filter(information=productForm.instance.pk).count() == 0:
                        productToAdd.append(productForm.instance)
                    productList.append(productForm.instance)
            return product_add_to_site_inventory(request, siteId=site.pk,
                                                 productToAdd=productToAdd,
                                                 productList=productList,)
    else:
        siteForm=SiteFormReadOnly(instance=site, error_class=TitleErrorList)
        productForms=ProductFormset(queryset=productsList, error_class=TitleErrorList)
    return render(request, 'rims/site_add_inventory.html', {"nav_sites":1,
                                                'site':site,
                                                'siteForm':siteForm,
                                                'startRow':startRow,
                                                'stopRow':stopRow,
                                                'pageNo':str(pageNo),
                                                'previousPageNo':str(max(1,pageNo-1)),
                                                'nextPageNo':str(min(pageNo+1,numPages)),
                                                'numPages': numPagesIndicator,
                                                'productForms':productForms,
                                                })

@login_required()
def site_delete(request, sitesToDelete={}, page=1):
    if request.method == 'POST':
        if 'Delete Site' in request.POST:
            sitesToDelete=request.POST.getlist('sites')
            for siteId in sitesToDelete:
                site=Site.objects.get(pk=int(siteId))
                siteInventory=site.inventoryitem_set.all()
                for item in siteInventory:
                    item.delete()
                site.delete()
            return redirect(reverse('rims:sites', kwargs={'page':1}))
        if 'Cancel' in request.POST:
            return redirect(reverse('rims:sites', kwargs={'page':1}))
    if any([sitesToDelete[k].count()>0  for k in sitesToDelete]):
        warningMessage='One or more sites contain inventory.  Deleting the sites will delete all inventory as well. Delete anyway?'
    else:
        warningMessage='Are you sure?'
    return render(request, 'rims/site_delete.html', {"nav_sites":1,
                                                'sitesToDelete':sitesToDelete,
                                                'warningMessage':warningMessage,
                                                })

@login_required()
def site_delete_all(request):
    sites=Site.objects.all()
    sitesToDelete={}
    for site in sites:
        sitesToDelete[site]=site.inventoryitem_set.all()
    if request.method == 'POST':
        if 'Delete All Sites' in request.POST:
            sites.delete()
            siteInventory=site.inventoryitem_set.all()
            siteInventory.delete()
            return redirect(reverse('rims:imports'))
        if 'Cancel' in request.POST:
            return redirect(reverse('rims:imports'))
    if any([sitesToDelete[k].count()>0  for k in sitesToDelete]):
        warningMessage='One or more sites of ' + str(sites.count()) + ' total sites contain inventory.  Deleting the sites will delete all inventory as well. Delete anyway?'
    else:
        warningMessage='Delete all ' + str(sites.count()) + ' sites?'
    return render(request, 'rims/site_delete_all.html', {"nav_sites":1,
                                                'warningMessage':warningMessage,
                                                })

@login_required()
def site_export(request):
    return render(request, 'rims/site_export.html', {"nav_sites":1,
                                                })
    
def get_latest_site_inventory(site=None, startDate=None, stopDate=None):
    siteInventory=site.inventoryitem_set.filter(deleted=False)
    if stopDate:
        siteInventory=siteInventory.filter(modified__lte=stopDate)
    
    productInformation=siteInventory.values('information')
    productInformation=productInformation.distinct()
    latestProducts=[]
    for information in productInformation:
        latestProducts.append(siteInventory.filter(information=information['information']).latest())
    for inventoryItem in siteInventory:
        if inventoryItem not in latestProducts:
            siteInventory=siteInventory.exclude(pk=inventoryItem.pk)
    siteInventory=siteInventory.order_by('information__name')
    return siteInventory
    
@login_required()
def products(request, page=1):
    productsList=ProductInformation.objects.all().order_by('name')
    ProductFormset=modelformset_factory( ProductInformation, form=ProductListFormWithDelete, fields=['Delete'], extra=0)
    if page == 'all':
        page_size = productsList.count()
        pageNum = 1
    else:
        page_size = PAGE_SIZE
        pageNum = page
    numPages=int(productsList.count()/page_size)
    if productsList.count()% page_size !=0:
        numPages += 1
    numPages=(max(1,numPages))
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
        productForms=ProductFormset(request.POST,queryset=slicedProductsList, error_class=TitleErrorList)
        if 'Delete' in request.POST:
            productsToDelete={}
            for productForm in productForms:
                if productForm.prefix+'-'+'Delete' in request.POST:
                    productsToDelete[productForm.instance]=productForm.instance.inventoryitem_set.all()
            if len(productsToDelete) > 0:
                return product_delete(request,productsToDelete=productsToDelete, page=page)
            return redirect(reverse('rims:products',kwargs={'page':page,}))
        if 'Add' in request.POST:
            return redirect(reverse('rims:product_add'))
    else:
        productForms=ProductFormset(queryset=slicedProductsList, error_class=TitleErrorList)
    return render(request,'rims/products.html', {'nav_products':1,
                                              'pageNo':str(pageNo),
                                              'previousPageNo':str(max(1,pageNo-1)),
                                              'nextPageNo':str(min(pageNo+1,numPages)),
                                              'numPages': numPagesIndicator,
                                              'productsList':slicedProductsList,
                                              'numProductErrors':numProductErrors,
                                              'productForms':productForms,
                                              })

@login_required()
def product_detail(request, page=1, code='-1'):
    product = ProductInformation.objects.get(pk=code)
    inventorySites=product.inventoryitem_set.all().values('site').distinct()
    sitesList=[]
    for siteNumber in inventorySites:
        site = Site.objects.get(pk=siteNumber['site'])
        sitesList.append((site,site.inventory_quantity(code)))
    if page == 'all':
        page_size = len(sitesList)
        pageNum = 1
    else:
        page_size = PAGE_SIZE
        pageNum = page
    numPages=int(len(sitesList)/page_size)
    if len(sitesList)% page_size !=0:
        numPages += 1
    numPages=(max(1,numPages))
    if page == 'all':
        numPagesIndicator = 'all'
    else:
        numPagesIndicator = numPages
    pageNo = min(numPages,max(1,int(pageNum)))
    slicedSitesList=sitesList[(pageNo-1) * page_size: pageNo * page_size]
    numSiteErrors=0
    for site in slicedSitesList:
        if not site[0].check_site():
            numSiteErrors += 1
    if request.method == "POST":
        productForm=ProductInformationForm(request.POST,instance=product, error_class=TitleErrorList)
        if 'Save' in request.POST:
            if productForm.is_valid():
                productForm.save()
                return redirect(reverse('rims:product_detail',kwargs={'code':product.code,}))
    else:
        productForm=ProductInformationForm(product.__dict__,instance=product, error_class=TitleErrorList)
    return render(request, 'rims/product_detail.html',
                            {"nav_products":1,
                             'pageNo':str(pageNo),
                             'previousPageNo':str(max(1,pageNo-1)),
                             'nextPageNo':str(min(pageNo+1,numPages)),
                             'numPages': numPagesIndicator,
                             'product': product,
                             'productForm':productForm,
                             'sitesList':sitesList,
                            })

@login_required()
def product_add(request):
    productForm=ProductInformationForm(error_class=TitleErrorList)
    if request.method == "POST":
        if 'Save' in request.POST:
            productForm=ProductInformationForm(request.POST, error_class=TitleErrorList)
            if productForm.is_valid():
                productForm.save()
                product=productForm.instance
                return redirect(reverse('rims:product_detail', kwargs={'code':product.pk,
                                                                    'page': 1}))
    return render(request, 'rims/product_detail.html', {"nav_sites":1,
                                                'productForm':productForm,
                                                })
    
@login_required()
def product_add_to_site_inventory(request, siteId=1, productToAdd=None, productList=None):
    site=Site.objects.get(pk=siteId)
    ProductFormset=modelformset_factory(ProductInformation,extra=0,
                                                form=ProductInformationFormWithQuantity)
    newProduct = ProductInformation.objects.all()
    if productList:
        for productItem in newProduct:
            if productItem not in productList: 
                newProduct=newProduct.exclude(pk=productItem.pk)
    if request.method == 'POST':
        if newProduct.count() == 0:
            return redirect(reverse('rims:site_detail', kwargs={'siteId':site.pk,
                                                                'page':1}))
        if 'Save Inventory' in request.POST:
            productForms=ProductFormset(request.POST, queryset=newProduct, error_class=TitleErrorList)
            if productForms.is_valid():
                for productForm in productForms:
                    cleanedData=productForm.cleaned_data
                    inventoryItem = InventoryItem.objects.filter(information=productForm.instance
                                                                 ).filter(site=site)
                    if inventoryItem.count()>0:
                        inventoryItem=inventoryItem[0]
                        inventoryItem.quantity=int(cleanedData.get('Quantity'))
                    else:
                        inventoryItem=InventoryItem(information=productForm.instance,
                                                    site=site,
                                                    quantity=int(cleanedData.get('Quantity')))
                    inventoryItem.save()
                return redirect(reverse('rims:site_detail', kwargs={'siteId':site.pk,
                                                                    'page':1}))
        if 'Cancel' in request.POST:
            return redirect(reverse('rims:site_detail', kwargs={'siteId':site.pk,
                                                                'page':1}),
                                        )
    productForms=ProductFormset(queryset=newProduct, error_class=TitleErrorList)
    siteInventory=InventoryItem.objects.filter(site=siteId)
    for productForm in productForms:
        if productForm.instance not in productToAdd:
            inventoryItem=siteInventory.get(information__code=productForm.instance.code)
            productForm.fields['Quantity'].initial=inventoryItem.quantity
    return render(request, 'rims/product_add_to_site_inventory.html', {'nav_sites':1,
                                                     'site':site,
                                                     'productForms':productForms,
                                                     'page':1
                                                })
    
@login_required()
def product_delete(request, productsToDelete={}, page=1):
    if request.method == 'POST':
        if 'Delete Product' in request.POST:
            productsToDelete=request.POST.getlist('products')
            for code in productsToDelete:
                product=ProductInformation.objects.get(pk=code)
                productInventory=product.inventoryitem_set.all()
                for item in productInventory:
                    item.delete()
                product.delete()
            return redirect(reverse('rims:products', kwargs={'page':1}))
        if 'Cancel' in request.POST:
            return redirect(reverse('rims:products', kwargs={'page':1}))
    if any([productsToDelete[k].count()>0  for k in productsToDelete]):
        warningMessage='One or more products contain inventory.  Deleting the products will delete all inventory in all sites containing this product as well. Delete anyway?'
    else:
        warningMessage='Are you sure?'
    return render(request, 'rims/product_delete.html', {"nav_imports":1,
                                                'productsToDelete':productsToDelete,
                                                'warningMessage':warningMessage,
                                                })
    
@login_required()
def product_delete_all(request):
    products=ProductInformation.objects.all()
    productsToDelete={}
    for product in products:
        productsToDelete[product]=product.inventoryitem_set.all()
    if request.method == 'POST':
        if 'Delete All Products' in request.POST:
            for product in productsToDelete:
                productInventory=product.inventoryitem_set.all()
                for item in productInventory:
                    item.delete()
                product.delete()
            return redirect(reverse('rims:imports'))
        if 'Cancel' in request.POST:
            return redirect(reverse('rims:imports'))
    if any([productsToDelete[k].count()>0  for k in productsToDelete]):
        warningMessage='One or more products of ' + str(products.count()) + ' total products contain inventory.  Deleting the products will delete all inventory in all sites containing this product as well. Delete anyway?'
    else:
        warningMessage='Delete all ' + str(products.count()) + ' products?'
    return render(request, 'rims/product_delete_all.html', {"nav_imports":1,
                                                'warningMessage':warningMessage,
                                                })

@login_required()
def product_export(request):
    return render(request, 'rims/product_export.html', {"nav_products":1,
                                                })
    
@login_required()
def inventory_delete_all(request):
    inventory=InventoryItem.objects.all()
    if request.method == 'POST':
        if 'Delete All Inventory' in request.POST:
            inventory.delete()
            return redirect(reverse('rims:imports'))
        if 'Cancel' in request.POST:
            return redirect(reverse('rims:imports'))
    warningMessage='Delete all ' + str(inventory.count()) + ' inventory items?'
    return render(request, 'rims/inventory_delete_all.html', {"nav_imports":1,
                                                'warningMessage':warningMessage,
                                                })
    
@login_required()
def inventory_export(request):
    return render(request, 'rims/inventory_export.html', {"nav_sites":1,
                                                })
    