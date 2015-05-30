from django.test import TestCase

# Create your tests here.
from .models import Site, ProductInformation, InventoryItem

class SiteMethodTests(TestCase):
    """
    tests for Site instance methods
    """
    # test helper functions
    def create_inventory_item_for_site(self,site=None,
                                             product=None,
                                             quantity=1,
                                             deleted=0,):
        if not site:
            site=Site(name="test site 1",)
            site.save()
        if not product:
            product=ProductInformation(name="test product 1",
                                       code="pdt1",)
            product.save()
        inventoryItem=site.add_inventory(product=product,
                                    quantity=quantity,
                                    deleted=deleted,)
        return site, product, inventoryItem
    
    def create_m_products_change_inventory_n_times_for_site(self,site=None,m=1,n=1):
        if not site:
            site=Site(name="test site 1",)
            site.save()
        productList=[]
        inventoryItemList=[]
        for k in range(m):
            productName="test product "+str(k+1)
            productCode="pdt"+str(k+1)
            product=ProductInformation(name=productName, code=productCode,)
            product.save()
            productList.append(product)
            for p in range(n):
                site,product,inventoryItem=self.create_inventory_item_for_site(
                                                    site=site,
                                                    product=product,
                                                    quantity=p+1,
                                                    deleted=0,)
                inventoryItemList.append(inventoryItem)
        return site,productList,inventoryItemList
    
    #Site inventory tests
    def test_latest_inventory_quantity_after_initial_creation(self):
        """
        site.latest_inventory should only return the latest change
        """
        site=Site(name="test site 1")
        site.save()
        product=ProductInformation(name="test product 1", code="pdt1")
        product.save()
        site,product,inventoryItem=self.create_inventory_item_for_site(
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
        self.create_inventory_item_for_site(site=site,product=product,quantity=1)
        self.create_inventory_item_for_site(site=site,product=product,deleted=1)
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
        site=Site(name="test site 1",)
        site.save()
        site,products,inventoryItems=self.create_m_products_change_inventory_n_times_for_site(
                                        site=site,m=1,n=3)
        latestInventory=site.latest_inventory()
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
        site=Site(name="test site 1",)
        site.save()
        site,products,inventoryItems=self.create_m_products_change_inventory_n_times_for_site(
                                        site=site,m=1,n=3)
        self.create_inventory_item_for_site(site=site,product=products[0],deleted=1)
        latestInventory=site.latest_inventory()
        # latest_inventory is a queryset of all the most recent changes to the
        # site's inventory.  Check that a deleted InventoryItem doesn't show up
        # in inventory
        with self.assertRaises(InventoryItem.DoesNotExist):
            latestInventory.get(information_id=products[0].pk)
         
    def test_inventory_history_after_3_changes(self):
        """
        InventoryItem history of changes should be retained in the database
        """
        site=Site(name="test site 1",)
        site.save()
        self.create_m_products_change_inventory_n_times_for_site(
                                        site=site,m=1,n=3)
        self.assertEqual(site.inventoryitem_set.all().count(),3)
         
    def test_latest_inventory_quantity_after_deletion_and_re_addition(self):
        """
        site.latest_inventory should only return the latest change and not return
        any deleted items. If an item is deleted and then re-added, we should always
        see the last change
        """
        site=Site(name="test site 1",)
        site.save()
        site,products,inventoryItems=self.create_m_products_change_inventory_n_times_for_site(
                                        site=site,m=1,n=3)
        self.create_inventory_item_for_site(site=site,product=products[0],deleted=1)
        self.create_inventory_item_for_site(site=site,product=products[0],quantity=100)
        latestInventory=site.latest_inventory()
        # latest_inventory is a queryset of all the most recent changes to the
        # site's inventory.  Check that we still have inventory after a deletion
        # and re-addition
        self.assertEqual(latestInventory.get(information_id=products[0].pk).quantity,100)