from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from .forms import AddAccountForm, AddProductForm
from .models import AccountDetail, ProductDetail, AccessToken
from bs4 import BeautifulSoup
import json
from cryptography.fernet import Fernet
from shopify.models import Products
from shopify.views import send_template
import binascii
import os
from shopify.utils.userdetails import UserDetail

########## encryption - decryption
'''
key = Fernet.generate_key()
cipher_suite = Fernet(key)
cipher_text = cipher_suite.encrypt(b"testing")
plain_text = cipher_suite.decrypt(cipher_text)
'''


class AddMerchant(APIView):
	def post(self, request):
		form = AddAccountForm(request.POST, request=request)

		if 'email' not in request.POST or not request.POST['email']:
			response = {'error': 'Please enter Email.'}
			return HttpResponse(json.dumps(response))

		if 'platform' not in request.POST or not request.POST['platform']:
			response = {'error': 'Please enter Platform.'}
			return HttpResponse(json.dumps(response))

		if 'name' not in request.POST or not request.POST['name']:
			response = {'error': 'Please enter Name.'}
			return HttpResponse(json.dumps(response))

		if 'myshopify_domain' not in request.POST or not request.POST['myshopify_domain']:
			response = {'error': 'Please enter Shopify Domain.'}
			return HttpResponse(json.dumps(response))

		if 'domain' not in request.POST or not request.POST['domain']:
			response = {'error': 'Please enter Domain.'}
			return HttpResponse(json.dumps(response))

		if 'token' not in request.POST or not request.POST['token']:
			response = {'error': 'Please enter Token.'}
			return HttpResponse(json.dumps(response))

		if 'HTTP_API_KEY' not in request.META or not request.META['HTTP_API_KEY']:
			existing_detail = AccountDetail.objects.filter(platform=platform, shopify_domain=shopify_domain)
			if not existing_detail:
				response = {"error": "You don't have access to add merchant."}
				return HttpResponse(json.dumps(response))
		else:
			api_key = request.META['HTTP_API_KEY']
			if api_key != "pbkdf2_sha256$29000$p7lpJChcK4Lo$IHMul9j5lcPNJP4f/W1nXZknVi2N+GJIR1tZCo5C7uM=":
				response = {"error": "You don't have access to add merchant."}
				return HttpResponse(json.dumps(response))

		email = request.POST['email']
		platform = request.POST['platform']
		username = request.POST['name']
		shopify_domain = request.POST['myshopify_domain']
		main_domain = request.POST['domain']
		token = request.POST['token']

		update(platform, shopify_domain, main_domain, token)

		isenabled = False
		response = {}

		if form.is_valid():
			existing_detail = AccountDetail.objects.filter(platform=platform, shopify_domain=shopify_domain)
			if not existing_detail:
				try:
					detail = AccountDetail(email=email, platform=platform, username=username, shopify_domain=shopify_domain, main_domain=main_domain, token=token)
					detail.save()
					access_token = binascii.hexlify(os.urandom(20)).decode()
					AccessToken.objects.create(merchant_id=detail.id, access_token=access_token)

					admin_detail = UserDetail(request).get_admin()
					admin_email = admin_detail.emailid

					# email1
					Vars1 = {"account_type": "retailer"}
					template_id1 = "138014"
					send_template(admin_email, Vars1, template_id1)

					# email2
					Vars = {"first_name": username, "merchant_name": shopify_domain}
					template_id = "136351"
					send_template(email, Vars, template_id)
					enabled = int(detail.status)
					if enabled == 1:
						isenabled = True
					response = {'Success': 'Saved Successfully', 'is_enabled': isenabled, 'access_token': access_token}
				except:
					response = {'error': 'Error While Saving!'}
					return HttpResponse(json.dumps(response))
			else:
				is_deleted = int(existing_detail[0].is_deleted)

				if is_deleted == 1:
					admin_detail = UserDetail(request).get_admin()
					admin_email = admin_detail.emailid
					Vars1 = {"account_type": "retailer"}
					template_id1 = "138014"
					send_template(admin_email, Vars1, template_id1)

					# email2
					Vars = {"first_name": username, "merchant_name": shopify_domain}
					template_id = "136351"
					send_template(email, Vars, template_id)
					AccountDetail.objects.filter(platform=platform, shopify_domain=shopify_domain).update(is_deleted=0)

				enabled = int(existing_detail[0].status)
				if enabled == 1:
					isenabled = True
				merchant_id = existing_detail[0].id
				token_detail = AccessToken.objects.get(merchant_id=merchant_id)
				access_token = token_detail.access_token
				response = {'is_enabled': isenabled, 'access_token': access_token}
		else:
			form = str(form)
			soup = BeautifulSoup(form, 'html.parser')
			if soup:
				ul = soup.find("ul", {"class": "errorlist nonfield"})
				if ul:
					error = ul.find("li").text
					response = {'error': error, 'is_enabled': isenabled}
					return HttpResponse(json.dumps(response))
		return HttpResponse(json.dumps(response))


