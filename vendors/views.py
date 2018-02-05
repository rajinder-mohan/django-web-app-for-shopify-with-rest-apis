from django.shortcuts import render
from rest_framework.views import APIView
from .forms import AddVendorForm, AddProductForm
from bs4 import BeautifulSoup
import json
from django.http import HttpResponse
from shopify.models import AccountType, Account, Commission, Vendor, Categories, Products
import binascii
import os
from passlib.hash import django_pbkdf2_sha256 as handler
# import urllib, cStringIO
import urllib
from images.models import Images
from datetime import datetime
import urllib.parse
import urllib.request as urllib2
from django.core.files import File
from PIL import Image
from django.core.files.temp import NamedTemporaryFile
from django.conf import settings
from io import StringIO
import requests
import time,ast,random
from images.models import *
from mailjet_rest import Client
from merchants.models import *
from orders.models import *
mailjet = Client(auth=(settings.MAILJET_API_KEY, settings.MAILJET_API_SECRET))

def send_template(emailid, Vars, template_id):
	data = {
		'FromEmail': 'info@fashioncircle.de',
		'FromName': 'Chris Weber',
		'MJ-TemplateID': template_id,
		'MJ-TemplateLanguage': True,
		'Recipients': [
			{ "Email": emailid}
		],
		'Vars': Vars
	}
	result = mailjet.send.create(data=data)
	return


class AddVendor(APIView):

	def post(self, request):
		response = {}
		print ('request')
		form = AddVendorForm(request.POST, request=request)
		print (form)
		if form.is_valid():
			try:
				print ('form v1alid')
				account_type = AccountType.objects.get(type="vendor")
				account_id = account_type.id

				paypal_emailid = emailid = request.GET.get('email')
				vendor_name = request.GET.get('name')
				platform = request.GET.get('platform')
				first_name = vendor_name
				last_name = ''
				if ' ' in vendor_name:
					name = vendor_name.split(' ')
					first_name = name[0]
					last_name = name[1]
				website = request.GET.get('website')
				status = 0
				country = request.GET.get('country')
				random_new_token=''.join(random.choice('0123456789ABCDEF') for i in range(16))

				lis=[]
				password = binascii.hexlify(os.urandom(16)).decode()
				encrypted = handler.encrypt(password)
				token_time=datetime.now()
				obj = Account(account_id=account_id,token_time=token_time, first_name=first_name, last_name=last_name, emailid=emailid, paypal_emailid=paypal_emailid, website=website, status=status, country=country, token=random_new_token, platform=platform, password=encrypted, added_shop="yes")
				obj.save()
				vendor_detail = Vendor(user_id=obj.id,vendor=vendor_name)
				vendor_detail.save()

				# add commission
				add_commission = Commission(user_id=obj.id, commission=10)
				add_commission.save()

				# get admin_email
				admin_object=Account.objects.get(id=1)
				admin_email=admin_object.emailid
				# email1
				Vars1 = {"account_type": "label"}
				template_id1 = "138014"
				send_template(admin_email, Vars1, template_id1)

				# email2
				Vars = {"first_name": first_name, "label_name": vendor_name,"password":password}
				template_id = "170804"
				send_template(emailid, Vars, template_id)
				response['success']='success'




			except Exception as r:
				print ('\n\n    Exception')
				response['exception']=r


		else:
			html = str(form)
			error_html = BeautifulSoup(html, 'html.parser')
			ul = error_html.find("ul", {"class": "errorlist nonfield"})
			error = ul.find("li").text
			print ('Error is This ;  '+str(error))
			response['error'] = error
			# retrun HttpResponse(json.dumps(response))
		print ('\n\n res',response)
		return HttpResponse(json.dumps(response))


