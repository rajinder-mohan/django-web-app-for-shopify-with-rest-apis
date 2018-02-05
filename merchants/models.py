from __future__ import unicode_literals

from django.db import models

from shopify.models import Account, Products
from datetime import datetime

class AccountDetail(models.Model):
	#email = models.EmailField(unique=True)
	email = models.EmailField()
	password = models.TextField()
	platform = models.CharField(max_length=200)
	username = models.CharField(max_length=500, blank=True)
	shop_domain = models.CharField(max_length=255, unique=True)
	main_domain = models.CharField(max_length=255, unique=True)
	token = models.CharField(max_length=500)
	token_time=models.DateTimeField(default=datetime.now)
	status = models.IntegerField(default=0)
	is_deleted = models.IntegerField(default=0)

	def __str__(self):
		return str(self.username)


class ProductDetail(models.Model):
	merchant = models.ForeignKey(AccountDetail, on_delete=models.CASCADE)
	vendor = models.ForeignKey(Account, on_delete=models.CASCADE)
	product = models.ForeignKey(Products, on_delete=models.CASCADE)
	platform = models.CharField(max_length=200)
	PlatformProductId = models.BigIntegerField()

	def __str__(self):
		return str(self.id)


class AccessToken(models.Model):
	merchant = models.ForeignKey(AccountDetail, on_delete=models.CASCADE)
	access_token = models.CharField(max_length=200)

	def __str__(self):
		return self.access_token


class DenyAccess(models.Model):
	vendor = models.ForeignKey(Account, on_delete=models.CASCADE)
	merchant = models.ForeignKey(AccountDetail, on_delete=models.CASCADE)

	def __str__(self):
		return str(self.vendor_id)
class MerchantShopeCredentials(models.Model):
		merchant = models.ForeignKey(AccountDetail, on_delete=models.CASCADE)
		key = models.CharField(null=True,blank=True,max_length=200)
		secret = models.CharField(null=True,blank=True,max_length=200)
		request_token = models.CharField(null=True,blank=True,max_length=200)
		request_token_secret = models.CharField(null=True,blank=True,max_length=200)
		access_token = models.CharField(null=True,blank=True,max_length=200)
		access_token_secret = models.CharField(null=True,blank=True,max_length=200)
		platform = models.CharField(max_length=100, default='Shopify')

		def __str__(self):
			return str(self.merchant.name)
