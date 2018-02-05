from __future__ import unicode_literals

from django.db import models
from shopify.models import Account
# Create your models here.

class VendorsShopCredentials(models.Model):
		vendor = models.ForeignKey(Account, on_delete=models.CASCADE)
		key = models.CharField(null=True,blank=True,max_length=200)
		secret = models.CharField(null=True,blank=True,max_length=200)
		request_token = models.CharField(null=True,blank=True,max_length=200)
		request_token_secret = models.CharField(null=True,blank=True,max_length=200)
		access_token = models.CharField(null=True,blank=True,max_length=200)
		access_token_secret = models.CharField(null=True,blank=True,max_length=200)
		platform = models.CharField(max_length=100, default='Shopify')

		def __str__(self):
			return str(self.merchant.name)
