from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory
from django.utils.dateparse import parse_datetime, parse_date, date_re
from .models import Site, InventoryItem, ProductInformation
from rims.forms import InventoryItemFormNoSite,\
ProductInformationForm, ProductInformationFormWithQuantity, SiteForm, \
SiteFormReadOnly, SiteListForm,ProductListFormWithDelete, TitleErrorList, \
DateSpanQueryForm, ProductListFormWithAdd, UploadFileForm, ProductListFormWithoutDelete
from redcross.settings import LOG_FILE
from .settings import PAGE_SIZE
from collections import OrderedDict
import datetime
import pytz
import re
    
# Helper functions
def reorder_date_mdy_to_ymd(dateString,sep):
    parts=dateString.split(sep)
    return parts[2]+"-"+parts[0]+"-"+parts[1]

def parse_datestr_tz(dateTimeString,hours=0,minutes=0):
    if date_re.match(dateTimeString):
        naive=datetime.datetime.combine(parse_date(dateTimeString), datetime.time(hours,minutes))
    else:
        naive=parse_datetime(dateTimeString)
    return pytz.utc.localize(naive)

def log_actions(modifier='unknown', modificationDate=None, modificationMessage='no message'):
    modDate=modificationDate
    if not modDate:
        modDate = timezone.now()
    logString = modDate.strftime("%m/%d/%y %H:%M:%S") + ', ' + modifier + ', ' + modificationMessage +"\n"
    #try:
    with open(LOG_FILE, 'a') as fStr:
        fStr.write(logString)
    #except:
        # failed to open file
    #    pass
    
# Create your views here.
def home(request):
    # display most recently edited sites and inventory
    recentSites = Site.recently_changed_inventory(PAGE_SIZE)
    recentInventory = InventoryItem.recently_changed(PAGE_SIZE)
    return render(request,'rims/home.html', {'nav_rims':1,
                                             'sitesList':recentSites,
                                             'inventoryList':recentInventory
                                             })