class AddProduct(APIView):

	def image_generate(self,imgage,url):
		image_path=""
		filename=url.split("?")[0].split("/")[-1]
		file_path=settings.MEDIA_ROOT
		currenttime=str(int(time.time()))
		file_name=currenttime+"_"+filename

		file_path=file_path + "/products/"+str(currenttime)
		save_path="products/"+str(currenttime)+"/"+file_name
		url=str(url)

		thumbnails=Thumbnails.objects.all()
		if(not os.path.exists(file_path)):
			os.makedirs(file_path)
		for thumbnail in thumbnails:
			width = thumbnail.width
			height = thumbnail.height
			response = requests.get(url)

			image=Image.open(StringIO(response.content))
			img = image.resize((width,height), Image.ANTIALIAS)
			same_image_path=file_path+"/"+file_name
			save=img.save(same_image_path)
			filename=file_path+"/"+str(width)+"_"+file_name
			img.save(filename)

		Images.objects.filter(id=imgage.id).update(image=save_path,image_name=file_name)
		# imgage.update(image=save_path)
		return image_path

	def post(self, request):
		response = {}
		form = AddProductForm(request.POST, request=request)
		if form.is_valid():
			category = request.POST['category']

			myshopify_domain = request.POST['myshopify_domain']
			title = request.POST['title']
			description = request.POST['description']
			dropshipping_price = 0.0
			dropshipping_percentage=0.0
			if 'dropshipping_price' in request.POST:
				dropshipping_price = request.POST['dropshipping_price']

			if 'dropship_price_percent' in request.POST:
				dropshipping_percentage = request.POST['dropship_price_percent']
				dropshipping_percentage=float(dropshipping_percentage)

			sku = request.POST['sku']
			quantity = request.POST['quantity']
			PlatformProductId = request.POST['product_id']
			selling_price = 0.0

			if 'selling_price' in request.POST:
				selling_price = request.POST['selling_price']
			platform = request.POST['platform']
			wholesale_percentage=0.0

			if 'wholesale_price' in request.POST:
				wholesale_price=request.POST['wholesale_price']
				wholesale_price=float(wholesale_price)

			if 'wholesale_price_percent' in request.POST:
				wholesale_percentage=request.POST['wholesale_price_percent']
				wholesale_percentage=float(wholesale_percentage)


			vendor_detail = Account.objects.get(website=myshopify_domain)
			user_id = vendor_detail.id
			user_id=int(user_id)

			# category_id = 0

			existing_category = Categories.objects.filter(title=category)
			category_id = existing_category[0].id

			weight = request.POST['weight']
			weight_unit = request.POST['weight_unit']

			product_obj = Products(user_id=user_id, category_id=category_id, title=title, description=description, selling_price=selling_price, dropshipping_price=dropshipping_price, sku=sku, quantity=quantity, PlatformProductId=PlatformProductId, platform=platform,wholesale_price=wholesale_price, weight=weight, weight_unit=weight_unit,dropshipping_percentage=dropshipping_percentage,wholesale_percentage=wholesale_percentage)
			product_obj.save()
			product_id = product_obj.id
			images = request.POST['image']
			lis=[]
			if ',' in images:
				split=images.split(',')
				for x in split:
					lis.append(x)
			else:
				lis.append(images)


			lis=lis[::-1]



			for url in lis:
				image_obj = Images.objects.create(user_id=user_id,product_id=product_id)


			response['success'] = "Saved Successfully"
		else:
			html = str(form)
			error_html = BeautifulSoup(html, 'html.parser')
			ul = error_html.find("ul", {"class": "errorlist nonfield"})
			error = ul.find("li").text
			response['error'] = error
		return HttpResponse(json.dumps(response))


class DeleteProduct(APIView):

	def delete(self, request):
		response = {}


		if 'HTTP_API_KEY' not in self.request.META or not self.request.META['HTTP_API_KEY']:
			response['error'] = "You donot have access to Vendors"
			return HttpResponse(json.dumps(response))

		api_key = self.request.META['HTTP_API_KEY']

		if api_key != "pbkdf2_sha256$29000$p7lpJChcK4Lo$IHMul9j5lcPNJP4f/W1nXZknVi2N+GJIR1tZCo5C7uM=":
			response['error'] = "You donot have access to Vendors"
			return HttpResponse(json.dumps(response))

		if 'website' not in request.POST or not request.POST['website']:
			response['error'] = "Please enter website name."
			return HttpResponse(json.dumps(response))

		website = request.POST['website']

		if 'platform_pro_id' not in request.POST or not request.POST['platform_pro_id']:
			response['error'] = "Please enter Platform Product Id."
			return HttpResponse(json.dumps(response))

		platform_pro_id = request.POST['platform_pro_id']

		existing_domain = Account.objects.filter(website=website)
		if not existing_domain:
			response = {"error": "website does not exist."}
			return HttpResponse(json.dumps(response))

		second_lis=[]

		user_id = existing_domain[0].id
		user_id=int(user_id)
		products_detail=Products.objects.filter(user_id=user_id,PlatformProductId=platform_pro_id)
		if not products_detail:
			response = {"error": "User Id,Platform Id does not belong to a single product"}
			return HttpResponse(json.dumps(response))
		else:
			merchant_details=ProductDetail.objects.filter(product_id=products_detail[0].id)
			for merchant_detail in merchant_details:
				PlatforProduId=merchant_detail.PlatformProductId
				acc_id=merchant_detail.merchant_id
				account_detail=AccountDetail.objects.filter(id=acc_id)
				if account_detail:
					shopify_domain=account_detail[0].shopify_domain
					acc_token=account_detail[0].token
					acc_platform=account_detail[0].platform
					second_lis.append({'shopify_domain':shopify_domain,'PlatformProductId':PlatforProduId,'token':acc_token,'platform':acc_platform})
			delete=products_detail.delete()

		link = settings.SHOPIFY_DOMAIN + "/fashioncircle/webhooks/getShopDataOnDelete.php"
		resp = requests.post(link, data=json.dumps(second_lis), headers={'content-type': 'application/json'})

		response = {"success": "Successfully Deleted"}
		return HttpResponse(json.dumps(response))




