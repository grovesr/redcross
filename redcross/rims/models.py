from django.db import models

# Create your models here.
class UnitOfMeasure(models.Model):
    """
    Red Cross unit of measure model
    contains expandable list of units of measure to associate with Products
    """
    name=models.CharField(max_length=20, default="EACH",
                          help_text="How are these measured (EACH, BOX, ...)?")

class Product(models.Model):
    """
    Red Cross inventory Product model
    """
    productCode=models.CharField(max_length=10, default="D11", primary_key=True,
                                 help_text="Unique Red Cross code for this product")
    productName=models.CharField(max_length=50, default="",
                                 help_text="Name of this product")
    expendable=models.BooleanField(default=True, help_text="Is this product expendable?")
    unitOfMeasure=models.OneToOneField(UnitOfMeasure,
                                       help_text="How are these measured (EACH, BOX, ...)?")
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
        return self.productName+" ("+self.productCode+")"