@login_required()
def imports(request):
    warningMessage=''
    canDeleteSites=request.user.has_perm('rims.delete_site')
    canAddSites=request.user.has_perm('rims.add_site')
    canDeleteProducts=request.user.has_perm('rims.delete_productinformation')
    canAddProducts=request.user.has_perm('rims.add_productinformation')
    canDeleteInventory=request.user.has_perm('rims.delete_inventoryitem')
    canAddInventory=request.user.has_perm('rims.add_inventoryitem')
    canChangeProducts=request.user.has_perm('rims.change_product')
    canChangeSites=request.user.has_perm('rims.change_site')
    canChangeInventory=request.user.has_perm('rims.change_inventoryitem')
    #canDeleteSites=True
    #canDeleteProducts=True
    #canDeleteInventory=True
    #canAddSites=True
    #canAddProducts=True
    #canAddInventory=True
    #canChangeProducts=True
    #canChangeSites=True
    #canChangeInventory=True
    if request.method == 'POST':
        if 'Delete Sites' in request.POST:
            if canDeleteSites and canDeleteInventory:
                return site_delete_all(request)
            else:
                warningMessage='You don''t have permission to delete sites or inventory'
        if 'Delete Products' in request.POST:
            if canDeleteProducts and canDeleteInventory:
                return product_delete_all(request)
            else:
                warningMessage='You don''t have permission to delete products or inventory'
        if 'Delete Inventory' in request.POST:
            if canDeleteInventory:
                return inventory_delete_all(request)
            else:
                warningMessage='You don''t have permission to delete inventory'
        if 'Export Sites' in request.POST:
                warningMessage='Site export not yet implemented'
                return site_export(request,warningMessage=warningMessage)
        elif 'Export Products' in request.POST:
                warningMessage='Product export not yet implemented'
                return product_export(request,warningMessage=warningMessage)
        elif 'Export Inventory' in request.POST:
                warningMessage='Inventory export not yet implemented'
                return inventory_export(request,warningMessage=warningMessage)
        if 'file' in request.FILES:
            fileSelectForm = UploadFileForm(request.POST, request.FILES)
            if fileSelectForm.is_valid():
                if 'Import Sites' in request.POST:
                    if canAddSites and canChangeSites:
                        result=Site.parse_sites_from_xls(file_contents=request.FILES['file'].file.read(),
                                                    modifier=request.user.username)
                        if result == -1:
                            warningMessage=('Error while trying to import sites from spreadsheet "' + 
                            request.FILES['file'].name + '"')
                            log_actions(modifier=request.user.username,
                                                  modificationDate=timezone.now(),
                                                  modificationMessage=warningMessage)
                        else:
                            log_actions(modifier=request.user.username,
                                                  modificationDate=timezone.now(),
                                                  modificationMessage='successful bulk import of sites using "' + 
                                                  request.FILES['file'].name +'"')
                            return redirect(reverse('rims:sites', kwargs={'page':1}))
                    else:
                        warningMessage='You don''t have permission to import sites'
                if 'Import Products' in request.POST:
                    if canAddProducts and canChangeProducts:
                        result=ProductInformation.parse_product_information_from_xls(file_contents=request.FILES['file'].file.read(),
                                                                  modifier=request.user.username)
                        if result == -1:
                            warningMessage=('Error while trying to import products from spreadsheet "' + 
                            request.FILES['file'].name +'"')
                            log_actions(modifier=request.user.username,
                                                  modificationDate=timezone.now(),
                                                  modificationMessage=warningMessage)
                        else:
                            log_actions(modifier=request.user.username,
                                                  modificationDate=timezone.now(),
                                                  modificationMessage='successful bulk import of products using "' + 
                                                  request.FILES['file'].name +'"')
                            return redirect(reverse('rims:products', kwargs={'page':1}))
                    else:
                        warningMessage='You don''t have permission to import products'
                if 'Import Inventory' in request.POST:
                    if canAddInventory and canChangeInventory:
                        result=InventoryItem.parse_inventory_from_xls(file_contents=request.FILES['file'].file.read(),
                                                                  modifier=request.user.username)
                        if result == -1:
                            warningMessage=('Error while trying to import inventory from spreadsheet "' + 
                            request.FILES['file'].name +'"')
                            log_actions(modifier=request.user.username,
                                                  modificationDate=timezone.now(),
                                                  modificationMessage=warningMessage)
                        else:
                            log_actions(modifier=request.user.username,
                                                  modificationDate=timezone.now(),
                                                  modificationMessage='successful bulk import of inventory using "' + 
                                                  request.FILES['file'].name +'"')
                            return redirect(reverse('rims:sites', kwargs={'page':1}))
                    else:
                        warningMessage='You don''t have permission to import inventory'
        else:
            if ('Import Sites' in request.POST or 'Import Products' in request.POST or
                'Import Inventory' in request.POST or
                'Export Sites' in request.POST or 'Export Products' in request.POST or
                'Export Inventory' in request.POST):
                warningMessage='No file selected'
    fileSelectForm = UploadFileForm()
    return render(request,'rims/imports.html', {'nav_imports':1,
                                                'warningMessage':warningMessage,
                                                'fileSelectForm':fileSelectForm,
                                                'canImportSites':canAddSites and canChangeSites,
                                                'canImportProducts':canAddProducts and canChangeProducts,
                                                'canImportInventory':canAddInventory and canChangeInventory,
                                                'canDeleteSites':canDeleteSites and canDeleteInventory,
                                                'canDeleteProducts':canDeleteProducts and canDeleteInventory,
                                                'canDeleteInventory':canDeleteInventory,
                                                })

