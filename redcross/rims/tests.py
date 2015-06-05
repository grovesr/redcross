from django.test import TestCase
from django.core.urlresolvers import reverse
from collections import OrderedDict
import os

# Create your tests here.
from .models import Site, ProductInformation, InventoryItem
from .settings import PAGE_SIZE, APP_DIR

# test helper functions
def create_inventory_item_for_site(site=None,
                                     product=None,
                                     quantity=1,
                                     deleted=0,
                                     modifier='admin'):
    if not site:
        site=Site(name="test site 1",)
        site.save()
    if not product:
        product=ProductInformation(name="test product 1",
                                   code="pdt1",)
        product.save()
    inventoryItem=site.add_inventory(product=product,
                                quantity=quantity,
                                deleted=deleted,
                                modifier=modifier,)
    return site, product, inventoryItem

def create_products_with_inventory_items_for_sites(numSites=1,
                                                   numProducts=1,
                                                   numItems=1):
    sitesList=[]
    productList=[]
    inventoryItemList=[]
    for m in range(numSites):
        siteName="test site "+str(m+1)
        site=Site(name=siteName,)
        site.save()
        sitesList.append(site)
        for n in range(numProducts):
            if m == 0:
                productName="test product "+str(n+1)
                productCode="pdt"+str(n+1)
                product=ProductInformation(name=productName, code=productCode,)
                product.save()
                productList.append(product)
            else:
                product=ProductInformation.objects.get(pk="pdt"+str(n+1))
            for p in range(numItems):
                site,product,inventoryItem=create_inventory_item_for_site(
                                                    site=site,
                                                    product=product,
                                                    quantity=p+1,
                                                    deleted=0,)
                inventoryItemList.append(inventoryItem)
    return sitesList,productList,inventoryItemList
    
def import_sites_from_xls(filename=None):
    sites=Site.parse_sites_from_xls(filename=filename, modifier='testAdmin')
    data, workbook=Site.import_sites_from_xls(filename=filename)
    #TODO: parse the data for comparison from data dictionary
    return sites

def import_products_from_xls(filename=None):
    products=ProductInformation.parse_product_information_from_xls(filename=filename, modifier='testAdmin')
    data, workbook=ProductInformation.import_product_information_from_xls(filename=filename)
    #TODO: parse the data for comparison from data dictionary
    return products

def import_inventory_items_from_xls(filename=None):
    inventoryItems=InventoryItem.parse_inventory_from_xls(filename=filename, modifier='testAdmin')
    data, workbook=InventoryItem.import_inventory_from_xls(filename=filename)
    #TODO: parse the data for comparison from data dictionary
    return inventoryItems