class AddProduct(APIView):
	def post(self, request):
		form = AddProductForm(request.POST, request=request)

		if form.is_valid():
			domain = request.POST['domain']
			vendor_id = request.POST['vendor_id']
			product_id = request.POST['product_id']
			platform = request.POST['platform']

			PlatformProductId = request.POST['PlatformProductId']

			merchant_detail = AccountDetail.objects.get(main_domain=domain)
			merchant_id = merchant_detail.id

			Products.objects.filter(id=product_id).update(isAdded=True)

			existing_product = ProductDetail.objects.filter(merchant_id=merchant_id, vendor_id=vendor_id, product_id=product_id)
			if existing_product:
				response = {"error": "This product is already added in your shopify app."}
				return HttpResponse(json.dumps(response))

			try:
				add_product = ProductDetail(merchant_id=merchant_id, vendor_id=vendor_id, product_id=product_id, platform=platform, PlatformProductId=PlatformProductId)
				add_product.save()
			except:
				response = {'error': 'Error While Saving!'}
				return HttpResponse(json.dumps(response))
		else:
			form = str(form)
			soup = BeautifulSoup(form, 'html.parser')
			if soup:
				ul = soup.find("ul", {"class": "errorlist nonfield"})
				if ul:
					error = ul.find("li").text
					return HttpResponse(error)
		response = {'Success': 'Saved Successfully'}
		return HttpResponse(json.dumps(response))

	def delete(self, request):

		if 'HTTP_ACCESS_TOKEN' not in request.META or not request.META['HTTP_ACCESS_TOKEN']:
			response = {"error": "You don't have access to delete product."}
			return HttpResponse(json.dumps(response))

		access_token = request.META['HTTP_ACCESS_TOKEN']
		existing_token = AccessToken.objects.filter(access_token=access_token)
		if not existing_token:
			response = {"error": "You don't have access to delete product."}
			return HttpResponset(json.dumps(response))

		if 'domain' not in request.POST or not request.POST['domain']:
			response = {"error": "Please enter domain."}
			return HttpResponse(json.dumps(response))

		if 'PlatformProductId' not in request.POST or not request.POST['PlatformProductId']:
			response = {"error": "Please enter PlatformProductId"}
			return HttpResponse(json.dumps(response))
		domain = request.POST['domain']
		PlatformProductId = request.POST['PlatformProductId']

		merchant_detail = AccountDetail.objects.get(main_domain=domain)
		merchant_id = merchant_detail.id
		status = merchant_detail.status
		if int(status == 0):
			response = {"error": "You don't have access to delete product. Please contact to adminitrator to activate your account."}
			return HttpResponse(json.dumps(response))

		existing = ProductDetail.objects.filter(merchant_id=merchant_id, PlatformProductId=PlatformProductId)
		if existing:
			product_id = existing[0].product_id
			try:
				ProductDetail.objects.filter(merchant_id=merchant_id, PlatformProductId=PlatformProductId).delete()
				response = {'success': 'Deleted Successfully', 'product_id': product_id}
				return HttpResponse(json.dumps(response))
			except:
				pass
		response = {'error': 'Error While Deleting'}
		return HttpResponse(json.dumps(response))

def update(platform, myshopify_domain, domain, token):
	existing_domain = AccountDetail.objects.filter(shopify_domain=myshopify_domain, platform=platform)
	if existing_domain:
		existing_token = existing_domain[0].token
		AccountDetail.objects.filter(shopify_domain=myshopify_domain, platform=platform).update(main_domain=domain, token=token)
	return


class DeleteMerchant(APIView):

	def delete(self, request):
		domain = request.POST['domain']

		existing_domain = AccountDetail.objects.filter(main_domain=domain)
		if not existing_domain:
			response = {"error": "Domain does not exist."}
			return HttpResponse(json.dumps(response))

		merchant_id = existing_domain[0].id
		merchant_name = existing_domain[0].username
		merchant_email = existing_domain[0].email

		access_token = request.META['HTTP_ACCESS_TOKEN']

		existing_token = AccessToken.objects.filter(merchant_id=merchant_id, access_token=access_token)
		if not existing_token:
			response = {"error": "You don't have access to delete product."}
			return HttpResponse(json.dumps(response))

		# AccountDetail.objects.filter(main_domain=domain).delete()
		# AccessToken.objects.filter(merchant_id=merchant_id, access_token=access_token).delete()
		products_list = []
		products = ProductDetail.objects.filter(merchant_id=merchant_id)
		for product in products:
			product_id = product.product_id
			pdetail = Products.objects.get(id=product_id)
			products_list.append({'product_name': pdetail.title})

		products = ProductDetail.objects.filter(merchant_id=merchant_id).delete()
		AccountDetail.objects.filter(main_domain=domain).update(status=0, is_deleted=1)

		template_id = "150825"
		Vars = {"first_name": merchant_name, "mj-invoice-item": products_list}
		send_template(merchant_email, Vars, template_id)
		response = {"success": "Successfully Deleted"}
		return HttpResponse(json.dumps(response))
