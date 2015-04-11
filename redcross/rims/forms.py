from django import forms
from django.forms.utils import ErrorList
from django.forms import ModelChoiceField, Textarea
from rims.models import InventoryItem, ProductInformation, Site
from django.forms.fields import MultipleChoiceField

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields=['quantity','information','site',]
        widgets = {'information': forms.HiddenInput()}
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
    
class SiteListForm(forms.ModelForm):
    class Meta:
        model = Site
        fields=['Delete',]
    Delete=forms.BooleanField(initial = False,)
    error_css_class = 'detail-error-text'
    required_css_class = 'rims-required-field'

class ProductListForm(forms.ModelForm):
    class Meta:
        model = ProductInformation
        fields=['Delete',]
    Delete=forms.BooleanField(initial = False,)
    error_css_class = 'detail-error-text'
    required_css_class = 'rims-required-field'

class TitleErrorList(ErrorList):
    def __unicode__(self):              # __unicode__ on Python 2
        return self.as_title()

    def as_title(self):
        if not self: 
            return ''
        return '%s, ' % ''.join(['%s, ' % e for e in self])[:-2]