@login_required()
def reports_dates(request, report=None, page=1, startDate=None, stopDate=None):
    dateSpanForm=DateSpanQueryForm()
    infoMessage=''
    warningMessage=''
    sitesList=None
    inventoryList=None
    if report and startDate and stopDate:
        parsedStartDate=parse_datestr_tz(reorder_date_mdy_to_ymd(startDate,'-'),0,0)
        parsedStopDate=parse_datestr_tz(reorder_date_mdy_to_ymd(stopDate,'-'),23,59)
        sites=Site.objects.all().order_by('name')
        sitesList = OrderedDict()
        inventoryList = {}
        if re.match('site_detail',report):
            # site detail reports don't contain inventory details, just get
            # the site data and pass it to the template for rendering
            sitesList=sites
        else:
            # other reports require information about the inventory at each site
            for site in sites:
                siteInventory = site.latest_inventory(stopDate=parsedStopDate)
                sitesList[site]=siteInventory
                if re.match('inventory_detail',report) or re.match('inventory_status',report):
                    # these reports require details about each inventory item
                    # contained at each site
                    for item in siteInventory:
                        if item.information not in inventoryList:
                            # accumulation list
                            inventoryList[item.information]=(list(),(0,0))
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
                             kwargs={'report':'site_inventory_print',
                                     'page':page,
                                     'startDate':beginDate,
                                     'stopDate':endDate}))
        elif 'Site Inventory XLS' in request.POST:
            return redirect(reverse('rims:reports_dates',
                             kwargs={'report':'site_inventory_xls',
                                     'page':page,
                                     'startDate':beginDate,
                                     'stopDate':endDate}))
        elif 'Site Detail Print' in request.POST:
            return redirect(reverse('rims:reports_dates',
                             kwargs={'report':'site_detail_print',
                                     'page':page,
                                     'startDate':beginDate,
                                     'stopDate':endDate}))
        elif 'Site Detail XLS' in request.POST:
            return redirect(reverse('rims:reports_dates',
                             kwargs={'report':'site_detail_xls',
                                     'page':page,
                                     'startDate':beginDate,
                                     'stopDate':endDate}))
        elif 'Inventory Detail Print' in request.POST:
            return redirect(reverse('rims:reports_dates',
                             kwargs={'report':'inventory_detail_print',
                                     'page':page,
                                     'startDate':beginDate,
                                     'stopDate':endDate}))
        elif 'Inventory Detail XLS' in request.POST:
            return redirect(reverse('rims:reports_dates',
                             kwargs={'report':'inventory_detail_xls',
                                     'page':page,
                                     'startDate':beginDate,
                                     'stopDate':endDate}))
        elif 'Inventory Status Print' in request.POST:
            return redirect(reverse('rims:reports_dates',
                             kwargs={'report':'inventory_status_print',
                                     'page':page,
                                     'startDate':beginDate,
                                     'stopDate':endDate}))
        elif 'Inventory Status XLS' in request.POST:
            return redirect(reverse('rims:reports_dates',
                             kwargs={'report':'inventory_status_xls',
                                     'page':page,
                                     'startDate':beginDate,
                                     'stopDate':endDate}))
    return render(request,'rims/reports.html', {'nav_reports':1,
                                                'warningMessage':warningMessage,
                                                'infoMessage':infoMessage,
                                                'report':report,
                                                'dateSpanForm':dateSpanForm,
                                                'startDate':startDate,
                                                'stopDate':stopDate,
                                                'pageNo':page,
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
    warningMessage=''
    canDelete=request.user.has_perm('rims.delete_site') and request.user.has_perm('rims.delete_inventoryitem')
    canAdd=request.user.has_perm('rims.add_site')
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
            if canDelete:
                sitesToDelete={}
                for siteForm in siteForms:
                    if siteForm.prefix+'-'+'Delete' in request.POST:
                        sitesToDelete[siteForm.instance]=siteForm.instance.inventoryitem_set.all()
                if len(sitesToDelete) > 0:
                    return site_delete(request,sitesToDelete=sitesToDelete, page=page)
                return redirect(reverse('rims:sites',kwargs={'page':page,}))
            else:
                warningMessage='You don''t have permission to delete sites'
        if 'Add' in request.POST:
            if canAdd:
                return redirect(reverse('rims:site_add'))
            else:
                warningMessage='You don''t have permission to add sites'
    siteForms=SiteFormset(queryset=slicedSitesList, error_class=TitleErrorList)
    if len(slicedSitesList) == 0:
        warningMessage='No sites found'
    return render(request,'rims/sites.html', {'nav_sites':1,
                                              'pageNo':str(pageNo),
                                              'previousPageNo':str(max(1,pageNo-1)),
                                              'nextPageNo':str(min(pageNo+1,numPages)),
                                              'numPages': numPagesIndicator,
                                              'numSiteErrors':numSiteErrors,
                                              'siteForms':siteForms,
                                              'warningMessage':warningMessage,
                                              'canAdd':canAdd,
                                              'canDelete':canDelete,
                                              })

@login_required()
def site_detail(request, siteId=1, page=1, siteSave=0, inventorySave=0):
    infoMessage=''
    if int(siteSave):
        infoMessage='Successfully added or changed site'
    if int(inventorySave):
        infoMessage='Successfully changed site inventory'
    warningMessage=''
    canAdd=request.user.has_perm('rims.add_inventoryitem')
    canChangeInventory=request.user.has_perm('rims.change_inventoryitem')
    canChangeSite=request.user.has_perm('rims.change_site')
    canDelete=request.user.has_perm('rims.delete_inventoryitem')
    site=Site.objects.get(pk=siteId)
    siteInventory=site.latest_inventory()
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
            if 'Save Site' in request.POST:
                if canChangeSite:
                    if siteForm.is_valid():
                        siteForm.instance.modifier=request.user.username
                        siteForm.save()
                        log_actions(modifier=request.user.username,
                                  modificationDate=timezone.now(),
                                  modificationMessage='changed site information for ' + str(siteForm.instance))
                        return redirect(reverse('rims:site_detail',kwargs={'siteId':site.pk, 
                                                                'page':pageIndicator,
                                                                'inventorySave':0,
                                                                'siteSave':1}))
                    else:
                        warningMessage='More information required before the site can be saved'
                else:
                    warningMessage='You don''t have permission to change site information'
            if ('Save Changes' in request.POST):
                if canChangeInventory and canDelete:
                    if inventoryForms.is_valid():
                        inventoryItems=[]
                        for inventoryForm in inventoryForms:
                            inventoryForm.instance.modifier=request.user.username
                            if inventoryForm.prefix+'-'+'deleteItem' in request.POST:
                                inventoryForm.instance.deleted=True
                        inventoryItems=inventoryForms.save(commit=False)
                        for inventoryItem in inventoryItems:
                            newItem=inventoryItem.copy()
                            newItem.save()
                        siteInventory=site.latest_inventory()
                        inventoryForms=InventoryFormset(queryset=siteInventory, error_class=TitleErrorList)
                        return redirect(reverse('rims:site_detail',kwargs={'siteId':site.pk, 
                                                                'page':pageIndicator,
                                                                'inventorySave':1,
                                                                'siteSave':0,}))
                    else:
                        warningMessage='More information required before the inventory can be changed'
                else:
                    warningMessage='You don''t have permission to change or delete inventory'
            if 'Add New Inventory' in request.POST:
                if canAdd:
                    return redirect(reverse('rims:site_add_inventory',kwargs={'siteId':site.pk, 'page':1}))
                else:
                    warningMessage='You don''t have permission to add inventory'
        siteForm=SiteForm(site.__dict__,instance=site, error_class=TitleErrorList)
        inventoryForms=InventoryFormset(queryset=siteInventory, error_class=TitleErrorList)
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
                                                'canAdd':canAdd,
                                                'canChangeInventory':canChangeInventory,
                                                'canChangeSite':canChangeSite,
                                                'canDelete':canDelete,
                                                'warningMessage':warningMessage,
                                                'infoMessage':infoMessage
                                                })