class UninstallVendor(APIView):

	def delete(self, request):
		response = {}

		if 'HTTP_API_KEY' not in self.request.META or not self.request.META['HTTP_API_KEY']:
			response['error'] = "You donot have access to Vendors"
			return HttpResponse(json.dumps(response))

		api_key = self.request.META['HTTP_API_KEY']

		if api_key != "pbkdf2_sha256$29000$p7lpJChcK4Lo$IHMul9j5lcPNJP4f/W1nXZknVi2N+GJIR1tZCo5C7uM=":
			response['error'] = "You donot have access to Vendors"
			return HttpResponse(json.dumps(response))

		if 'website' not in request.POST or not request.POST['website']:
			response['error'] = "Please enter website name."
			return HttpResponse(json.dumps(response))

		website = request.POST['website']

		existing_domain = Account.objects.filter(website=website)
		if not existing_domain:
			response = {"error": "website does not exist."}
			return HttpResponse(json.dumps(response))

		else:
			prim_key=existing_domain[0].id
			token=existing_domain[0].token
			domain=existing_domain[0].website
			check_previous_status=existing_domain[0].is_app_uninstall
			if check_previous_status is True:
				response = {"error": "Vendor Already Unistaleld"}
				return HttpResponse(json.dumps(response))

			else:
				update=Account.objects.filter(website=website).update(is_app_uninstall=True)
				if update:
					lis=[]
					product_obj=Products.objects.filter(user_id=prim_key).exclude(PlatformProductId=0)
					for obj in product_obj:
						obj_id=obj.id
						product_details=ProductDetail.objects.filter(product_id=obj_id)
						if product_details:
							for product_detail in product_details:
								platform_pro_id=product_detail.PlatformProductId
								merchant_id=product_detail.merchant_id
								account_detail=AccountDetail.objects.filter(id=merchant_id)
								platform=account_detail[0].platform
								shopify_domain=account_detail[0].shopify_domain
								token=account_detail[0].token
								lis.append({'platform':platform,'token':token,'shopify_domain':shopify_domain,'PlatformProductId':platform_pro_id})

					data = {'products': lis}
					link = settings.SHOPIFY_DOMAIN + "/fashioncircle/webhooks/getShopDataOnDelete.php"
					resp = requests.post(link, data=json.dumps(lis), headers={'content-type': 'application/json'})
					response['success'] = str("Successfully Unistalled Vendor")
					return HttpResponse(json.dumps(response))


