from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from xlrdutils import xlrdutils
import re
from collections import OrderedDict
from __builtin__ import classmethod

# Create your models here.

########################################################
# these are the base models which other models reference
########################################################

class Site(models.Model):
    """
    Red Cross Site model
    """
    number=models.AutoField(primary_key=True,
                               help_text="unique site number")
    name=models.CharField(max_length=50, default="",
                            help_text="Name of this site")
    county=models.CharField(max_length=50, default='',
                          help_text="County where site is located")
    address1=models.CharField(max_length=50, default="",
                                  help_text="First street address of this site")
    address2=models.CharField(max_length=50, default="",
                                  null=True, blank=True,
                                  help_text="Second street address of this site")
    address3=models.CharField(max_length=50, default="",
                                  null=True, blank=True,
                                  help_text="Third street address of this site")
    contactName=models.CharField(max_length=50, default="",
                                 help_text="Primary contact name")
    contactPhone=models.CharField(max_length=25, default="",
                                  help_text="Primary contact phone number")
    notes=models.TextField(default="", help_text="Additional information about the site",
                           null=True, blank=True)
    modified=models.DateTimeField(auto_now=True, auto_now_add=True,
                                  help_text='last modified on this date')
    modifier=models.CharField(max_length=50, default="admin", blank=True,
                              help_text='user that last modified this record')
    
    @classmethod
    def recently_changed_inventory(cls,numSites=20):
        """
        list of sites that had inventory changes recently.  Limit to numSites.
        """
        recentInventory=InventoryItem.objects.order_by('-modified',
                                      '-modifiedMicroseconds',).values('site_id')
        sitesList=OrderedDict()
        for inventoryItem in recentInventory:
            sitesList[cls.objects.get(pk=inventoryItem['site_id'])]=None
            if len(sitesList)>=numSites:
                break
        return sitesList.keys()
    
    @classmethod
    def import_sites_from_xls(cls,filename=None, file_contents=None):
        workbook=xlrdutils.open_workbook(filename=filename, file_contents=file_contents)
        data=xlrdutils.read_lines(workbook,headerKeyText='Site Number')
        return (data, workbook)
    
    @classmethod
    def parse_sites_from_xls(cls,filename=None, file_contents=None, modifier=''):
        """
        read in an excel file containing site information and populate the Sites table
        """
        data, workbook=cls.import_sites_from_xls(filename=filename, file_contents=file_contents)
        if data == -1 or workbook == -1:
            return -1
        keys=data.keys()
        sites=[]
        for indx in range(len(data[keys[0]])):
            site=Site()
            site.modifier=modifier
            for header in keys:
                value=data[header][indx]
                tableHeader=site.convert_header_name(header)
                if tableHeader ==-1:
                    continue
                if value==0 or value:
                    value=site.convert_value(tableHeader,value)
                    setattr(site,tableHeader,value)
            site.save()
            sites.append(site)
        return sites
    
    def __unicode__(self):
        return self.name + ' (' + str(self.number) + ')'
    
    def add_inventory(self,product=None, quantity=0, deleted=0, modifier="admin"):
        """
        Add a new inventory item change record for the site
        """
        if not product:
            return None
        inventoryItem=InventoryItem(information=product,
                                    site=self,
                                    quantity=quantity,
                                    deleted=deleted,
                                    modifier=modifier,)
        inventoryItem.save()
        return inventoryItem
    
    def convert_header_name(self,name):
        if re.match('^.*?site\s*name',name,re.IGNORECASE):
            return 'name'
        elif re.match('^.*?site\s*number',name,re.IGNORECASE):
            return 'number'
        elif re.match('^.*?site\s*address\s*1',name,re.IGNORECASE):
            return 'address1'
        elif re.match('^.*?site\s*address\s*2',name,re.IGNORECASE):
            return 'address2'
        elif re.match('^.*?site\s*address\s*3',name,re.IGNORECASE):
            return 'address3'
        elif re.match('^.*?site\s*contact\s*name',name,re.IGNORECASE):
            return 'contactName'
        elif re.match('^.*?site\s*phone',name,re.IGNORECASE):
            return 'contactPhone'
        elif re.match('^.*?site.*?notes',name,re.IGNORECASE):
            return 'notes'
        elif re.match('^\s*county\s*$',name,re.IGNORECASE):
            return'county'
        return -1

    def convert_value(self,key,value):
        if isinstance(getattr(self,key),bool):
            return value==1
        elif isinstance(getattr(self,key),int):
            return int(value)
        elif isinstance(getattr(self,key),long):
            return long(value)
        elif isinstance(getattr(self,key),str):
            return str(value)
        elif isinstance(getattr(self,key),unicode):
            if key == 'contactPhone' and isinstance(value,float):
                return unicode(int(value))
            return unicode(value)
        elif re.match('^.*date',key,re.IGNORECASE):
            return value
        if key=='number':
            return long(value)
        return -1
    
    def total_inventory(self):
        items = self.inventoryitem_set.all()
        count=0
        for item in items:
            count += item.quantity
        return count
    
    def inventory_quantity(self,code):
        items = self.inventoryitem_set.all()
        for item in items:
            if code == item.information.code:
                return item.quantity
        return 0
    
    def check_site(self):
        """
        check to see if any required fields are empty
        """
        try:
            self.full_clean()
        except ValidationError:
            return False
        return True
    
    def num_inventory_errors(self):
        products = self.product_set.all()
        count=0
        for product in products:
            count += product.num_errors()
        return count
    
    def latest_inventory(self, startDate=None, stopDate=None):
        # get the inventory entries associated with this site. These are records
        # detailing the history of inventory states for products at this site.  Includes
        # adjustments to inventory as well as deletions
        siteInventory=self.inventoryitem_set.all()
        if stopDate:
            # if we have a stop date, use it to filter the inventory, so we don't get
            # anything after the stop date
            siteInventory=siteInventory.filter(modified__lte=stopDate)
        # get the unique set of product information associated with the inventory
        # at this site
        productInformation=siteInventory.values('information')
        productInformation=productInformation.distinct()
        latestInventory=[]
        # for each product information get the latest inventory entry for this product
        for information in productInformation:
            latest = siteInventory.filter(information=information['information']).order_by('-modified','-modifiedMicroseconds')
            latest = latest[0]
            # if the inventory for this product was not deleted as it's latest state,
            # then add it to the latestInventory list
            if not latest.deleted:
                latestInventory.append(latest)
        # now look through the site inventory and remove any inventory that was deleted
        # as its last state.  We do this because we need a queryset, not a list
        # because we are using it to generate a formset later
        #TODO: figure out a better way of doing this
        for inventoryItem in siteInventory:
            if inventoryItem not in latestInventory:
                siteInventory=siteInventory.exclude(pk=inventoryItem.pk)
        siteInventory=siteInventory.order_by('information__name')
        return siteInventory