@login_required()
def site_add(request):
    warningMessage=''
    canAdd=request.user.has_perm('rims.add_site')
    if request.user.has_perm('rims.add_site'):
        if request.method == "POST":
            if 'Save Site' in request.POST:
                if canAdd:
                    siteForm=SiteForm(request.POST,Site(), error_class=TitleErrorList)
                    if siteForm.is_valid():
                        siteForm.instance.modifier=request.user.username
                        siteForm.save()
                        site=siteForm.instance
                        return redirect(reverse('rims:site_detail', kwargs={'siteId':site.pk,
                                                                            'page': 1,
                                                                            'siteSave':1,
                                                                            'inventorySave':0,}))
                    return render(request, 'rims/site_detail.html', {"nav_sites":1,
                                                'canChangeSite':canAdd,
                                                'siteForm':siteForm,
                                                'warningMessage':warningMessage,
                                                })
                else:
                    warningMessage='You don''t have permission to add sites'
    else:
        warningMessage='You don''t have permission to add sites'
    siteForm=SiteForm(instance=Site(), error_class=TitleErrorList)
    return render(request, 'rims/site_detail.html', {"nav_sites":1,
                                                'canChangeSite':canAdd,
                                                'siteForm':siteForm,
                                                'warningMessage':warningMessage,
                                                })
    