class PlaceVendorProduct(APIView):

	def post(self, request):
		response = {}
		api_key = self.request.META['HTTP_API_KEY']

		if api_key != "pbkdf2_sha256$29000$p7lpJChcK4Lo$IHMul9j5lcPNJP4f/W1nXZknVi2N+GJIR1tZCo5C7uM=":
			response['error']='API KEY DOES NOT MATCH'
			return HttpResponse(json.dumps(response))

		else:
			ax=request.data['order_detail']
			products=ax.decode('unicode_escape').encode('ascii','ignore')

			products=json.loads(products)
			order_domain=products['domain']
			order_platform=products['platform']
			order_orderid=products['OrderId']
			order_paymentMethod=products['paymentMethod']
			order_financial_status=products['financial_status']
			order_url=products['OrderUrl']

			products=products['products']

			# Update Product Quantity

			for i in products:
				vendor_lis=[]
				merchant_lis=[]

				product_obj=Products.objects.filter(PlatformProductId=i['ShopifyProductId'])
				database_quantity=int(product_obj[0].quantity)
				remaining_quantity=database_quantity-int(i['ProductQty'])

				product_obj=Products.objects.filter(PlatformProductId=i['ShopifyProductId']).update(quantity=remaining_quantity)

				# Vendor Web Hook
				if product_obj:
					filters=Products.objects.filter(PlatformProductId=i['ShopifyProductId'])
					product_pk=filters[0].id
					user_id=filters[0].user_id
					platform=filters[0].platform
					account_obj=Account.objects.filter(id=user_id)
					shopify_domain=account_obj[0].website
					token=account_obj[0].token
					vendor_lis.append({'ProductQuantity':remaining_quantity,'platform':platform,'PlatformProductId':i['ShopifyProductId'],'shopify_domain':shopify_domain,'token':token})


					vendor_link = "https://shopify.fashioncircle.de/vendorApp/webhooks/update_product_inventory.php"
					resp = requests.post(vendor_link, data=json.dumps(vendor_lis), headers={'content-type': 'application/json'})


					# Merchant Web Hook
					product_detail_obj=ProductDetail.objects.filter(product_id=product_pk)
					for product_detail in product_detail_obj:
						merchant_obj_acc=AccountDetail.objects.filter(id=product_detail.merchant_id)
						merch_platform=merchant_obj_acc[0].platform
						merch_platformproductid=product_detail.PlatformProductId



						merchant_lis.append({'platform':merch_platform,'PlatformProductId':merch_platformproductid,'ProductQuantity':remaining_quantity,'shopify_domain':merchant_obj_acc[0].shopify_domain,'token':merchant_obj_acc[0].token})
					merchant_link = "https://shopify.fashioncircle.de/fashioncircle/webhooks/update_product_inventory.php"
					resp = requests.post(merchant_link, data=json.dumps(merchant_lis), headers={'content-type': 'application/json'})

			response['success']="Product Quantity Updated Successfully, "
		return HttpResponse(json.dumps(response))


class MerchantList(APIView):
	def get(self, request):
		response = {}
		api_key = self.request.META['HTTP_API_KEY']
		all_merchant_lis=[]
		blocked_merchat_lis=[]
		final_data_list=[]

		if api_key != "pbkdf2_sha256$29000$p7lpJChcK4Lo$IHMul9j5lcPNJP4f/W1nXZknVi2N+GJIR1tZCo5C7uM=":
			response['error']='API KEY DOES NOT MATCH'
			return HttpResponse(json.dumps(response))
		else:
			email=self.request.GET.get('domain')
			email=email.decode('unicode_escape').encode('ascii','ignore')

			if email=='':
				response['error']='Domain Param Is Blank'
				return HttpResponse(json.dumps(response))
			else:
				account_obj=Account.objects.filter(website=email)
				vendor_id=account_obj[0].id

				# All Merchant List
				all_merchant_obj=AccountDetail.objects.all()
				for i in all_merchant_obj:
					all_merchant_lis.append(i.id)
				# All Blocked Merchants
				deny_users=DenyAccess.objects.filter(vendor_id=vendor_id)
				for deny_user in deny_users:
					blocked_merchat_lis.append(deny_user.merchant_id)

				for merchant_list in all_merchant_lis:
					if merchant_list not in blocked_merchat_lis:
						account_obj=AccountDetail.objects.filter(id=merchant_list)
						username=account_obj[0].username
						shopify_domain=account_obj[0].shopify_domain
						status='1'
						final_data_list.append({'username':username,'shopify_domain':shopify_domain,'status':status})
					else:
						account_obj=AccountDetail.objects.filter(id=merchant_list)
						username=account_obj[0].username
						shopify_domain=account_obj[0].shopify_domain
						status='0'
						final_data_list.append({'username':username,'shopify_domain':shopify_domain,'status':status})



		return HttpResponse(json.dumps(final_data_list))



