from django.contrib import admin
from rims.models import Product, Site, UnitOfMeasure, DRNumber,\
    TransactionPrefix, ProductInformation
# Register your models here.
admin.site.register(Product)
admin.site.register(Site)
admin.site.register(DRNumber)
admin.site.register(UnitOfMeasure)
admin.site.register(TransactionPrefix)
admin.site.register(ProductInformation)