@login_required()
def site_add_inventory(request, siteId=1, page=1):
    warningMessage=''
    canAdd=request.user.has_perm('rims.add_inventoryitem')
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
    if canAdd:
        if request.method == "POST":
            productForms=ProductFormset(request.POST,queryset=productsList, error_class=TitleErrorList)
            if 'Add Products' in request.POST:
                if canAdd:
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
                warningMessage='You don''t have permission to add site inventory'
    else:
        warningMessage='You don''t have permission to add site inventory'
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
                                                'warningMessage':warningMessage,
                                                'canAdd':canAdd,
                                                })

@login_required()
def site_delete(request, sitesToDelete={}, page=1):
    warningMessage=''
    canDelete=request.user.has_perm('rims.delete_site')
    if request.method == 'POST':
        if 'Delete Site' in request.POST:
            if canDelete:
                sitesToDelete=request.POST.getlist('sites')
                for siteId in sitesToDelete:
                    site=Site.objects.get(pk=int(siteId))
                    siteInventory=site.inventoryitem_set.all()
                    for item in siteInventory:
                        item.delete()
                    log_actions(modifier=request.user.username,
                                          modificationDate=timezone.now(),
                                          modificationMessage='deleted site and all associated inventory for site number ' + 
                                          str(site.pk) + ' with name ' + site.name)
                    site.delete()
                return redirect(reverse('rims:sites', kwargs={'page':1}))
        if 'Cancel' in request.POST:
            return redirect(reverse('rims:sites', kwargs={'page':1}))
    if canDelete:
        if any([sitesToDelete[k].count()>0  for k in sitesToDelete]):
            warningMessage='One or more sites contain inventory.  Deleting the sites will delete all inventory as well. Delete anyway?'
        else:
            warningMessage='Are you sure?'
    else:
            warningMessage='You don''t have permission to delete sites'
            sitesToDelete=[]
    return render(request, 'rims/site_delete.html', {"nav_sites":1,
                                                'sitesToDelete':sitesToDelete,
                                                'warningMessage':warningMessage,
                                                'canDelete':canDelete,
                                                })

@login_required()
def site_delete_all(request):
    sites=Site.objects.all()
    warningMessage=''
    canDelete=request.user.has_perm('rims.delete_site')
    if request.method == 'POST':
        if 'Delete All Sites' in request.POST:
            if canDelete:
                sites=Site.objects.all()
                inventoryItems=InventoryItem.objects.all()
                sites.delete()
                log_actions(modifier=request.user.username,
                                          modificationDate=timezone.now(),
                                          modificationMessage='deleted all sites and inventory')
                inventoryItems.delete()
                return redirect(reverse('rims:imports'))
        if 'Cancel' in request.POST:
            return redirect(reverse('rims:imports'))
    if canDelete:
        warningMessage='Delete all ' + str(sites.count()) + ' sites?  This will delete all inventory as well.'
    else:
        warningMessage='You don''t have permission to delete sites or inventory' 
    return render(request, 'rims/site_delete_all.html', {"nav_sites":1,
                                                'warningMessage':warningMessage,
                                                'canDelete':canDelete,
                                                })

@login_required()
def site_export(request, warningMessage=''):
    return render(request, 'rims/site_export.html', {"nav_sites":1,
                                                     'warningMessage':warningMessage,
                                                })
    
@login_required()
def products(request, page=1):
    warningMessage=''
    canAdd=request.user.has_perm('rims.add_productinformation')
    canDelete=request.user.has_perm('rims.delete_productinformation')
    if canDelete:
        ProductFormset=modelformset_factory( ProductInformation, form=ProductListFormWithDelete, extra=0)
    else:
        ProductFormset=modelformset_factory( ProductInformation, form=ProductListFormWithoutDelete, extra=0)
    productsList=ProductInformation.objects.all().order_by('name')
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
            if canDelete:
                productsToDelete={}
                for productForm in productForms:
                    if productForm.prefix+'-'+'Delete' in request.POST:
                        productsToDelete[productForm.instance]=productForm.instance.inventoryitem_set.all()
                if len(productsToDelete) > 0:
                    return product_delete(request,productsToDelete=productsToDelete, page=page)
                return redirect(reverse('rims:products',kwargs={'page':page,}))
            else:
                warningMessage='You don''t have permission to delete products'
        if 'Add' in request.POST:
            if canAdd:
                return redirect(reverse('rims:product_add'))
            else:
                warningMessage='You don''t have permission to add products'
    productForms=ProductFormset(queryset=slicedProductsList, error_class=TitleErrorList)
    if len(slicedProductsList) == 0:
        warningMessage='No products found'
    return render(request,'rims/products.html', {'nav_products':1,
                                              'pageNo':str(pageNo),
                                              'previousPageNo':str(max(1,pageNo-1)),
                                              'nextPageNo':str(min(pageNo+1,numPages)),
                                              'numPages': numPagesIndicator,
                                              'productsList':slicedProductsList,
                                              'numProductErrors':numProductErrors,
                                              'productForms':productForms,
                                              'canAdd':canAdd,
                                              'canDelete':canDelete,
                                              'warningMessage':warningMessage,
                                              })

