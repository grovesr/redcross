from django import forms
from django.forms.utils import ErrorList
from rims.models import Product, ProductInformation, Site
    
class FileNameForm(forms.Form):
    files=forms.CharField(widget=forms.HiddenInput, max_length=1024)
    

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields=['quantity',]
    error_css_class = 'detail-table-error-text'
    required_css_class = 'rims-required-field'
    
class ProductInformationForm(forms.ModelForm):
    class Meta:
        model = ProductInformation
        fields=['name', 'code', 'unitOfMeasure', 'quantityOfMeasure','expendable',
                'cartonsPerPallet', 'doubleStackPallets', 'warehouseLocation',
                'canExpire', 'expirationDate', 'expirationNotes', 'costPerItem']
    error_css_class = 'detail-table-error-text'
    required_css_class = 'rims-required-field'
    
class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ['name','region','address1','address2','address3','contactName',
                  'contactPhone','notes']
    error_css_class = 'detail-error-text'
    required_css_class = 'rims-required-field'

class TitleErrorList(ErrorList):
    def __unicode__(self):              # __unicode__ on Python 2
        return self.as_title()

    def as_title(self):
        if not self: 
            return ''
        return '%s, ' % ''.join(['%s, ' % e for e in self])[:-2]
