from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.conf import settings
import PIL
from PIL import Image
import time
import os

class AccountType(models.Model):
	type = models.CharField(max_length=10)

	def __str__(self):
		return str(self.type)

class Account(models.Model):
	account = models.ForeignKey(AccountType, on_delete=models.CASCADE)
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	emailid = models.EmailField(unique=True)
	paypal_emailid = models.EmailField(blank=True)
	website = models.CharField(max_length=500, blank=True)
	password = models.TextField()
	status = models.IntegerField(default=0)
	activation_key = models.CharField(max_length=200, blank=True)
	country = models.CharField(max_length=200, blank=True)
	token = models.CharField(max_length=500, blank=True)
	platform = models.CharField(max_length=100, default='Shopify')
	added_shop = models.CharField(max_length=100, default="no")
	is_app_uninstall=models.BooleanField(default=False)
	token_time=models.DateTimeField()
	def __str__(self):
		return str(self.id)


class Vendor(models.Model):
	user = models.OneToOneField(Account, on_delete=models.CASCADE)
	vendor = models.CharField(max_length=100, unique=True)

	def __str__(self):
		return str(self.vendor)


class Categories(models.Model):
	user = models.ForeignKey(AccountType, on_delete=models.CASCADE)
	title = models.CharField(max_length=500)

	def __str__(self):
		return str(self.title)


class Products(models.Model):
	user = models.ForeignKey(Account, on_delete=models.CASCADE)
	category = models.ForeignKey(Categories, on_delete=models.CASCADE)
	title = models.CharField(max_length=500)
	description = models.TextField()
	selling_price = models.FloatField(default=0.00)
	dropshipping_price = models.FloatField(default=0.00)
	dropshipping_percentage=models.FloatField(default=0.00)
	wholesale_price = models.FloatField(default=0.00)
	wholesale_percentage=models.FloatField(default=0.00)
	is_tax=models.BooleanField(default=False)
	sku = models.CharField(max_length=100)
	barcode = models.CharField(max_length=100)
	created_date = models.DateTimeField(default=timezone.now)
	updated_date = models.DateTimeField(default=timezone.now)
	isAdded = models.BooleanField(default=False)
	quantity = models.BigIntegerField(default=5)
	PlatformProductId = models.BigIntegerField(default=0)
	platform = models.CharField(max_length=100, default='Shopify')
	weight = models.CharField(max_length=100, blank=True)
	weight_unit = models.CharField(max_length=100, blank=True)
	isconfig = models.BooleanField(default=False)
	parent_id = models.CharField(default=None, null=True, max_length=100, blank=True)
	varient_value = models.CharField(default=None, null=True, max_length=100, blank=True)

	def __str__(self):
		return str(self.id)

	def product_in_store(self,merchant_id):
		product_added = self.productdetail_set.filter(merchant__id=int(merchant_id))
		if(product_added):
			return True
		else:
			return False


class Commission(models.Model):
	user = models.ForeignKey(Account, on_delete=models.CASCADE)
	commission = models.IntegerField(default=10)

	def __str__(self):
		return str(self.commission)

class ApiAuth(models.Model):
	platform_name = models.CharField(max_length=100, blank=True)
	platform_key = models.CharField(max_length=100, blank=True)