@login_required()
def product_detail(request, page=1, code='-1', productSave=0):
    infoMessage=''
    if productSave:
        infoMessage='Successfully added or changed product'
    warningMessage=''
    canChange=request.user.has_perm('rims.change_productinformation')
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
            if canChange:
                if productForm.is_valid():
                    productForm.instance.modifier=request.user.username
                    productForm.save()
                    log_actions(modifier=request.user.username,
                                  modificationDate=timezone.now(),
                                  modificationMessage='changed product information for ' + str(productForm.instance))
                    return redirect(reverse('rims:product_detail', 
                                            kwargs={'code':product.code,
                                                    'productSave':1,}))
            else:
                warningMessage='You don''t have permission to change product information'
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
                             'canChange':canChange,
                             'warningMessage':warningMessage,
                             'infoMessage':infoMessage,
                            })

@login_required()
def product_add(request):
    warningMessage=''
    canAdd=request.user.has_perm('rims.add_productinformation')
    productForm=ProductInformationForm(error_class=TitleErrorList)
    if request.method == "POST":
        if 'Save' in request.POST:
            if canAdd:
                productForm=ProductInformationForm(request.POST, error_class=TitleErrorList)
                if productForm.is_valid():
                    productForm.instance.modifier=request.user.username
                    productForm.save()
                    product=productForm.instance
                    return redirect(reverse('rims:product_detail', kwargs={'code':product.pk,
                                                                        'page': 1,
                                                                        'productSave':1}))
    if not canAdd:
        warningMessage='You don''t have permission to add new products'
    return render(request, 'rims/product_detail.html', {"nav_products":1,
                                                'productForm':productForm,
                                                'canAdd':canAdd,
                                                'warningMessage':warningMessage
                                                })
    
@login_required()
def product_add_to_site_inventory(request, siteId=1, productToAdd=None, productList=None):
    canAdd=request.user.has_perm('rims.add_inventoryitem')
    warningMessage=''
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
            if canAdd:
                productForms=ProductFormset(request.POST, queryset=newProduct, error_class=TitleErrorList)
                if productForms.is_valid():
                    for productForm in productForms:
                        cleanedData=productForm.cleaned_data
                        site.add_inventory(information=productForm.instance,
                                           site=site,
                                           quantity=int(cleanedData.get('Quantity')),
                                           modifier=request.user.username,)
                    return redirect(reverse('rims:site_detail', kwargs={'siteId':site.pk,
                                                                        'page':1}))
        if 'Cancel' in request.POST:
            return redirect(reverse('rims:site_detail', kwargs={'siteId':site.pk,
                                                                'page':1}),
                                        )
    if not canAdd:
        warningMessage='You don''t have permission to add to site inventory'
    productForms=ProductFormset(queryset=newProduct, error_class=TitleErrorList)
    siteInventory=InventoryItem.objects.filter(site=siteId)
    for productForm in productForms:
        if productForm.instance not in productToAdd:
            inventoryItem=siteInventory.get(information__code=productForm.instance.code)
            productForm.fields['Quantity'].initial=inventoryItem.quantity
    return render(request, 'rims/product_add_to_site_inventory.html', {'nav_sites':1,
                                                     'site':site,
                                                     'productForms':productForms,
                                                     'page':1,
                                                     'warningMessage':warningMessage,
                                                     'canAdd':canAdd,
                                                })
    