class AllVendorOrders(APIView):
	def get(self, request):
		response = {}
		api_key = self.request.META['HTTP_API_KEY']
		order_id_lis=[]
		final_lis=[]
		# final_data_list=[]

		if api_key != "pbkdf2_sha256$29000$p7lpJChcK4Lo$IHMul9j5lcPNJP4f/W1nXZknVi2N+GJIR1tZCo5C7uM=":
			response['error']='API KEY DOES NOT MATCH'
			return HttpResponse(json.dumps(response))
		else:
			website=self.request.GET.get('domain')
			website=website.decode('unicode_escape').encode('ascii','ignore')
			if website=='':
				response['error']='Domain Param Is Blank'
				return HttpResponse(json.dumps(response))
			else:
				account_obj=Account.objects.filter(website=website)
				if account_obj:
					vendor_id=account_obj[0].id

					# commission
					commission = 0

					commission_detail = Commission.objects.filter(user_id=vendor_id)
					if commission_detail:
						commission = commission_detail[0].commission

					orders=OrderProducts.objects.filter(user_id=vendor_id)
					if orders:
						for i in orders:
							order_id_lis.append(i.order_id)
						order_id_lis=set(order_id_lis)
						order_id_lis=list(order_id_lis)
						for lis in order_id_lis:
							order_obj=Orders.objects.filter(id=lis)
							paid_date = order_obj[0].updated_status
							vendorPlateformOrderId = order_obj[0].vendorPlateformOrderId
							vendor_order_number = order_obj[0].vendor_order_number
							merchant_id=order_obj[0].merchant_id
							merchant_obj=AccountDetail.objects.filter(id=merchant_id)
							try:
								merchant_name=merchant_obj[0].username
								merchant_domain=merchant_obj[0].shopify_domain
							except:
								merchant_name=''
								merchant_domain=''
							OrderId=order_obj[0].OrderId
							paymentMethod=order_obj[0].paymentMethod
							financial_status=order_obj[0].financial_status
							OrderUrl=order_obj[0].OrderUrl
							total_amount=order_obj[0].total_amount
							order_date=str(order_obj[0].date)
							order_time=str(order_obj[0].time)
							fulfillment_status=order_obj[0].fulfillment_status
							paid_by_merchant = order_obj[0].paid_by_merchant
							final_lis.append({'fulfillment_status':fulfillment_status,'order_date':order_date,'order_time':order_time,'financial_status':financial_status,'merchant_domain':merchant_domain,'merchant_name':merchant_name,'OrderId':OrderId,'payment_method':paymentMethod,'OrderUrl':OrderUrl,'total_amount':total_amount,'commission':commission,'paid_date':paid_date,'vendorPlateformOrderId':vendorPlateformOrderId,'paid_by_merchant':paid_by_merchant,'vendor_order_number':vendor_order_number})
						return HttpResponse(json.dumps(final_lis))

					else:
						response['error']='No Orders Found With Vendor'
						return HttpResponse(json.dumps(response))
				else:
					response['error']='NO Vendor Found With Domain'
					return HttpResponse(json.dumps(response))


		return HttpResponse(json.dumps(order_id_lis))




class ChangeMerchant(APIView):
	def post(self, request):
		response = {}
		api_key = self.request.META['HTTP_API_KEY']

		# final_data_list=[]

		if api_key != "pbkdf2_sha256$29000$p7lpJChcK4Lo$IHMul9j5lcPNJP4f/W1nXZknVi2N+GJIR1tZCo5C7uM=":
			response['error']='API KEY DOES NOT MATCH'
			return HttpResponse(json.dumps(response))
		else:
			if 'vendor_domain' not in self.request.POST or not self.request.POST['vendor_domain']:
				return HttpResponse('Vendor Domain Is Blank')
			if 'merchant_domain' not in self.request.POST or not self.request.POST['merchant_domain']:
				return HttpResponse('Merchant Domain Is Blank')
			if 'status' not in self.request.POST or not self.request.POST['status']:
				return HttpResponse('Status  Is Blank')

			vendor_domain=self.request.POST.get('vendor_domain')
			merchant_domain=self.request.POST.get('merchant_domain')
			status=self.request.POST.get('status')

			account_obj=Account.objects.filter(website=vendor_domain)
			if account_obj:
				merchant_obj=AccountDetail.objects.filter(shopify_domain=merchant_domain)
				if merchant_obj:
					vendor_id=account_obj[0].id
					merchant_id=merchant_obj[0].id
					if status=='1':
						access_obj=DenyAccess.objects.filter(vendor_id=vendor_id,merchant_id=merchant_id)
						if access_obj:
							unblock=access_obj.delete()
							response['success']='Great!! '+merchant_obj[0].username +' Has Access Now'
							return HttpResponse(json.dumps(response))

						else:
							response['error']=merchant_obj[0].username+' Has Already Access.Hangover Last Night?'
							return HttpResponse(json.dumps(response))
					if status=='0':
						access_check=DenyAccess.objects.filter(vendor_id=vendor_id,merchant_id=merchant_id)
						if access_check:
							response['error']=merchant_obj[0].username+' Is Already Blocked. Hangover Last Night?'
							return HttpResponse(json.dumps(response))
						else:
							create=DenyAccess.objects.create(vendor_id=vendor_id,merchant_id=merchant_id)
							response['success']='Great!! '+merchant_obj[0].username+'Is Blocked Now '
							return HttpResponse(json.dumps(response))

				else:
					response['error']='NO Merchant Found With Domain'
					return HttpResponse(json.dumps(response))
			else:
				response['error']='NO Vendor Found With Domain'
				return HttpResponse(json.dumps(response))
		return HttpResponse('sh')


