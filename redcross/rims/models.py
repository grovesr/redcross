from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_datetime
from django.conf import settings
from xlrdutils import xlrdutils
import re
import pytz
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
    modified=models.DateTimeField(default=None, blank=True,
                                  help_text='last modified on this date')
    modifiedMicroseconds=models.IntegerField(default=0,
                                             help_text='modification microsecond offset')
    modifier=models.CharField(max_length=50, default="admin", blank=True,
                              help_text='user that last modified this record')
    
    @classmethod
    def recently_changed_inventory(cls,numSites=20):
        """
        list of sites that had inventory changes recently.  Limit to numSites.
        """
        recentInventory=InventoryItem.objects.all()
        recentInventoryList=[]
        for item in recentInventory:
            recentInventoryList.append(item)
        # latest inventory changes to the top of the list
        recentInventoryList.sort(reverse=True)
        sitesList=[]
        for inventoryItem in recentInventoryList:
            if inventoryItem.site not in sitesList:
                sitesList.append(inventoryItem.site)
        return sitesList[:numSites]
    
    @classmethod
    def import_sites_from_xls(cls,filename=None, file_contents=None):
        workbook=xlrdutils.open_workbook(filename=filename, file_contents=file_contents)
        data=xlrdutils.read_lines(workbook, sheet="Sites", headerKeyText='Site Address 1')
        return (data, workbook)
    
    @classmethod
    def parse_sites_from_xls(cls,filename=None, file_contents=None, modifier=''):
        """
        read in an excel file containing site information and populate the Sites table
        """
        #TODO: accumulate messages about import status and display
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
            if site.modified and not site.modified.tzinfo:
                site.modified=pytz.utc.localize(site.modified)
            site.save()
            sites.append(site)
        return sites
    
    def __unicode__(self):
        return self.name + ' (' + str(self.number) + ')'
    
    def save(self):
        # add in microseconds offset to make sure we can distinguish order of saves
        if not self.modified:
            self.modified=timezone.now()
        self.modifiedMicroseconds=self.modified.microsecond
        super(self.__class__,self).save()
    
    def __lt__(self,other):
        return self.timestamp() < other.timestamp()
    
    def timestamp(self):
        return parse_datetime(self.modified.strftime("%FT%H:%M:%S")+"." + '%06d' % self.modifiedMicroseconds+self.modified.strftime("%z"))
    
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
        items = self.latest_inventory()
        count=0
        for item in items:
            count += item.quantity
        return count
    
    def inventory_quantity(self,code):
        items = self.latest_inventory()
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
        latestInventoryIds=[]
        # for each product information get the latest inventory entry for this product
        for information in productInformation:
            inventoryItems = siteInventory.filter(information=information['information'])
            inventoryList=[]
            for item in inventoryItems:
                inventoryList.append(item)
            inventoryList.sort(reverse=True)
            latest = inventoryList[0]
            # if the inventory for this product was not deleted as it's latest state,
            # then add it to the latestInventory list
            if not latest.deleted:
                latestInventoryIds.append(latest.pk)
        # now look through the site inventory and remove any inventory that was deleted
        # as its last state.  We do this because we need a queryset, not a list
        # because we are using it to generate a formset later
        siteInventory=InventoryItem.objects.filter(pk__in=latestInventoryIds)
        siteInventory=siteInventory.order_by('information__code')
        return siteInventory
    
    def inventory_history_for_product(self,code=None, stopDate=None):
        """
        all inventory changes at the site with the same product info.
        """
        if stopDate:
            inventory=InventoryItem.objects.filter(
                               site=self).filter(
                               information=code).filter(modified__lte=stopDate)
        else:
            inventory=InventoryItem.objects.filter(
                               site=self).filter(information=code)
        inventoryList=[]
        for item in inventory:
            inventoryList.append(item)
        return inventoryList
    
    def product_in_inventory_history(self,item=None, stopDate=None):
        """
        check to see if the inventory change record is in this site's history
        """
        if stopDate:
            inventory=InventoryItem.objects.filter(
                               site=self).filter(
                               information=item.information).filter(modified__lte=stopDate)
        else:
            inventory=InventoryItem.objects.filter(
                               site=self).filter(information=item.information)
        for existingItem in inventory:
            print existingItem
            print existingItem.modified
            print item.modified
            if existingItem.equal(item):
                return True
        return False
    
    def latest_inventory_for_product(self,code=None):
        """
        last inventory change at the site with this product info.
        Don't include an item if it was deleted.
        """
        lastInventory=InventoryItem.objects.filter(
                           site=self).filter(
                           information=code)
        if lastInventory.count() == 0:
            return None
        inventoryList=[]
        for item in lastInventory:
            inventoryList.append(item)
        inventoryList.sort(reverse=True)
        if inventoryList[0].deleted:
            return None
        return lastInventory[0]

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
    modified=models.DateTimeField(default=None, blank=True,
                                  help_text='last modified on this date')
    modifiedMicroseconds=models.IntegerField(default=0,
                                             help_text='modification microsecond offset')
    modifier=models.CharField(max_length=50, default="admin", blank=True,
                              help_text='user that last modified this record')
    
    @classmethod
    def import_product_information_from_xls(cls,filename=None, file_contents=None):
        workbook=xlrdutils.open_workbook(filename=filename, file_contents=file_contents)
        data=xlrdutils.read_lines(workbook, sheet='Products', headerKeyText='Unit of Measure')
        return (data, workbook)
    
    @classmethod
    def parse_product_information_from_xls(cls,filename=None, file_contents=None, modifier=''):
        """
        read in an excel file containing product information and populate the ProductInformation table
        """
        #TODO: accumulate messages about import status and display
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
                    elif re.match('^code$',tableHeader,re.IGNORECASE):
                        value=value.strip().upper()
                    setattr(productInformation,tableHeader,value)
            if productInformation.expirationDate != None and productInformation.expirationDate != '':
                productInformation.canExpire=True
            else:
                productInformation.canExpire=False
            if productInformation.modified and not productInformation.modified.tzinfo:
                productInformation.modified=pytz.utc.localize(productInformation.modified)
            productInformation.save()
            products.append(productInformation)
        return products
    
    def __unicode__(self):
        return self.name+" ("+self.code+")"
    
    def save(self):
        # add in microseconds offset to make sure we can distinguish order of saves
        if not self.modified:
            self.modified=timezone.now()
        self.modifiedMicroseconds=self.modified.microsecond
        super(self.__class__,self).save()
    
    def timestamp(self):
        return parse_datetime(self.modified.strftime("%FT%H:%M:%S")+"." + '%06d' % self.modifiedMicroseconds+self.modified.strftime("%z"))
    
    def __lt__(self,other):
        return self.timestamp() < other.timestamp()
    
    def convert_header_name(self,name):
        if re.match('^.*?product\s*code',name,re.IGNORECASE):
            return 'code'
        elif re.match('^.*?product\s*name',name,re.IGNORECASE):
            return 'name'
        elif re.match('^.*expendable.*',name,re.IGNORECASE):
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
    
    def expendable_number(self):
        if self.expendable:
            return 1
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
    modified=models.DateTimeField(default=None, blank=True,
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
        recentInventory=InventoryItem.objects.all()
        recentInventoryList=[]
        for item in recentInventory:
            recentInventoryList.append(item)
        recentInventoryList.sort(reverse=True)
        inventoryList=OrderedDict()
        for inventoryItem in recentInventoryList:
            if not inventoryList.has_key(inventoryItem.information):
                inventoryList[inventoryItem.information]=inventoryItem
            if len(inventoryList)>=numInventory:
                break
        return inventoryList.values()
    
    @classmethod
    def import_inventory_from_xls(cls,filename=None, file_contents=None):
        workbook=xlrdutils.open_workbook(filename=filename, file_contents=file_contents)
        data= xlrdutils.read_lines(workbook, sheet='Inventory' ,headerKeyText='Cartons', zone=settings.TIME_ZONE)
        return (data, workbook)

    
    @classmethod
    def parse_inventory_from_xls(cls, filename=None, file_contents=None, modifier='', retainModDate=True):
        """
        read in an excel file containing product inventory information and populate the InventoryItem table
        """
        #TODO: accumulate messages about import status and display
        data, workbook=cls.import_inventory_from_xls(filename=filename, file_contents=file_contents)
        if data == -1 or workbook == -1:
            return -1
        keys=data.keys()
        inventoryItems=[]
        for indx in range(len(data[keys[0]])):
            inventoryItem=InventoryItem()
            inventoryItem.modifier=modifier
            for header in keys:
                value=data[header][indx]
                tableHeader=inventoryItem.convert_header_name(header)
                if tableHeader == -1:
                    if re.match('^.*?product\s*code',header,re.IGNORECASE):
                        inventoryItem.code=value.strip().upper()
                    elif re.match('^.*?prefix',header,re.IGNORECASE):
                        inventoryItem.prefix=value.strip().upper()
                    elif re.match('modified',header,re.IGNORECASE) and retainModDate:
                        #this comes back as UTC datetime
                        if value:
                            inventoryItem.modified=value
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
            site=Site.objects.get(pk=inventoryItem.site_id)
            if site.product_in_inventory_history(item=inventoryItem):
                # don't save inventory if there is no change
                continue
            inventoryItem.save()
            inventoryItems.append(inventoryItem)
        return inventoryItems
    
    def __unicode__(self):
        return self.information.name+"("+str(self.information.code)+"-"+str(self.quantity)+")"
    
    def save(self):
        # add in microseconds offset to make sure we can distinguish order of saves
        if not self.modified:
            self.modified=timezone.now()
        self.modifiedMicroseconds=self.modified.microsecond
        if self.deleted:
            self.quantity=0
        super(self.__class__,self).save()
        
    def __lt__(self,other):
        return self.timestamp() < other.timestamp()
    
    def equal(self,other):
        if (self == None and other != None) or (self != None and other == None):
            return False
        return (self.information == other.information) and\
            (self.site == other.site) and\
            (self.quantity == other.quantity) and\
            (self.deleted == other.deleted) and\
            (self.modified == other.modified)
            
    def timestamp(self):
        return parse_datetime(self.modified.strftime("%FT%H:%M:%S")+"." + '%06d' % self.modifiedMicroseconds+self.modified.strftime("%z"))
    
    def convert_header_name(self,name):
        if re.match('^.*?site\s*number',name,re.IGNORECASE):
            return 'site'
        elif re.match('^.*?cartons\s*$',name,re.IGNORECASE):
            return 'quantity'
        elif re.match('^\s*deleted\s*$',name,re.IGNORECASE):
            return 'deleted'
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
    
    def inventory_history_count(self):
        """
        all inventory changes at the site with the same product info.
        """
        inventory=InventoryItem.objects.filter(
                           site=self.site).filter(
                           information=self.information)
        return inventory.count()
    
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
    