class SiteMethodTests(TestCase):
    """
    tests for Site instance methods
    """
    #Site inventory tests
    def test_latest_inventory_quanity_after_initial_creation(self):
        """
        site.latest_inventory should only return the latest change
        """
        site=Site(name="test site 1")
        site.save()
        product=ProductInformation(name="test product 1", code="pdt1")
        product.save()
        site,product,inventoryItem=create_inventory_item_for_site(
                                        site=site,product=product,quantity=1)
        latestInventory=site.latest_inventory()
        #latest_inventory is a queryset of all the most recent changes to the
        #site's inventory.  check that the inventoryItem that we just created has
        # the appropriate quantity
        self.assertEqual(
                    latestInventory.get(information_id=product.pk).quantity,
                    inventoryItem.quantity)
        
    def test_latest_inventory_quantity_after_deletion(self):
        """
        site.latest_inventory should only return the latest change, and should
        not return any deleted items
        """
        site=Site(name="test site 1")
        site.save()
        product=ProductInformation(name="test product 1", code="pdt1")
        product.save()
        create_inventory_item_for_site(site=site,product=product,quantity=1)
        create_inventory_item_for_site(site=site,product=product,deleted=1)
        latestInventory=site.latest_inventory()
        # latest_inventory is a queryset of all the most recent changes to the
        # site's inventory.  Check that a deleted item doesn't show up in
        # inventory
        with self.assertRaises(InventoryItem.DoesNotExist):
            latestInventory.get(information_id=product.pk)
     
    def test_latest_inventory_quantity_after_3_quantity_change(self):
        """
        site.latest_inventory should only return the latest change
        """
        sites,products,inventoryItems=create_products_with_inventory_items_for_sites(
                                        numSites=1,
                                        numProducts=1,
                                        numItems=3)
        latestInventory=sites[0].latest_inventory()
        # latest_inventory is a queryset of all the most recent changes to the
        # site's inventory.  check that the inventoryItem that we just added 
        # and then changed several times has the appropriate final quantity
        self.assertEqual(latestInventory.get(
                         information_id=products[0].pk).quantity,
                         inventoryItems.pop().quantity)
         
    def test_latest_inventory_quantity_after_3_quantity_change_and_deletion(self):
        """
        site.latest_inventory should only return the latest change and not return
        any deleted items.
        """
        sites,products,inventoryItems=create_products_with_inventory_items_for_sites(
                                        numSites=1,
                                        numProducts=1,
                                        numItems=3)
        create_inventory_item_for_site(site=sites[0],product=products[0],deleted=1)
        latestInventory=sites[0].latest_inventory()
        # latest_inventory is a queryset of all the most recent changes to the
        # site's inventory.  Check that a deleted InventoryItem doesn't show up
        # in inventory
        with self.assertRaises(InventoryItem.DoesNotExist):
            latestInventory.get(information_id=products[0].pk)
         
    def test_inventory_history_after_3_changes(self):
        """
        InventoryItem history of changes should be retained in the database
        """
        sites,products,inventoryItems=create_products_with_inventory_items_for_sites(
                                        numSites=1,
                                        numProducts=1,
                                        numItems=3)
        self.assertEqual(sites[0].inventoryitem_set.all().count(),3)
         
    def test_latest_inventory_quantity_after_deletion_and_re_addition(self):
        """
        site.latest_inventory should only return the latest change and not return
        any deleted items. If an item is deleted and then re-added, we should always
        see the last change
        """
        sites,products,inventoryItems=create_products_with_inventory_items_for_sites(
                                        numSites=1,
                                        numProducts=1,
                                        numItems=1)
        create_inventory_item_for_site(site=sites[0],product=products[0],deleted=1)
        create_inventory_item_for_site(site=sites[0],product=products[0],quantity=100)
        latestInventory=sites[0].latest_inventory()
        # latest_inventory is a queryset of all the most recent changes to the
        # site's inventory.  Check that we still have inventory after a deletion
        # and re-addition
        self.assertEqual(latestInventory.get(information_id=products[0].pk).quantity,100)
        
    def test_latest_inventory_quantity_3_products_after_3_changes(self):
        """
        site.latest_inventory should only return the latest change
        """
        sites,products,inventoryItems=create_products_with_inventory_items_for_sites(
                                        numSites=1,
                                        numProducts=3,
                                        numItems=3)
        latestInventory=sites[0].latest_inventory()
        # latest_inventory is a queryset of all the most recent changes to the
        # site's inventory.
        self.assertEqual(latestInventory.get(information_id=products[0].pk).quantity,
                         inventoryItems[3*1-1].quantity)
        self.assertEqual(latestInventory.get(information_id=products[1].pk).quantity,
                         inventoryItems[3*2-1].quantity)
        self.assertEqual(latestInventory.get(information_id=products[2].pk).quantity,
                         inventoryItems[3*3-1].quantity)
    
    def test_import_sites_from_xls_initial(self):
        """
        import 3 sites from Excel
        """
        sites=import_sites_from_xls(filename=os.path.join(APP_DIR,'testData/sites_add_site1_site2_site3.xls'))
        self.assertNotEqual(sites, -1, 'Failure to import sites from excel')
        storedSites=Site.objects.all()
        # check that we saved 3 sites
        self.assertEqual(storedSites.count(),3,'Number of imported sites mismatch. Some sites didn''t get stored.')
        
        # check that the site modifiers are correctly stored
        siteModifiers=[]
        for site in sites:
            siteModifiers.append(site.modifier)
        storedSiteModifiers=[]
        for storedSite in storedSites:
            storedSiteModifiers.append(storedSite.modifier)
        self.assertListEqual(storedSiteModifiers, siteModifiers)
    
    def test_import_products_from_xls_initial(self):
        """
        import 3 products from Excel
        """
        products=import_products_from_xls(filename=os.path.join(APP_DIR,'testData/products_add_prod1_prod2_prod3.xls'))
        self.assertNotEqual(products,-1,'Failure to import products from Excel')
        storedProducts=ProductInformation.objects.all()
        # check that we saved 3 sites
        self.assertEqual(storedProducts.count(),3,'Number of imported products mismatch. Some product didn''t get stored.')
        
        # check that the product modifiers are correctly stored
        productModifiers=[]
        for product in products:
            productModifiers.append(product.modifier)
        storedProductModifiers=[]
        for storedProduct in storedProducts:
            storedProductModifiers.append(storedProduct.modifier)
        self.assertListEqual(storedProductModifiers, productModifiers)
        
    def test_import_inventory_from_xls_initial(self):
        """
        import 3 inventory items to 3 sites from Excel
        """
        import_sites_from_xls(filename=os.path.join(APP_DIR,'testData/sites_add_site1_site2_site3.xls'))
        import_products_from_xls(filename=os.path.join(APP_DIR,'testData/products_add_prod1_prod2_prod3.xls'))
        inventoryItems=import_inventory_items_from_xls(filename=os.path.join(APP_DIR,'testData/inventory_add_10_to_site1_site2_site3_prod1_prod2_prod3.xls'))
        self.assertNotEqual(inventoryItems, -1, 'Failure to import inventory from Excel')
        self.assertNotEqual(len(inventoryItems), 0, 'Failure to create any inventoryItems. Missing associated Sites or ProductInformations?')
        storedInventory=InventoryItem.objects.all()
        # check that we saved 3 sites
        self.assertEqual(storedInventory.count(),3*3,'Total inventory mismatch.  Some didn''t get stored.')
        
        # check that the product modifiers are correctly stored
        inventoryModifiers=[]
        for item in inventoryItems:
            inventoryModifiers.append(item.modifier)
        storedInventoryModifiers=[]
        for storedItem in storedInventory:
            storedInventoryModifiers.append(storedItem.modifier)
        self.assertListEqual(storedInventoryModifiers, inventoryModifiers)
        inventoryModified=[]
        for item in inventoryItems:
            inventoryModified.append(item.timestamp())
        storedInventoryModified=[]
        for storedItem in storedInventory:
            storedInventoryModified.append(storedItem.timestamp())
        self.assertListEqual(storedInventoryModified, inventoryModified)
        