class UpdateOrder(APIView):

	def post(self, request, *args, **kwargs):
		response = {}
		if 'HTTP_API_KEY' not in request.META:
			response['error'] = "You don't have access to this API."
			return HttpResponse(json.dumps(response))

		api_key = request.META['HTTP_API_KEY']

		if api_key != "pbkdf2_sha256$29000$p7lpJChcK4Lo$IHMul9j5lcPNJP4f/W1nXZknVi2N+GJIR1tZCo5C7uM=":
			response['error'] = "You don't have access to this API."
			return HttpResponse(json.dumps(response))

		if 'merchantOrderID' not in self.request.POST or not self.request.POST['merchantOrderID']:
			response['error'] = "Please enter merchantOrderID."
			return HttpResponse(json.dumps(response))

		if 'vendorPlateformOrderId' not in self.request.POST or not self.request.POST['vendorPlateformOrderId']:
			response['error'] = "Please enter vendorPlateformOrderId."
			return HttpResponse(json.dumps(response))

		merchantOrderID = request.POST['merchantOrderID']
		vendorPlateformOrderId = request.POST['vendorPlateformOrderId']
		vendor_order_number = request.POST['vendor_order_number']
		vendorPlateformOrderId = str(vendorPlateformOrderId)
		vendor_order_number = str(vendor_order_number)

		order_detail = Orders.objects.filter(OrderId=merchantOrderID)
		if order_detail:
			Orders.objects.filter(OrderId=merchantOrderID).update(vendorPlateformOrderId=vendorPlateformOrderId, vendor_order_number=vendor_order_number)
			response['success'] = "Successfully Saved."
		else:
			response['error'] = "Order does not exist."
			return HttpResponse(json.dumps(response))
		return HttpResponse(json.dumps(response))





class UpdatePayPAl(APIView):

	def post(self, request, *args, **kwargs):
		response = {}
		if 'HTTP_API_KEY' not in request.META:
			response['error'] = "You don't have access to this API."
			return HttpResponse(json.dumps(response))

		api_key = request.META['HTTP_API_KEY']

		if api_key != "pbkdf2_sha256$29000$p7lpJChcK4Lo$IHMul9j5lcPNJP4f/W1nXZknVi2N+GJIR1tZCo5C7uM=":
			response['error'] = "Wrong API."
			return HttpResponse(json.dumps(response))

		if 'domain' not in self.request.POST or not self.request.POST['domain']:
			response['error'] = "Please enter domain."
			return HttpResponse(json.dumps(response))

		if 'paypalid' not in self.request.POST or not self.request.POST['paypalid']:
			response['error'] = "Please enter paypal"
			return HttpResponse(json.dumps(response))

		domain = request.POST['domain']
		paypalid = request.POST['paypalid']
		acc_obj=Account.objects.filter(website=domain)

		if acc_obj:
			update=Account.objects.filter(website=domain).update(paypal_emailid=paypalid)
			response['success'] = "Paypal Email Updated Successfully"

			return HttpResponse(json.dumps(response))
		else:

			response['error'] = "Account Does Not Exist With Domain"
			return HttpResponse(json.dumps(response))