class ProductInformation(models.Model):
    """
    Red Cross inventory InventoryItem Information model
    """
    BALE='BALE'
    BOX='BOX'
    CARTON='CARTON'
    CASE='CASE'
    EACH = 'EACH'
    PACKAGE='PACKAGE'
    unitOfMeasureChoices = (
        (BALE, 'BALE'),
        (BOX, 'BOX'),
        (CARTON, 'CARTON'),
        (CASE,'CASE'),
        (EACH,'EACH'),
        (PACKAGE,'PACKAGE')
    )
    unitOfMeasure=models.CharField(max_length=10, default=EACH, choices=unitOfMeasureChoices,
                                    help_text="How are these measured (EACH, BOX, ...)?")
    code=models.CharField(max_length=10, default="D11", primary_key=True,
                                 help_text="Unique Red Cross code for this product")
    name=models.CharField(max_length=50, default="",
                                 help_text="Name of this product")
    expendable=models.BooleanField(default=False, help_text="Is this product expendable?")
    quantityOfMeasure=models.IntegerField(default=1,
                                          help_text="How many individual items in each package?")
    costPerItem=models.DecimalField(default=0.00, decimal_places=2, max_digits=7,
                                    blank=True, null=True,
                                    help_text="How much does each individual item cost?")
    cartonsPerPallet=models.IntegerField(default=0, blank=True, null=True,
                                         help_text="How many of these units fit on one pallet?")
    doubleStackPallets=models.BooleanField(default=False,
                                           help_text="Can pallets containing these products be stacked?")
    warehouseLocation=models.CharField(max_length=10, default="",
                                       blank=True, null=True,
                                       help_text="location of this item in the warehouse")
    canExpire=models.BooleanField(default=False,
                                  help_text="Can this product expire?")
    expirationDate=models.DateField(blank=True, null=True, help_text="What is the expiration date, if any?")
    expirationNotes=models.TextField(default="", blank=True, null=True,
                                     help_text="Special expiration notes for this product")
    modified=models.DateTimeField(auto_now=True, auto_now_add=True,
                                  help_text='last modified on this date')
    modifier=models.CharField(max_length=50, default="admin", blank=True,
                              help_text='user that last modified this record')
    
    def __unicode__(self):
        return self.name+" ("+self.code+")"
    
    @classmethod
    def import_product_information_from_xls(cls,filename=None, file_contents=None):
        workbook=xlrdutils.open_workbook(filename=filename, file_contents=file_contents)
        data=xlrdutils.read_lines(workbook,headerKeyText='Product Code')
        return (data, workbook)
    
    @classmethod
    def parse_product_information_from_xls(cls,filename=None, file_contents=None, modifier=''):
        """
        read in an excel file containing product information and populate the ProductInformation table
        """
        data, workbook=cls.import_product_information_from_xls(filename=filename, file_contents=file_contents)
        if data == -1 or workbook == -1:
            return -1
        keys=data.keys()
        products=[]
        for indx in range(len(data[keys[0]])):
            productInformation=ProductInformation()
            productInformation.modifier=modifier
            for header in keys:
                value=data[header][indx]
                tableHeader=productInformation.convert_header_name(header)
                if tableHeader ==-1:
                    continue
                if value==0 or value:
                    value=productInformation.convert_value(tableHeader,value)
                    if re.match('^.*?date.*',tableHeader,re.IGNORECASE):
                        value=xlrdutils.parse_date(workbook,value)
                    setattr(productInformation,tableHeader,value)
            if productInformation.expirationDate != None and productInformation.expirationDate != '':
                productInformation.canExpire=True
            else:
                productInformation.canExpire=False
            productInformation.save()
            products.append(productInformation)
        return products
    
    def convert_header_name(self,name):
        if re.match('^.*?product\s*code',name,re.IGNORECASE):
            return 'code'
        elif re.match('^.*?product\s*name',name,re.IGNORECASE):
            return 'name'
        elif re.match('^.*?non\s*expendable',name,re.IGNORECASE):
            return 'expendable'
        elif re.match('^.*?unit\s*of\s*measure',name,re.IGNORECASE):
            return 'unitOfMeasure'
        elif re.match('^.*?qty\s*of\s*measure',name,re.IGNORECASE):
            return 'quantityOfMeasure'
        elif re.match('^.*?cost\s*each',name,re.IGNORECASE):
            return 'costPerItem'
        elif re.match('^.*?cartons\s*per\s*pallet',name,re.IGNORECASE):
            return 'cartonsPerPallet'
        elif re.match('^.*?double\s*stack\s*pallets',name,re.IGNORECASE):
            return 'doubleStackPallets'
        elif re.match('^.*?warehouse\s*location',name,re.IGNORECASE):
            return 'warehouseLocation'
        elif re.match('^.*?expiration\s*date',name,re.IGNORECASE):
            return 'expirationDate'
        elif re.match('^.*?expiration\s*notes',name,re.IGNORECASE):
            return 'expirationNotes'
        return -1

    def convert_value(self,key,value):
        if isinstance(getattr(self,key),bool):
            if re.match('^.*?non/s*expendable',key,re.IGNORECASE):
                return value != 1
            return value==1
        elif isinstance(getattr(self,key),int):
            return int(value)
        elif isinstance(getattr(self,key),float):
            return float(value)
        elif isinstance(getattr(self,key),str):
            return str(value.strip())
        elif isinstance(getattr(self,key),unicode):
            return unicode(value.strip())
        elif re.match('^.*date',key,re.IGNORECASE):
            return value
        return -1
    
    def check_product(self):
        """
        check to see if any required fields are empty
        """
        try:
            self.full_clean()
        except ValidationError:
            return False
        return True
    
    def num_errors(self):