@login_required()
def product_delete(request, productsToDelete={}, page=1):
    warningMessage=''
    canDeleteProduct=request.user.has_perm('rims.delete_productinformation')
    canDeleteInventory=request.user.has_perm('rims.delete_inventoryitem')
    if request.method == 'POST':
        if 'Delete Product' in request.POST:
            if canDeleteProduct and canDeleteInventory:
                productsToDelete=request.POST.getlist('products')
                for code in productsToDelete:
                    product=ProductInformation.objects.get(pk=code)
                    productInventory=product.inventoryitem_set.all()
                    for item in productInventory:
                        item.delete()
                    log_actions(modifier=request.user.username,
                                          modificationDate=timezone.now(),
                                          modificationMessage='deleted product and associated inventory for product code ' + 
                                          str(product.pk) + ' with name ' + product.name)
                    product.delete()
                return redirect(reverse('rims:products', kwargs={'page':1}))
                
        if 'Cancel' in request.POST:
            return redirect(reverse('rims:products', kwargs={'page':1}))
    if canDeleteProduct and canDeleteInventory:
        if any([productsToDelete[k].count()>0  for k in productsToDelete]):
            warningMessage='One or more products contain inventory.  Deleting the products will delete all inventory in all sites containing this product as well. Delete anyway?'
        else:
            warningMessage='Are you sure?'
    else:
        warningMessage = 'You don''t have permission to delete products or inventory'
        productsToDelete=[]
    
    return render(request, 'rims/product_delete.html', {"nav_products":1,
                                                'productsToDelete':productsToDelete,
                                                'warningMessage':warningMessage,
                                                'canDelete':canDeleteProduct and canDeleteInventory,
                                                })
    
@login_required()
def product_delete_all(request):
    canDelete=False
    products=ProductInformation.objects.all()
    if request.method == 'POST':
        if 'Delete All Products' in request.POST:
            if request.user.has_perms(['rims.inventoryitem_delete','rims.productinformation_delete']):
                products=ProductInformation.objects.all()
                inventoryItems=InventoryItem.objects.all()
                inventoryItems.delete()
                products.delete()
                log_actions(modifier=request.user.username,
                                          modificationDate=timezone.now(),
                                          modificationMessage='deleted all products inventory')
                return redirect(reverse('rims:imports'))
            else:
                warningMessage = 'You don''t have permission to delete products or inventory'
                return render(request, 'rims/product_delete_all.html', {"nav_imports":1,
                                                    'warningMessage':warningMessage,
                                                    'canDelete':canDelete,
                                                    })
        if 'Cancel' in request.POST:
            return redirect(reverse('rims:imports'))
    if request.user.has_perms(['rims.inventoryitem_delete','rims.productinformation_delete']):
        canDelete=True
        warningMessage='Delete all ' + str(products.count()) + ' products? This will delete all inventory as well.'
    else:
        warningMessage = 'You don''t have permission to delete products or inventory'
    return render(request, 'rims/product_delete_all.html', {"nav_imports":1,
                                                'warningMessage':warningMessage,
                                                'canDelete':canDelete,
                                                })

@login_required()
def product_export(request, warningMessage=''):
    return render(request, 'rims/product_export.html', {"nav_products":1,
                                                        'warningMessage':warningMessage,
                                                })
    
@login_required()
def inventory_delete_all(request):
    canDelete=False
    inventory=InventoryItem.objects.all()
    if request.method == 'POST':
        if 'Delete All Inventory' in request.POST:
            if request.user.has_perms('rims.inventoryitem_delete'):
                inventory.delete()
                log_actions(modifier=request.user.username,
                                          modificationDate=timezone.now(),
                                          modificationMessage='deleted all inventory')
                return redirect(reverse('rims:imports'))
            else:
                warningMessage='You don''t have permission to delete inventory'
                return render(request, 'rims/inventory_delete_all.html', {"nav_imports":1,
                                                        'warningMessage':warningMessage,
                                                        'canDelete':canDelete,
                                                        })
        if 'Cancel' in request.POST:
            return redirect(reverse('rims:imports'))
    if request.user.has_perms('rims.inventoryitem_delete'):
        canDelete=True
        warningMessage='Delete all ' + str(inventory.count()) + ' inventory items?'
    else:
        warningMessage='You don''t have permission to delete inventory'
    return render(request, 'rims/inventory_delete_all.html', {"nav_imports":1,
                                                'warningMessage':warningMessage,
                                                'canDelete':canDelete,
                                                })
    
@login_required()
def inventory_export(request, warningMessage=''):
    return render(request, 'rims/inventory_export.html', {"nav_sites":1,
                                                          'warningMessage':warningMessage,
                                                })
    