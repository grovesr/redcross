from django.db import models

# Create your models here.

########################################################
# these are the base models which other models reference
########################################################

class Site(models.Model):
    """
    Red Cross Site model
    """
    DELIVERY = 'delivery'
    INVENTORY = 'inventory'
    siteTypeChoices = (
        (DELIVERY, 'delivery'),
        (INVENTORY, 'inventory'),
    )
    name=models.CharField(max_length=50, default="",
                            help_text="Name of this site")
    type=models.CharField(max_length=20, default=DELIVERY, choices=siteTypeChoices,
                          help_text="Delivery or Inventory site type")
    address1=models.CharField(max_length=50, default="",
                                  help_text="Site name for this inventory site")
    address2=models.CharField(max_length=50, default="",
                                  help_text="Street address of this inventory site")
    address3=models.CharField(max_length=50, default="",
                                  help_text="Town address of this inventory site")
    contactName=models.CharField(max_length=50, default="",
                                 help_text="Primary cnotact name")
    contactPhone=models.CharField(max_length=25, default="",
                                  help_text="Primary contact phone number")
    notes=models.TextField(default="", help_text="Additional information about the site",
                           null=True, blank=True)
    
    def __unicode__(self):
        return self.name
    
class UnitOfMeasure(models.Model):
    """
    Red Cross unit of measure model
    contains expandable list of units of measure to associate with Products
    """
    name=models.CharField(max_length=20, default="EACH",
                          help_text="How are these measured (EACH, BOX, ...)?")

    def __unicode__(self):
        return self.name

class DRNumber (models.Model):
    """
    Red Cross Disaster Relief Operations number.  Assigned if a relief operation
    is expected to cost more than $10,000.  Attach this to inventory transactions
    so we can track inventory movements associated with large disasters.
    """
    dr=models.CharField(max_length=10, default="N/A",
                        help_text="Disaster Relief Operations number (large disasters only).")
    name=models.CharField(max_length=50, default="No Name Required",
                          help_text="description of the Disaster Operation")
    
    def __unicode__(self):
        return self.dr

class TransactionPrefix (models.Model):
    """
    Red Cross Inventory transaction prefix.  Describes what kind of transaction
    has occurred.
    """
    
    prefix=models.CharField(max_length=5, default='P',
                            help_text="Code used to identify inventory transaction types")
    transaction=models.CharField(max_length=50, default="Physical Inventory",
                                 help_text="description of the transaction prefix code")
    
    def __unicode__(self):
        return self.prefix

###########################################################
#  The below models have relations to the base models above
###########################################################

class ProductInformation(models.Model):
    """
    Red Cross inventory Product Information model
    """
    unitOfMeasure=models.ForeignKey(UnitOfMeasure,
                                    help_text="How are these measured (EACH, BOX, ...)?")
    code=models.CharField(max_length=10, default="D11", primary_key=True,
                                 help_text="Unique Red Cross code for this product")
    name=models.CharField(max_length=50, default="",
                                 help_text="Name of this product")
    expendable=models.BooleanField(default=True, help_text="Is this product expendable?")
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
                                       help_text="??????")
    canExpire=models.BooleanField(default=False,
                                  help_text="Can this product expire?")
    expirationDate=models.DateField(blank=True, null=True, help_text="What is the expiration dat, if any?")
    expirationNotes=models.TextField(default="", blank=True, null=True,
                                     help_text="Special expiration notes for this product")
    
    def __unicode__(self):
        return self.name+" ("+self.code+")"

class Product(models.Model):
    """
    Red Cross Inventory Product
    """
    information=models.ForeignKey(ProductInformation,
                                  help_text="The detailed information about this product type")
    site=models.ForeignKey(Site,
                           help_text="The site containing this product")
    quantity=models.IntegerField(default=0,
                                 help_text="Number of product units (each, boxes, cases, ...) of this type at the site containing this product")
    
    def __unicode__(self):
        return self.information.name+"("+str(self.quantity)+")"