#TODO: add code to check for errors
        return 0

###########################################################
#  The below models have relations to the base models above
###########################################################

class InventoryItem(models.Model):
    """
    Red Cross Inventory InventoryItem
    """
    
    class Meta():
        get_latest_by='modified'
    information=models.ForeignKey(ProductInformation,
                                  help_text="The detailed information about this product type")
    site=models.ForeignKey(Site,
                           help_text="The site containing this inventory")
    quantity=models.IntegerField(default=0,
                                 help_text="Number of inventory units (each, boxes, cases, ...) of this type at the site containing this product")
    deleted=models.BooleanField(default=False)
    modified=models.DateTimeField(auto_now=True, auto_now_add=True,
                                  help_text='last modified on this date')
    modifiedMicroseconds=models.IntegerField(default=0,
                                             help_text='modification microsecond offset')
    modifier=models.CharField(max_length=50, default="admin", blank=True,
                              help_text='user that last modified this record')
    @classmethod
    def recently_changed(cls,numInventory=20):
        """
        list of recently changed inventory.
        """
        recentInventory=InventoryItem.objects.order_by('-modified',
                                      '-modifiedMicroseconds',).values('pk','information')
        inventoryList=OrderedDict()
        for inventoryItem in recentInventory:
            if not inventoryList.has_key(ProductInformation.objects.get(pk=inventoryItem['information'])):
                inventoryList[ProductInformation.objects.get(pk=inventoryItem['information'])]=InventoryItem.objects.get(pk=inventoryItem['pk'])
            if len(inventoryList)>=numInventory:
                break
        return inventoryList.values()
    
    @classmethod
    def import_inventory_from_xls(cls,filename=None, file_contents=None):
        workbook=xlrdutils.open_workbook(filename=filename, file_contents=file_contents)
        data= xlrdutils.read_lines(workbook,headerKeyText='Product Code')
        return (data, workbook)

    
    @classmethod
    def parse_inventory_from_xls(cls, filename=None, file_contents=None, modifier=''):
        """
        read in an excel file containing product inventory information and populate the InventoryItem table
        """
        data, workbook=cls.import_inventory_from_xls(filename=filename, file_contents=file_contents)
        if data == -1 or workbook == -1:
            return -1
        keys=data.keys()
        for indx in range(len(data[keys[0]])):
            inventoryItem=InventoryItem()
            inventoryItem.modifier=modifier
            for header in keys:
                value=data[header][indx]
                tableHeader=inventoryItem.convert_header_name(header)
                if tableHeader == -1:
                    if re.match('^.*?product\s*code',header,re.IGNORECASE):
                        inventoryItem.code=value.strip()
                    elif re.match('^.*?prefix',header,re.IGNORECASE):
                        inventoryItem.prefix=value.strip()
                    else:
                        continue
                else:
                    if value==0 or value:
                        if re.match('^.*?site',tableHeader):
                            inventoryItem.site_id=value
                        else:
                            value=inventoryItem.convert_value(tableHeader,value)
                            setattr(inventoryItem,tableHeader,value)
            try:
                if not re.match('p',inventoryItem.prefix,re.IGNORECASE):
                    continue
                if inventoryItem.linkToInformation() == -1 or inventoryItem.linkToSite() == -1:
                    continue
            except AttributeError:
                return -1
            # check to see if this item already exists at this site, if so add to it
            latestExistingInventory=inventoryItem.latest_inventory_at_site(site=inventoryItem.site)
            if latestExistingInventory:
                inventoryItem.quantity = inventoryItem.quantity + latestExistingInventory.quantity
            inventoryItem.save()
    
    def __unicode__(self):
        return self.information.name+"("+str(self.information.code)+"-"+str(self.quantity)+")"
    
    def save(self):
        # add in microseconds offset to make sure we can distinguish order of saves
        self.modifiedMicroseconds=timezone.now().microsecond
        super(self.__class__,self).save()
        
    
    def latest_inventory_at_site(self,site=None):
        """
        last inventory change at the site with the same product info.
        """
        lastInventory=InventoryItem.objects.filter(
                           site=site).filter(
                           information=self.information).order_by('-modified',
                                      '-modifiedMicroseconds',)
        if lastInventory.count() == 0:
            return None
        return lastInventory[0]
    
    def convert_header_name(self,name):
        if re.match('^.*?site\s*number',name,re.IGNORECASE):
            return 'site'
        elif re.match('^.*?cartons\s*$',name,re.IGNORECASE):
            return 'quantity'
        return -1

    def convert_value(self,key,value):
        if isinstance(getattr(self,key),bool):
            return value==1
        elif isinstance(getattr(self,key),int):
            return int(value)
        elif isinstance(getattr(self,key),str):
            return str(value)
        elif isinstance(getattr(self,key),unicode):
            return unicode(value)
        elif re.match('^.*date',key,re.IGNORECASE):
            return value
        elif re.match('^.*site',key,re.IGNORECASE):
            return value
        return -1

    def linkToInformation(self):
        if hasattr(self, 'code'):
            info=ProductInformation.objects.filter(pk=self.code)
            if info.count():
                self.information=info[0]
                return 0
        return -1
            
    def linkToSite(self):
        site=Site.objects.filter(pk=self.site_id)
        if site.count():
            self.site=site[0]
        else:
            return -1
        return 0
            
    def num_errors(self):
        return self.information.num_errors()
        
    def check_quantity(self):
        return self.num_errors()==0
    
    def check_information(self):
        return self.information.num_errors()==0
    
    def copy(self):
        newItem=InventoryItem(information=self.information,
                              site=self.site,
                              quantity=self.quantity,
                              deleted=self.deleted,
                              modifier=self.modifier,
                              )
        return newItem
    
    def pieces(self):
        return self.quantity * self.information.quantityOfMeasure
    