class HomeViewTests(TestCase):
    """
    tests for Home view
    """
    
    def test_home_view_for_latest_changes(self):
        """
        The home view should display sites with recently edited inventory with
        the latest changes at the top and latest inventory changes with the latest
        changes at the top as well
        """
        sites,products,inventoryItems=create_products_with_inventory_items_for_sites(
                                        numSites=20,
                                        numProducts=5,
                                        numItems=1)
        response=self.client.get(reverse('rims:home'))
        sitesResponseList=[]
        itemsResponseList=[]
        for site in response.context['sitesList']:
            
            sitesResponseList.append(repr(site))
        for item in response.context['inventoryList']:
            # include the microsecond modification to ensure uniqueness when comparing
            itemsResponseList.append(repr(item)+str(item.modified.strftime('%Y-%m-%d+%H:%M:%S'))+'.'+str(item.modifiedMicroseconds))
        
        sitesActualList=[]
        itemsActualList=[]
        for site in sites:
            sitesActualList.append(repr(site))
        # compare the latest changed sites only
        sitesActualList.reverse()
        # just retain the latest inventory changes to compare to the response
        latestInventoryItems=OrderedDict()
        inventoryItems.reverse()
        for item in inventoryItems:
            if not latestInventoryItems.has_key(item.information):
                latestInventoryItems[item.information]=item
        for item in latestInventoryItems.values():
            # include the microsecond modification to ensure uniqueness when comparing
            itemsActualList.append(repr(item)+str(item.modified.strftime('%Y-%m-%d+%H:%M:%S'))+'.'+str(item.modifiedMicroseconds))
        self.assertListEqual(sitesResponseList, sitesActualList[:PAGE_SIZE])
        self.assertListEqual(itemsResponseList, itemsActualList[:PAGE_SIZE])
    