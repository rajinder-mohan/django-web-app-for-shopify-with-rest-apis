from __future__ import unicode_literals

from django.db import models
from merchants.models import ProductDetail, AccountDetail
from shopify.models import Account, Products
from django.core.validators import URLValidator


class Orders(models.Model):
	merchant = models.ForeignKey(AccountDetail, blank=True, null=True,on_delete=models.CASCADE)
	platform = models.CharField(max_length=100)
	OrderId = models.BigIntegerField()
	paymentMethod = models.CharField(max_length=200)
	financial_status = models.CharField(max_length=100)
	OrderUrl = models.CharField(blank=True, null=True,max_length=1000)
	total_amount = models.FloatField(default=0.00)
	date = models.DateField(auto_now_add=True)
	time = models.TimeField(auto_now_add=True)
	fulfillment_status=models.CharField(max_length=100,blank=True,null=True,default='pending')
	customer_email=models.CharField(max_length=100,null=True, blank=True)
	customer_first_name=models.CharField(max_length=100,null=True, blank=True)
	customer_last_name=models.CharField(max_length=100,null=True, blank=True)
	customer_address=models.CharField(max_length=100,null=True, blank=True)
	customer_city=models.CharField(max_length=100,null=True, blank=True)
	customer_province=models.CharField(max_length=100,null=True, blank=True)
	customer_phone=models.CharField(max_length=100,null=True, blank=True)
	customer_zipcode=models.CharField(max_length=100,null=True, blank=True)
	customer_country=models.CharField(max_length=100,null=True, blank=True)

	#new field for updated status date
	updated_status = models.CharField(max_length=100, blank=True)
	vendorPlateformOrderId = models.CharField(max_length=200, blank=True)
	paid_by_merchant = models.CharField(max_length=100, blank=True)
	vendor_order_number = models.CharField(max_length=100, blank=True)

	# tracking
	tracking_company=models.CharField(max_length=100,blank=True,null=True)
	tracking_url=models.TextField(validators=[URLValidator()],null=True, blank=True)
	tracking_number=models.BigIntegerField(null=True, blank=True)

	def __str__(self):
		return str(self.id)


class OrderProducts(models.Model):
	order = models.ForeignKey(Orders, blank=True, null=True,on_delete=models.CASCADE)
	product_id = models.IntegerField()  #Product Table Foreign Key
	product_name = models.CharField(max_length=500)
	product_price = models.FloatField(default=0.00)
	user = models.ForeignKey(Account, on_delete=models.CASCADE)
	ShopifyProductId = models.BigIntegerField()
	ProductQty = models.BigIntegerField()
	date = models.DateField(auto_now_add=True)
	time = models.TimeField(auto_now_add=True)
	fulfillment_status=models.TextField(max_length=100,null=True,blank=True)
	fulfillment_quantity=models.BigIntegerField(default=0)

	def __str__(self):
		return str(self.id)
