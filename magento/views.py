

                        					# MAGENTO VIEWS


import binascii
import os
from passlib.hash import django_pbkdf2_sha256 as handler
from django.views.generic import TemplateView,View
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from django.shortcuts import render
from bs4 import BeautifulSoup
from django.utils.decorators import method_decorator
from .decorators import session_check,merchant_session_check
from django.contrib import messages
from shopify.models import Account,Products,Categories,Commission,ApiAuth
from itertools import groupby
from collections import OrderedDict
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import datetime
import pycountry,requests,json
from validate_email import validate_email
from django.conf import settings
import uuid
from rauth.service import OAuth1Service
import requests
import urllib.parse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from passlib.hash import django_pbkdf2_sha256 as handler
from mailjet_rest import Client
from merchants.models import AccountDetail, ProductDetail, AccessToken,DenyAccess,MerchantShopeCredentials
from shopify.utils.userdetails import UserDetail
import base64
from orders.models import Orders,OrderProducts
from .models import PaypalAdaptive
from django.db.models import Sum
from vendors.models import VendorsShopCredentials
from images.models import Images
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



class VendorRegister(TemplateView):
	template_name = 'vendor/mag_vend_register.html'

	def post(self, request, *args, **kwargs):
		response={}

		context = super(VendorRegister, self).get_context_data()
		name = request.POST['name']

		email=request.POST['email']
		platform=request.POST['platform']
		website=request.POST['website']
		country=request.POST['country']
		api_key ="pbkdf2_sha256$29000$p7lpJChcK4Lo$IHMul9j5lcPNJP4f/W1nXZknVi2N+GJIR1tZCo5C7uM="
		data ={"api_key":api_key,"name":name,"email":email,"platform":platform,"website":website,"country":country}
		headers={'HTTP_API_KEY':'de'}
		url=  settings.SITE_URL+'/vendors/add'
		try:
			posted=requests.post(url,params=data,headers=headers)
			response=posted.text


		except Exception as r:
			response['exception']=r

		return HttpResponse(json.dumps(response))

	def get_context_data(self, *args, **kwargs):
		context = super(VendorRegister, self).get_context_data(**kwargs)
		all_countries = []

		countries_list = list(pycountry.countries)
		for country in countries_list:
			all_countries.append(country.name)
		context['all_countries']=all_countries
		return context





class VendorLogin(TemplateView):
	template_name = 'vendor/mag_vend_login.html'
	def post(self, request, *args, **kwargs):

		response={}
		context = super(VendorLogin, self).get_context_data()
		email = request.POST['loginemail']
		password = request.POST['loginpassword']
		email_obj=Account.objects.filter(emailid=email)
		if not email_obj:
			response['emailerror']='email'
		else:
			status=email_obj[0].status
			if status==0:
				response['status']='status'
				return HttpResponse(response)
			added_shop=email_obj[0].added_shop
			if added_shop!='yes':
				response['shop']='shop'
				return HttpResponse(response)

			# print ('email matched')
			hash_password = email_obj[0].password
			verify_password = handler.verify(password, hash_password)
			print ('\n\n' +str(verify_password))
			if verify_password is False:
				response['passworderror']='password'
			else:
				token=email_obj[0].token
				request.session['vendor_token'] = token
				print (request.session['vendor_token'])
				response['success']='success'
		return HttpResponse(response)


		# email=request.POST['email']
		# platform=request.POST['platform']
		# website=request.POST['website']
		# country=request.POST['country']
		# api_key ="pbkdf2_sha256$29000$p7lpJChcK4Lo$IHMul9j5lcPNJP4f/W1nXZknVi2N+GJIR1tZCo5C7uM="
		# data ={"api_key":api_key,"name":name,"email":email,"platform":platform,"website":website,"country":country}
		# headers={'HTTP_API_KEY':'de'}
		# url=  settings.SITE_URL+'/vendors/add'
		# try:
		# 	posted=requests.post(url,params=data,headers=headers)
		# 	response=posted.text
		#
		#
		# except Exception as r:
		# 	response['exception']=r


	def get_context_data(self, *args, **kwargs):

		context = super(VendorLogin, self).get_context_data(**kwargs)
		all_countries = []

		countries_list = list(pycountry.countries)
		for country in countries_list:
			all_countries.append(country.name)
		context['all_countries']=all_countries
		return context

class VendorForgetPassword(TemplateView):

	template_name = 'vendor/mag_vend_forget_password.html'

	def get_context_data(self, *args, **kwargs):
		context = super(VendorForgetPassword, self).get_context_data(**kwargs)
		return context

	def post(self, request, *args, **kwargs):
		response={}
		email=request.POST.get("email")
		try:
			account=Account.objects.get(emailid=email)
			if account.status==0:
				response['status']=0
				response['msg']="This is a inactive account. Contact with administrator to activate your account."
			elif account.added_shop=="no":
				response['status']=0
				response['msg']="There is no shop associated with this account."
			elif account.platform !="Magento":
				response['status']=0
				response['msg']="This is not right platform for this email. This email is associated with Magento."
			else:
				password = binascii.hexlify(os.urandom(16)).decode()
				encrypted = handler.encrypt(password)
				account.password=encrypted
				account.save()
				first_name = account.first_name
				Vars = {"first_name": first_name, "merchant_name": account.platform,"password":password}
				template_id = "253891"
				send_template(email, Vars, template_id)
				response['status']=1
				response['msg']="New password is send to "+email+". Please check your email."
		except Account.DoesNotExist:
			response['status']=0
			response['msg']="There is no account associated with this email."
		return HttpResponse(json.dumps(response), content_type='application/json')


class VendorDashboard(TemplateView):

	template_name = 'vendor/mag_vend_dashboard.html'

	def get(self, request, *arg, **kwargs):
		try:
			headers = {'Accept': 'application/json'}
			token=request.session['vendor_token']
			#---------Merchant Details And Megento Auth key and secret-------
			vendor = Account.objects.get(token=token)
			order_id_lis=[]
			final_lis=[]
			credentials = VendorsShopCredentials.objects.get(vendor__id=vendor.id)
			if credentials.access_token:
				request.session["access_token"] = credentials.access_token
				request.session["access_token_secret"] = credentials.access_token_secret
			MAGENTO_HOST = vendor.website
			MAGENTO_API_BASE = '%s/api/rest/' % MAGENTO_HOST
			magento = OAuth1Service(
				name               = 'fashion_circle',
				consumer_key       = credentials.key,
				consumer_secret    = credentials.secret,
				request_token_url  = '%s/oauth/initiate' % MAGENTO_HOST,
				access_token_url   = '%s/oauth/token' % MAGENTO_HOST,
				authorize_url      = '%s/admin/oauth_authorize' % MAGENTO_HOST,
				SITE_URL           = MAGENTO_API_BASE
				)
			if 'access_token' not in request.session:
				oauth_token = request.GET.get('oauth_token')
				oauth_verifier = request.GET.get('oauth_verifier')
				if not oauth_token and not oauth_verifier:
					request_token, request_token_secret = magento.get_request_token(method='POST', params={'oauth_callback':'{}/magento/vendor_dashboard'.format(settings.SITE_URL)})
					credentials.request_token = request_token
					credentials.request_token_secret = request_token_secret
					credentials.save()
					authorize_url = magento.get_authorize_url(request_token)
					return HttpResponseRedirect(authorize_url)
				else:
					session = magento.get_auth_session(credentials.request_token,
											   credentials.request_token_secret,
											   method='POST',
											   data={'oauth_verifier': oauth_verifier})
					request.session["access_token"] = session.access_token
					request.session["access_token_secret"] = session.access_token_secret
					credentials.access_token = request.session["access_token"]
					credentials.access_token_secret = request.session["access_token_secret"]
					credentials.save()
					tok = request.session["access_token"], request.session["access_token_secret"]
					session = magento.get_session(token=tok, signature=None)

					r = session.get(
						'products',
						header_auth=True,
						headers=headers
					)
					if r.status_code==200:
						response=json.loads(r.text)
						images_list=[]
						show_products=[]
						for product_id,product in response.items():
							images_response = session.get(
								'products/{}/images'.format(product_id),
								header_auth=True,
								headers=headers
							)
							image=json.loads(images_response.text)
							if image:
								product["imgurl"]=image[0]["url"]
							for idetail in image:
								images_list.append(idetail["url"])
							product_response = session.get(
								'products/{}'.format(product_id),
								header_auth=True,
								headers=headers
							)

							product_details=json.loads(product_response.text)
							product["qty"]=product_details["stock_data"]["qty"]
							show_products.append(product)
						merchants = AccountDetail.objects.all()
						page = self.request.GET.get('page', 1)
						merchant_list = Paginator(merchants, 20)
						products_list = Paginator(show_products, 12)

						try:
							products_list = products_list.page(page)
						except PageNotAnInteger:
							products_list = products_list.page(1)
						except EmptyPage:
							products_list = products_list.page(products_list.num_pages)
						try:
							merchant_list = merchant_list.page(page)
						except PageNotAnInteger:
							merchant_list = merchant_list.page(1)
						except EmptyPage:
							merchant_list = merchant_list.page(merchant_list.num_pages)
						#-------------------------orders-------------------------------------------------
						vendorid = vendor.id
						commission = 0
						commission_detail = Commission.objects.filter(user_id=vendorid)
						if commission_detail:
							commission = commission_detail[0].commission
						orders=OrderProducts.objects.filter(user_id=vendorid)
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
									merchant_domain=merchant_obj[0].shop_domain
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
						final_order_list = Paginator(final_lis, 12)
						try:
							final_order_list = final_order_list.page(page)
						except PageNotAnInteger:
							final_order_list = final_order_list.page(1)
						except EmptyPage:
							final_order_list = final_order_list.page(final_order_list.num_pages)
						return render(request, self.template_name,{"products":products_list,"images":images_list,"vendor_id":vendor.id,"merchants":merchant_list,"final_orders":final_order_list})

			else:
				tok = request.session["access_token"], request.session["access_token_secret"]
				session = magento.get_session(token=tok, signature=None)
				r = session.get(
					'products',
					header_auth=True,
					headers=headers
				)
				if r.status_code==200:
					response=json.loads(r.text)
					images_list=[]
					show_products=[]
					for product_id,product in response.items():
						images_response = session.get(
							'products/{}/images'.format(product_id),
							header_auth=True,
							headers=headers
						)
						image=json.loads(images_response.text)
						if image:
							product["imgurl"]=image[0]["url"]
						for idetail in image:
							images_list.append(idetail["url"])
						product_response = session.get(
							'products/{}'.format(product_id),
							header_auth=True,
							headers=headers
						)

						product_details=json.loads(product_response.text)
						product["qty"]=product_details["stock_data"]["qty"]
						show_products.append(product)
					print(show_products)
					merchants = AccountDetail.objects.all()
					page = self.request.GET.get('page', 1)
					merchant_list = Paginator(merchants, 20)
					products_list = Paginator(show_products, 12)

					try:
						products_list = products_list.page(page)
					except PageNotAnInteger:
						products_list = products_list.page(1)
					except EmptyPage:
						products_list = products_list.page(products_list.num_pages)
					try:
						merchant_list = merchant_list.page(page)
					except PageNotAnInteger:
						merchant_list = merchant_list.page(1)
					except EmptyPage:
						merchant_list = merchant_list.page(merchant_list.num_pages)
					#-------------------------orders-------------------------------------------------
					vendorid = vendor.id
					commission = 0
					commission_detail = Commission.objects.filter(user_id=vendorid)
					if commission_detail:
						commission = commission_detail[0].commission
					orders=OrderProducts.objects.filter(user_id=vendorid)
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
								merchant_domain=merchant_obj[0].shop_domain
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
					print(final_lis)
					final_order_list = Paginator(final_lis, 12)
					try:
						final_order_list = final_order_list.page(page)
					except PageNotAnInteger:
						final_order_list = final_order_list.page(1)
					except EmptyPage:
						final_order_list = final_order_list.page(final_order_list.num_pages)
					return render(request, self.template_name,{"products":products_list,"images":images_list,"vendor_id":vendor.id,"merchants":merchant_list,"final_orders":final_order_list})
				else:
					response=json.loads(r.text)
					return render(request, self.template_name,{"products":response})
					# response_body_list = response['messages']['error']
		except Exception as e:
			print(e)
		return render(request, self.template_name,{})

	def post(self, request, *args, **kwargs):

		return HttpResponse("")

	@method_decorator(session_check)
	def dispatch(self, *args, **kwargs):
		return super(VendorDashboard, self).dispatch(*args, **kwargs)





# Merchant Starts Here


class MerchantRegister(TemplateView):
	template_name = 'merchant/mag_mer_register.html'

	def get_context_data(self, *args, **kwargs):
		context = super(MerchantRegister, self).get_context_data(**kwargs)
		merchant_token = str(uuid.uuid4())
		context['merchant_token']=merchant_token
		return context

	def post(self, request, *args, **kwargs):
		isenabled = False
		response={}
		email = request.POST['email']
		platform = request.POST['platform']
		username = request.POST['name']
		shop_domain = request.POST['mag_domain']
		main_domain = shop_domain #request.POST['domain']
		token = request.POST['merchant_token']
		key = request.POST['shop_key']
		key_secret = request.POST['shop_secret']
		update(platform, shop_domain, main_domain, token)
		try:
			existing_detail = AccountDetail.objects.get(email=email,platform=platform,shop_domain=shop_domain)
			is_deleted = int(existing_detail.is_deleted)

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

				AccountDetail.objects.filter(platform=platform, shop_domain=shop_domain).update(is_deleted=0)

			enabled = int(existing_detail.status)
			if enabled == 1:
				isenabled = True
			merchant_id = existing_detail.id
			token_detail = AccessToken.objects.get(merchant_id=merchant_id)
			access_token = token_detail.access_token
			response = {'Success': 'Saved Successfully','is_enabled': isenabled, 'access_token': access_token}
		except AccountDetail.DoesNotExist:

			try:

				existing_detail = AccountDetail.objects.get(email=email)
				response = {'email':'error','error': 'Email already exists. Please use different email.'}
			except AccountDetail.DoesNotExist:
				try:

					existing_detail = AccountDetail.objects.get(shop_domain=shop_domain)
					response = {'domain':'error','error': 'Shop domain already exists. Please use different domain.'}
				except AccountDetail.DoesNotExist:
					try:

						password = binascii.hexlify(os.urandom(16)).decode()
						encrypted = handler.encrypt(password)
						new_account= AccountDetail(email=email,platform=platform,username=username,shop_domain=shop_domain,main_domain=main_domain,token=token,status=0,is_deleted=0,password=encrypted);
						new_account.save()
						shop_credential = MerchantShopeCredentials(merchant=new_account,key=key,secret=key_secret,platform='Magento')
						shop_credential.save()
						access_token = binascii.hexlify(os.urandom(20)).decode()
						AccessToken.objects.create(merchant_id=new_account.id, access_token=access_token)

						admin_detail = UserDetail(request).get_admin()

						admin_email = admin_detail.emailid

						# email1

						Vars1 = {"account_type": "merchant"}
						template_id1 = "138014"
						send_template(admin_email, Vars1, template_id1)

						# email2
						# Vars = {"first_name": username, "merchant_name": shop_domain}
						# template_id = "136351"
						# send_template(email, Vars, template_id)
						Vars = {"first_name": username, "label_name": username,"password":password}
						template_id = "170804"
						send_template(email, Vars, template_id)
						enabled = int(new_account.status)
						if enabled == 1:
							isenabled = True
						response = {'Success': 'Saved Successfully', 'is_enabled': isenabled, 'access_token': access_token}
						print(response)
					except Exception as e:
						print("------------exception in merchant register---------------------")
						print(e)
						response = {'exception':str(e),'error': 'Error While Saving!'}
						return HttpResponse(json.dumps(response),content_type="application/json")
		return HttpResponse(json.dumps(response),content_type="application/json")

class MerchantLogin(TemplateView):
	template_name = 'merchant/mag_mer_login.html'

	def get_context_data(self, *args, **kwargs):
		context = super(MerchantLogin, self).get_context_data(**kwargs)
		return context

	def post(self, request, *args, **kwargs):
		response={}
		if 'merchant_token' in request.session:
			del request.session['merchant_token']
		if 'access_token' in request.session:
			del request.session['access_token']
		if 'access_token_secret' in request.session:
			del request.session['access_token_secret']
		email = request.POST['loginemail']
		password = request.POST['loginpassword']
		email_obj=AccountDetail.objects.filter(email=email)
		if not email_obj:
			response['emailerror']='email'
		else:
			status=email_obj[0].status
			if status==0:
				response['status']='status'
				return HttpResponse(response)

			# print ('email matched')
			hash_password = email_obj[0].password
			verify_password = handler.verify(password, hash_password)
			if verify_password is False:
				response['passworderror']='password'
			else:
				token=email_obj[0].token
				request.session['merchant_token'] = token
				response['success']='success'
				credentials = MerchantShopeCredentials.objects.get(merchant__id=email_obj[0].id)
				if credentials.access_token and credentials.access_token_secret:
					request.session['access_token'] = credentials.access_token
					request.session['access_token_secret'] = credentials.access_token_secret
					print("-----------------------------------------")
					print(request.session['access_token'])
					print(request.session['access_token_secret'])
		return HttpResponse(response)

class MerchantForgetPassword(TemplateView):
	template_name = 'merchant/mag_mer_forget_password.html'

	def get_context_data(self, *args, **kwargs):
		context = super(MerchantForgetPassword, self).get_context_data(**kwargs)
		return context

	def post(self, request, *args, **kwargs):
		response={}
		email=request.POST.get("email")
		try:
			account=AccountDetail.objects.get(email=email)
			if account.status==0:
				response['status']=0
				response['msg']="This is a inactive account. Contact with administrator to activate your account."
			elif account.platform !="Magento":
				response['status']=0
				response['msg']="This is not right platform for this email. This email is associated with Magento."
			else:
				password = binascii.hexlify(os.urandom(16)).decode()
				encrypted = handler.encrypt(password)
				account.password=encrypted
				account.save()
				first_name = account.username
				Vars = {"first_name": first_name, "merchant_name": account.platform,"password":password}
				template_id = "253891"
				send_template(email, Vars, template_id)
				response['status']=1
				response['msg']="New password is send to "+email+". Please check your email."
		except Account.DoesNotExist:
			response['status']=0
			response['msg']="There is no account associated with this email."
		return HttpResponse(json.dumps(response), content_type='application/json')

class MerchantDashboard(TemplateView):

	template_name = 'merchant/mag_mer_dashboard.html'

	def get_context_data(self, *args, **kwargs):
		context = super(MerchantDashboard, self).get_context_data(**kwargs)
		try:
			token=self.request.session['merchant_token']

			products_list=[]
			try:
				restricted_vendor_id=[]
				details = AccountDetail.objects.get(token=token)
				restricted_vendors = DenyAccess.objects.filter(merchant__id=details.id)

				if restricted_vendors:
					for vendor in restricted_vendors:
						restricted_vendor_id.append(vendor.vendor.id)
					products_list = Products.objects.filter(parent_id=None).exclude(user__id__in=restricted_vendor_id)
				else:
					products_list = Products.objects.all()
				today = datetime.date.today()
				twomonth_past = today - datetime.timedelta(60)
				unpaid_orders = Orders.objects.exclude(paid_by_merchant='paid').order_by("id")
				paid_orders = Orders.objects.filter(paid_by_merchant='paid',date__gte=twomonth_past).order_by("-id")
			except AccountDetail.DoesNotExist:
				return HttpResponseRedirect('/merchant-logout')
			page = self.request.GET.get('page', 1)
			products = Paginator(products_list, 15)
			unpaid = Paginator(unpaid_orders, 10)
			paid = Paginator(paid_orders, 10)
			try:
				products = products.page(page)
			except PageNotAnInteger:
				products = products.page(1)
			except EmptyPage:
				products = products.page(products.num_pages)
			try:
				unpaid = unpaid.page(page)
			except PageNotAnInteger:
				unpaid = unpaid.page(1)
			except EmptyPage:
				unpaid = unpaid.page(unpaid.num_pages)
			try:
				paid = paid.page(page)
			except PageNotAnInteger:
				paid = paid.page(1)
			except EmptyPage:
				paid = paid.page(paid.num_pages)
			context['products'] = products
			context['merchant_id'] = details.id
			context['unpaid'] = unpaid
			context['paid'] = paid
			return context
		except Exception as e:
			print("Exception in dashboard context : "+e)


	def post(self, request, *args, **kwargs):

		return HttpResponse("")
	@method_decorator(merchant_session_check)
	def dispatch(self, *args, **kwargs):
		return super(MerchantDashboard, self).dispatch(*args, **kwargs)

def update(platform, myshop_domain, domain, token):
	try:
		existing_domain = AccountDetail.objects.get(shop_domain=myshop_domain, platform=platform)
		existing_token = existing_domain.token
		AccountDetail.objects.filter(shop_domain=myshop_domain, platform=platform).update(main_domain=domain, token=token)
	except Exception as e:
			pass
	return


class AddProducts(TemplateView):
	template_name = 'merchant/mag_mer_dashboard.html'
	def get(self, request, *arg, **kwargs):

		try:
			#---------------Get Product dhttps://fashioncirclechris.myshopify.com/admin/etails to add on magento shop----------
			product_id=request.GET.get("id")
			product_details = Products.objects.get(id=int(product_id))
			token=request.session['merchant_token']
			#---------Merchant Details And Megento Auth key and secret-------
			merchant = AccountDetail.objects.get(token=token)
			credentials = MerchantShopeCredentials.objects.get(merchant__id=merchant.id)
			MAGENTO_HOST = merchant.shop_domain
			MAGENTO_API_BASE = '%s/api/rest/' % MAGENTO_HOST

			magento = OAuth1Service(
				name               = 'fashion_circle',
				consumer_key       = credentials.key,
				consumer_secret    = credentials.secret,
				request_token_url  = '%s/oauth/initiate' % MAGENTO_HOST,
				access_token_url   = '%s/oauth/token' % MAGENTO_HOST,
				# Customer authorization
				#authorize_url     = '%s/oauth/authorize' % MAGENTO_HOST,
				# Admin authorize url depending on admin urlheaders = {'Content-Type': 'application/json', 'Accept': 'application/json'}
				authorize_url      = '%s/admin/oauth_authorize' % MAGENTO_HOST,
				base_url           = MAGENTO_API_BASE
				)
			if product_details.isconfig:
				if 'access_token' not in request.session:
					oauth_token = request.GET.get('oauth_token')
					oauth_verifier = request.GET.get('oauth_verifier')
					if not oauth_token and not oauth_verifier:
						request_token, request_token_secret = magento.get_request_token(method='POST', params={'oauth_callback':'{}/magento/merchant-add-products?id={}'.format(settings.SITE_URL,product_id)})
						credentials.request_token = request_token
						credentials.request_token_secret = request_token_secret
						credentials.save()
						authorize_url = magento.get_authorize_url(request_token)
						return HttpResponseRedirect(authorize_url)
					else:
						session = magento.get_auth_session(credentials.request_token,
												   credentials.request_token_secret,
												   method='POST',
												   data={'oauth_verifier': oauth_verifier})
						request.session["access_token"] = session.access_token
						request.session["access_token_secret"] = session.access_token_secret
						credentials.access_token = request.session["access_token"]
						credentials.access_token_secret = request.session["access_token_secret"]
						credentials.save()
				tok = request.session["access_token"], request.session["access_token_secret"]
				session = magento.get_session(token=tok, signature=None)
				in_stock=0
				if product_details.quantity >0:
					in_stock =1
				weight="0"
				if product_details.weight_unit=="kg":
					weight=product_details.weight
				elif product_details.weight_unit=="g":
					weight='0.{}'.format(product_details.weight_unit)
				product = {

				"type_id": "simple",
				"attribute_set_id": "4",
				"sku": product_details.sku,
				"name": product_details.title,
				"price": product_details.selling_price,
				"description": product_details.description,
				"short_description": product_details.description,
				"weight":weight,
				"fashion_circle_status" :"yes",
				"status": "1",
				"stock_data" :{
				"manage_stock" : 1,
				"qty":product_details.quantity,
				"is_in_stock":in_stock
				},
				"visibility": "4",
				"tax_class_id": "2"
				}
				child_varients = []
				product_data = {}
				child_products = Products.objects.filter(parent_id=str(product_details.id))
				for child_product in child_products:
					in_stock=0
					if child_product.quantity >0:
						in_stock =1
					weight="0"
					if child_product.weight_unit=="kg":
						weight=child_product.weight
					elif child_product.weight_unit=="g":
						weight='0.{}'.format(child_product.weight_unit)

					varientvalues =child_product.varient_value
					varientvalues = json.loads(varientvalues)

					product_data={
					"type_id": "simple",
					"attribute_set_id": "4",
					"sku": child_product.sku,
					"name": child_product.title,
					"price": child_product.selling_price,
					"description": child_product.description,
					"short_description": child_product.description,
					"weight":weight,
					"fashion_circle_status" :"yes",
					"status": "1",
					"stock_data" :{
					"manage_stock" : 1,
					"qty":child_product.quantity,
					"is_in_stock":in_stock
					},
					"visibility": "4",
					"tax_class_id": "2"

					}
					for level,value in varientvalues.items():
						product_data[level]=value
					child_varients.append(product_data)
				payload_data = {"product":product,"children_product":child_varients,"attribute":json.loads(product_details.varient_value)}
				merchant = AccountDetail.objects.get(token=request.session['merchant_token'])
				headers = {'content-type': 'application/json'}
				varient_add_data = requests.post(merchant.shop_domain+"/testconfig.php", data=json.dumps(payload_data), headers=headers)

				platformproductid = json.loads(varient_add_data.text)
				for parent_elmnt,children_elmnts in platformproductid.items():
					product_added = ProductDetail(merchant=merchant,vendor=product_details.user,product=product_details,platform="Magento",PlatformProductId=parent_elmnt)
					product_added.save()
					images=product_details.images_set.all()
					if images:
						for image in images:
							file_path=settings.BASE_DIR+image.image.url

							extention = (image.image_name).split(".")[-1:]

							with open(file_path,'rb') as image_file:
								encoded_string = base64.b64encode(image_file.read())
							if encoded_string:
								break
						encoded_string = str(encoded_string)
						encoded_string = encoded_string.split("'")
						base64_value = encoded_string[-2:]
						if encoded_string and extention:
							headers = {'Content-Type': 'application/xml', 'Accept': '*/*'}
							payload = '<?xml version="1.0"?><magento_api><file_mime_type>image/{}</file_mime_type><file_content>{}</file_content></magento_api>'.format(extention[0],base64_value[0])
							r = session.post(
							  'products/{}/images'.format(parent_elmnt),
							  header_auth=True,
							  headers=headers,
							  data=payload,
							)
					for sku_id,p_id in children_elmnts.items():
						add_products = Products.objects.get(sku=sku_id)
						product_added = ProductDetail(merchant=merchant,vendor=add_products.user,product=add_products,platform="Magento",PlatformProductId=p_id)
						product_added.save()
						images=add_products.images_set.all()
						if images:
							for image in images:
								file_path=settings.BASE_DIR+image.image.url

								extention = (image.image_name).split(".")[-1:]

								with open(file_path,'rb') as image_file:
									encoded_string = base64.b64encode(image_file.read())
								if encoded_string:
									break
							encoded_string = str(encoded_string)
							encoded_string = encoded_string.split("'")
							base64_value = encoded_string[-2:]
							if encoded_string and extention:
								headers = {'Content-Type': 'application/xml', 'Accept': '*/*'}
								payload = '<?xml version="1.0"?><magento_api><file_mime_type>image/{}</file_mime_type><file_content>{}</file_content></magento_api>'.format(extention[0],base64_value[0])
								r = session.post(
								  'products/{}/images'.format(p_id),
								  header_auth=True,
								  headers=headers,
								  data=payload,
								)
				return HttpResponseRedirect("merchant-dashboard")
			else:
				in_stock=0
				if product_details.quantity >0:
					in_stock =1
				weight="0"
				if product_details.weight_unit=="kg":
					weight=product_details.weight
				elif product_details.weight_unit=="g":
					weight='0.{}'.format(product_details.weight_unit)
				product = {

				"type_id": "simple",
				"attribute_set_id": "4",
				"sku": product_details.sku,
				"name": product_details.title,
				"price": product_details.selling_price,
				"description": product_details.description,
				"short_description": product_details.description,
				"weight":weight,
				"fashion_circle_status" :"yes",
				"status": "1",
				"stock_data" :{
				"manage_stock" : 1,
				"qty":product_details.quantity,
				"is_in_stock":in_stock
				},
				"visibility": "4",
				"tax_class_id": "2"
				}
				#-----------------------Set request header for post api/res/products/products---------
				headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

				if 'access_token' not in request.session:
					oauth_token = request.GET.get('oauth_token')
					oauth_verifier = request.GET.get('oauth_verifier')
					if not oauth_token and not oauth_verifier:
						request_token, request_token_secret = magento.get_request_token(method='POST', params={'oauth_callback':'{}/magento/merchant-add-products?id={}'.format(settings.SITE_URL,product_id)})
						credentials.request_token = request_token
						credentials.request_token_secret = request_token_secret
						credentials.save()
						authorize_url = magento.get_authorize_url(request_token)
						return HttpResponseRedirect(authorize_url)
					else:
						session = magento.get_auth_session(credentials.request_token,
												   credentials.request_token_secret,
												   method='POST',
												   data={'oauth_verifier': oauth_verifier})
						request.session["access_token"] = session.access_token
						request.session["access_token_secret"] = session.access_token_secret
						credentials.access_token = request.session["access_token"]
						credentials.access_token_secret = request.session["access_token_secret"]
						credentials.save()
						tok = request.session["access_token"], request.session["access_token_secret"]
						session = magento.get_session(token=tok, signature=None)



						payload = product
						r = session.post(
						    'products',
						    header_auth=True,
						    headers=headers,
						    data=json.dumps(payload),
						)

						if r.status_code==200:
							article_url = r.headers['location']
							location_list = article_url.rsplit('/',1)
							magento_product_id = location_list[-1]
							product_added = ProductDetail(merchant=merchant,vendor=product_details.user,product=product_details,platform="Magento",PlatformProductId=magento_product_id)
							product_added.save()
							encoded_string=""
							extention=""
							images=product_details.images_set.all()
							if images:
								for image in images:
									file_path=settings.BASE_DIR+image.image.url

									extention = (image.image_name).split(".")[-1:]

									with open(file_path,'rb') as image_file:
										encoded_string = base64.b64encode(image_file.read())
									if encoded_string:
										break
								encoded_string = str(encoded_string)
								encoded_string = encoded_string.split("'")
								base64_value = encoded_string[-2:]
								if encoded_string and extention:
									headers = {'Content-Type': 'application/xml', 'Accept': '*/*'}
									payload = '<?xml version="1.0"?><magento_api><file_mime_type>image/{}</file_mime_type><file_content>{}</file_content></magento_api>'.format(extention[0],base64_value[0])
									r = session.post(
									  'products/{}/images'.format(magento_product_id),
									  header_auth=True,
									  headers=headers,
									  data=payload,
									)
						if r.status_code==403 or r.status_code==401:
							response=json.loads(r.text)
							response_body_list = response['messages']['error']
							if response_body_list[0]['message']=='Access denied.' or response_body_list[0]['message']=='oauth_problem=token_revoked':
								if 'access_token' in request.session:
									del request.session['access_token']
									del request.session['access_token_secret']
								return HttpResponseRedirect("merchant-dashboard")

						return HttpResponseRedirect("merchant-dashboard")

				else:
					tok = request.session["access_token"], request.session["access_token_secret"]
					session = magento.get_session(token=tok, signature=None)
					payload = product
					r = session.post(
						'products',
						header_auth=True,
						headers=headers,
						data=json.dumps(payload),
					)
					if r.status_code==200:
						article_url = r.headers['location']
						location_list = article_url.rsplit('/',1)
						magento_product_id = location_list[-1]
						product_added = ProductDetail(merchant=merchant,vendor=product_details.user,product=product_details,platform="Magento",PlatformProductId=magento_product_id)
						product_added.save()
						encoded_string=""
						extention=""
						images=product_details.images_set.all()
						if images:
							for image in images:
								file_path=settings.BASE_DIR+image.image.url

								extention = (image.image_name).split(".")[-1:]

								with open(file_path,'rb') as image_file:
									encoded_string = base64.b64encode(image_file.read())
								if encoded_string:
									break
							encoded_string = str(encoded_string)
							encoded_string = encoded_string.split("'")
							base64_value = encoded_string[-2:]
							if encoded_string and extention:
								headers = {'Content-Type': 'application/xml', 'Accept': '*/*'}
								payload = '<?xml version="1.0"?><magento_api><file_mime_type>image/{}</file_mime_type><file_content>{}</file_content></magento_api>'.format(extention[0],base64_value[0])
								r = session.post(
								  'products/{}/images'.format(magento_product_id),
								  header_auth=True,
								  headers=headers,
								  data=payload,
								)
					if r.status_code==403 or r.status_code==401:
						response=json.loads(r.text)
						response_body_list = response['messages']['error']
						if response_body_list[0]['message']=='Access denied.' or response_body_list[0]['message']=='oauth_problem=token_revoked':
							if 'access_token' in request.session:
								del request.session['access_token']
								del request.session['access_token_secret']
							return HttpResponseRedirect("merchant-dashboard")
					else:
						print("--------------Other status---------------------")
						print(r.status_code)
						print(r.content)
					return HttpResponseRedirect("merchant-dashboard")
		except Exception as e:
			print(e)
			return HttpResponseRedirect("merchant-dashboard")

class RemoveProduct(TemplateView):
	template_name = 'merchant/mag_mer_dashboard.html'
	def get(self, request, *arg, **kwargs):
		product_id = request.GET.get("id")
		try:
			headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
			token=request.session['merchant_token']
			#---------Merchant Details And Megento Auth key and secret-------
			merchant = AccountDetail.objects.get(token=token)
			merchantproduct = ProductDetail.objects.filter(merchant=merchant,PlatformProductId=product_id)
			credentials = MerchantShopeCredentials.objects.get(merchant__id=merchant.id)
			MAGENTO_HOST = merchant.shop_domain
			MAGENTO_API_BASE = '%s/api/rest/' % MAGENTO_HOST

			magento = OAuth1Service(
				name               = 'fashion_circle',
				consumer_key       = credentials.key,
				consumer_secret    = credentials.secret,
				request_token_url  = '%s/oauth/initiate' % MAGENTO_HOST,
				access_token_url   = '%s/oauth/token' % MAGENTO_HOST,
				authorize_url      = '%s/admin/oauth_authorize' % MAGENTO_HOST,
				base_url           = MAGENTO_API_BASE
				)
			if 'access_token' not in request.session:
				oauth_token = request.GET.get('oauth_token')
				oauth_verifier = request.GET.get('oauth_verifier')
				if not oauth_token and not oauth_verifier:
					request_token, request_token_secret = magento.get_request_token(method='POST', params={'oauth_callback':'{}/magento/merchant-remove-product?id={}'.format(settings.SITE_URL,product_id)})
					credentials.request_token = request_token
					credentials.request_token_secret = request_token_secret
					credentials.save()
					authorize_url = magento.get_authorize_url(request_token)
					return HttpResponseRedirect(authorize_url)
				else:
					session = magento.get_auth_session(credentials.request_token,
											   credentials.request_token_secret,
											   method='POST',
											   data={'oauth_verifier': oauth_verifier})
					request.session["access_token"] = session.access_token
					request.session["access_token_secret"] = session.access_token_secret
					credentials.access_token = request.session["access_token"]
					credentials.access_token_secret = request.session["access_token_secret"]
					credentials.save()
					tok = request.session["access_token"], request.session["access_token_secret"]
					session = magento.get_session(token=tok, signature=None)
					if merchantproduct[0].product.isconfig:
						childrens = Products.objects.filter(parent_id=merchantproduct[0].product.id)
						for product in childrens:
							magento_product = ProductDetail.objects.filter(merchant=merchant,product__id=product.id)
							if magento_product:
								r = session.delete(
									'products/{}'.format(magento_product[0].PlatformProductId),
									header_auth=True,
									headers=headers
								)
								if r.status_code==200:
									magento_product[0].delete()
								if r.status_code==404:
									response=json.loads(r.text)
									response_body_list = response['messages']['error']
									if response_body_list[0]['message']=='Resource not found.':
										magento_product[0].delete()
						r = session.delete(
							'products/{}'.format(product_id),
							header_auth=True,
							headers=headers
						)
						if r.status_code==200:
							ProductDetail.objects.filter(merchant=merchant,PlatformProductId=product_id).delete()
						if r.status_code==404:
							response=json.loads(r.text)
							response_body_list = response['messages']['error']
							if response_body_list[0]['message']=='Resource not found.':
								ProductDetail.objects.filter(merchant=merchant,PlatformProductId=product_id).delete()
								return HttpResponseRedirect("merchant-dashboard")
					else:
						r = session.delete(
							'products/{}'.format(product_id),
							header_auth=True,
							headers=headers
						)
						if r.status_code==200:
							ProductDetail.objects.filter(merchant=merchant,PlatformProductId=product_id).delete()
						if r.status_code==404:
							response=json.loads(r.text)
							response_body_list = response['messages']['error']
							if response_body_list[0]['message']=='Resource not found.':
								ProductDetail.objects.filter(merchant=merchant,PlatformProductId=product_id).delete()
								return HttpResponseRedirect("merchant-dashboard")
					return HttpResponseRedirect("merchant-dashboard")

			else:
				tok = request.session["access_token"], request.session["access_token_secret"]
				session = magento.get_session(token=tok, signature=None)
				if merchantproduct[0].product.isconfig:
					childrens = Products.objects.filter(parent_id=merchantproduct[0].product.id)
					print("children")
					print(childrens)
					for product in childrens:
						magento_product = ProductDetail.objects.filter(merchant=merchant,product__id=product.id)
						print("magento product")
						print(magento_product)
						if magento_product:
							r = session.delete(
								'products/{}'.format(magento_product[0].PlatformProductId),
								header_auth=True,
								headers=headers
							)
							print("response")
							print(r.content)
							if r.status_code==200:
								magento_product[0].delete()
							if r.status_code==403:
								response=json.loads(r.text)
								response_body_list = response['messages']['error']
								if response_body_list[0]['message']=='Access denied.':
									if 'access_token' in request.session:
										del request.session['access_token']
										del request.session['access_token_secret']
									return HttpResponseRedirect("merchant-remove-product?id={}".format(product_id))
							if r.status_code==404:
								response=json.loads(r.text)
								response_body_list = response['messages']['error']
								if response_body_list[0]['message']=='Resource not found.':
									magento_product[0].delete()
					r = session.delete(
						'products/{}'.format(product_id),
						header_auth=True,
						headers=headers
					)
					if r.status_code==200:
						ProductDetail.objects.filter(merchant=merchant,PlatformProductId=product_id).delete()
						return HttpResponseRedirect("merchant-dashboard")
					if r.status_code==403:
						response=json.loads(r.text)
						response_body_list = response['messages']['error']
						if response_body_list[0]['message']=='Access denied.':
							if 'access_token' in request.session:
								del request.session['access_token']
								del request.session['access_token_secret']
							return HttpResponseRedirect("merchant-remove-product?id={}".format(product_id))
					if r.status_code==404:
						response=json.loads(r.text)
						response_body_list = response['messages']['error']
						if response_body_list[0]['message']=='Resource not found.':
							ProductDetail.objects.filter(merchant=merchant,PlatformProductId=product_id).delete()
							return HttpResponseRedirect("merchant-dashboard")
				else:
					r = session.delete(
						'products/{}'.format(product_id),
						header_auth=True,
						headers=headers
					)
					if r.status_code==200:
						ProductDetail.objects.filter(merchant=merchant,PlatformProductId=product_id).delete()
						return HttpResponseRedirect("merchant-dashboard")
					if r.status_code==403:
						response=json.loads(r.text)
						response_body_list = response['messages']['error']
						if response_body_list[0]['message']=='Access denied.':
							if 'access_token' in request.session:
								del request.session['access_token']
								del request.session['access_token_secret']
							return HttpResponseRedirect("merchant-remove-product?id={}".format(product_id))
					if r.status_code==404:
						response=json.loads(r.text)
						response_body_list = response['messages']['error']
						if response_body_list[0]['message']=='Resource not found.':
							ProductDetail.objects.filter(merchant=merchant,PlatformProductId=product_id).delete()
							return HttpResponseRedirect("merchant-dashboard")
		except Exception as e:
			print("Exception occur")
			print(type(e))
		return HttpResponseRedirect("merchant-dashboard")

class PaypalAdaptivePayment(TemplateView):
	template_name = 'merchant/mag_paypal_success.html'
	def get(self,request, *args, **kwargs):
		transaction_id = request.GET.get("transaction_id")
		try:
			paypal_order = PaypalAdaptive.objects.get(uiid=str(transaction_id))
			paypal_order.status = True
			paypal_order.save()
			paypal_order.order.paid_by_merchant='paid'
			paypal_order.order.save()

			return HttpResponseRedirect("/magento/merchant-dashboard?tabv=2")
		except PaypalAdaptive.DoesNotExist:
			return render(request,self.template_name,{"msg":"Paypal order not found when updating status."})

	def post(self,request, *args, **kwargs):
		try:
			order_id = request.POST.get("id")
			order = Orders.objects.get(id=int(order_id))
			transaction_id = str(uuid.uuid4())[:15]
			products_in_order = OrderProducts.objects.filter(order__id=order.id)
			commission = Commission.objects.get(id=1)
			commission_amount=0
			for product in products_in_order:
				commission_amount += (commission.commission * product.product_price)/100
			commission_amount = round(commission_amount,2)
			receiver=[{'amount': commission_amount, 'email': 'aman_katoch@esferasoft.com'}] #Enter chris email here and his commission in amount
			products_order = OrderProducts.objects.filter(order__id=order.id).values('user').annotate(Sum('product_price'))
			for product in products_order:
				vendor = Account.objects.get(id=product['user'])
				payment_mail=""
				if vendor.paypal_emailid:
					payment_mail = vendor.paypal_emailid
				else:
					payment_mail = vendor.emailid
				receiver.append({'amount': product['product_price__sum'], 'email': payment_mail})#product.user.emailid
			HEADERS = {
			    'X-PAYPAL-SECURITY-USERID': 'pankaj_kumarsharma_api1.esferasoft.com',
			    'X-PAYPAL-SECURITY-PASSWORD': 'HF86DZHEU7GBLAAV',
			    'X-PAYPAL-SECURITY-SIGNATURE': 'AFcWxV21C7fd0v3bYYYRCpSSRl31ARjgc-q2-DAFXRaeZgLWriIxfcE9',
			    # this application-id is the sandbox value, sa	me for everyone
			    'X-PAYPAL-APPLICATION-ID' : 'APP-80W284485P519543T',
				'X-PAYPAL-SERVICE-VERSION':'1.1.0',
			    'X-PAYPAL-REQUEST-DATA-FORMAT': 'JSON',
			    'X-PAYPAL-RESPONSE-DATA-FORMAT': 'JSON'
			}

			# sandbox API endpoint:
			ENDPOINT_PAY = 'https://svcs.sandbox.paypal.com/AdaptivePayments/Pay'
			PAYLOAD = {
				'actionType': 'PAY',
				'currencyCode': 'USD',
				'receiverList': {
				    'receiver': receiver
				},
				'returnUrl': 'http://ui.fashioncircle.de/magento/payment?transaction_id={}'.format(transaction_id),
				'cancelUrl': 'http://ui.fashioncircle.de/magento/payment/fail',
				'requestEnvelope': {
				    'errorLanguage': 'en_US',
				    'detailLevel': 'ReturnAll'
				},
				# Allowed values: SENDER, PRIMARYRECEIVER, EACHRECEIVER, SECONDARYONLY
				'feesPayer': 'EACHRECEIVER',
				'reverseAllParallelPaymentsOnError': True,
				'memo': 'no description',
			}

			r = requests.post(ENDPOINT_PAY, data=json.dumps(PAYLOAD), headers=HEADERS)
			if r.json()['responseEnvelope']['ack'] == 'Success':
				paypal_pay = PaypalAdaptive(order=order,uiid=transaction_id,pay_key=r.json()['payKey'])
				paypal_pay.save()
				redirect_url ='https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_ap-payment&paykey={}'.format(r.json()['payKey'])
				return HttpResponseRedirect(redirect_url)
			else:
			    print(r.content)
		except Exception as e:
			print(e)
		return render(request,self.template_name,{})

class FailPayment(TemplateView):
	template_name = 'merchant/mag_paypal_failure.html'
	def get(self, request, *args, **kwargs):

		return HttpResponseRedirect("/magento/merchant-dashboard?tabv=2")


class AddVendorProduct(View):

	def image_generate(self,imgage,url):
		image_path=""
		filename=url.split("/")[-1]
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
		category = ""
		account = Account.objects.get(token=request.session['vendor_token'])
		if 'category' in request.POST:
			category = request.POST['category']
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
		quantity =int(float(request.POST['quantity']))

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



		# category_id = 0

		existing_category = Categories.objects.filter(title=category)
		category_id = existing_category[0].id

		weight = request.POST['weight']
		weight_unit=""
		if 'weight_unit' in request.POST:
			weight_unit = request.POST['weight_unit']

		product_obj = Products(user_id=account.id, category_id=category_id, title=title, description=description, selling_price=selling_price, dropshipping_price=dropshipping_price, sku=sku, quantity=quantity, PlatformProductId=int(PlatformProductId), platform=platform,wholesale_price=wholesale_price, weight=weight, weight_unit=weight_unit,dropshipping_percentage=dropshipping_percentage,wholesale_percentage=wholesale_percentage)
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
			image_obj = Images.objects.create(user_id=account.id,product_id=product_id)


		return HttpResponseRedirect("/magento/vendor_dashboard")

class VendorRemoveProduct(View):
	"""docstring for VendorRemoveProduct."""
	def post(self, request):
		platformproduct_id = request.POST['product_id']
		response = {}
		product_id = request.POST['product_id']
		print("-----------------vendor remove product call-------------------------")
		deleteMerchantMagentoProduct(request,product_id)

		Products.objects.filter(id=product_id).delete()

		return HttpResponseRedirect("/magento/vendor_dashboard")


class ControlMerchantAccess(View):
	def post(self,request):
		access = request.POST["access"]
		if access == 'true':
			access=True
		else:
			access=False
		vendor = request.POST["vendor"]
		merchant = request.POST["merchant"]
		accountdetail = AccountDetail.objects.get(id=int(merchant))
		if access:
			DenyAccess.objects.filter(vendor__id=int(vendor),merchant__id=int(merchant)).delete()
			return HttpResponse(json.dumps({"msg":'Great!! '+accountdetail.username+' Has Access Now'}),content_type="application/json")
		else:
			account = Account.objects.get(id=int(vendor))
			denyaccess = DenyAccess(vendor=account,merchant=accountdetail)
			denyaccess.save()
			return HttpResponse(json.dumps({"msg":'Great!! '+accountdetail.username+'Is Blocked Now '}),content_type="application/json")

def deleteMerchantMagentoProduct(request,product_id):

	try:
		headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
		product = Products.objects.get(id=int(product_id))
		productdetail = ProductDetail.objects.filter(product__id=product.id,platform="Magento")
		for shops in productdetail:
		#---------Merchant Details And Megento Auth key and secret-------
			merchant = shops.merchant
			credentials = MerchantShopeCredentials.objects.get(merchant__id=merchant.id)
			MAGENTO_HOST = merchant.shop_domain
			MAGENTO_API_BASE = '%s/api/rest/' % MAGENTO_HOST
			magento = OAuth1Service(
				name               = 'fashion_circle',
				consumer_key       = credentials.key,
				consumer_secret    = credentials.secret,
				request_token_url  = '%s/oauth/initiate' % MAGENTO_HOST,
				access_token_url   = '%s/oauth/token' % MAGENTO_HOST,
				authorize_url      = '%s/admin/oauth_authorize' % MAGENTO_HOST,
				SITE_URL           = MAGENTO_API_BASE
				)

			tok = credentials.access_token, credentials.access_token_secret
			session = magento.get_session(token=tok, signature=None)
			r = session.delete(
				'products/{}'.format(shops.PlatformProductId),
				header_auth=True,
				headers=headers
			)
			print("---------------delete product from store-------------------")
			print(r.status_code)
			print(r.content)
			if r.status_code==200:
				return True
			else:
				return False
	except Exception as e:
		print(e)
		return False

class PaypalEmail(View):
	def get(self,request):
		response={}
		try:
			token = request.session["vendor_token"]
			paypal_email = request.GET["paypal_email"]
			vendor = Account.objects.get(token=token)
			vendor.paypal_emailid = paypal_email
			vendor.save()
			response['success'] = "Paypal Email Updated Successfully"
			return HttpResponse(json.dumps(response),content_type="application/json")
		except Account.DoesNotExist:
			response["error"]="Account not exists.";
			return HttpResponse(json.dumps(response),content_type="application/json")
		except Exception as e:
			print(e)
			response["error"]="Some error occur. Please try again.";
			return HttpResponse(json.dumps(response),content_type="application/json")


class ProductAvailable(APIView):
	def post(self, request):

		response = {}

		if 'HTTP_ACCESS_TOKEN' not in request.META or not request.META['HTTP_ACCESS_TOKEN']:
			response = {"error": "You don't have access to send order email to vendor."}
			return Response(response)

		access_token = request.META['HTTP_ACCESS_TOKEN']
		verify_shop = request.META['HTTP_SHOP']

		existing_token = ApiAuth.objects.filter(platform_key=access_token,platform_name=verify_shop)
		if not existing_token:
			response = {"error": "You don't have access to send order email to vendor."}
			return Response(response)


		account = AccountDetail.objects.filter(shop_domain=request.POST['shop_domain'])
		if account:
			productexists = ProductDetail.objects.filter(merchant=account,PlatformProductId=request.POST['product_id'])
			if productexists:
				response = {"available": "true"}
			else:
				response = {"available": "false"}
		else:
			response = {"available": "false"}

		return Response(response)

class UninstallMerchant(APIView):

	def delete(self, request):
		if 'HTTP_ACCESS_TOKEN' not in request.META or not request.META['HTTP_ACCESS_TOKEN']:
			response = {"error": "You don't have access to send order email to vendor."}
			return Response(response)

		access_token = request.META['HTTP_ACCESS_TOKEN']
		verify_shop = request.META['HTTP_SHOP']

		existing_token = ApiAuth.objects.filter(platform_key=access_token,platform_name=verify_shop)
		if not existing_token:
			response = {"error": "You don't have access to send order email to vendor."}
			return Response(response)
		domain = request.POST['shop_domain']

		existing_domain = AccountDetail.objects.filter(shop_domain=domain)
		if not existing_domain:
			response = {"error": "Domain does not exist."}
			return HttpResponse(json.dumps(response))

		merchant_id = existing_domain[0].id
		merchant_name = existing_domain[0].username
		merchant_email = existing_domain[0].email

		access_token = request.META['HTTP_ACCESS_TOKEN']


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

class ViewVarientProduct(View):
	def get(self,request):
		response={}
		try:
			product_data = request.GET['product_data']
			product_data = product_data[:-1]
			product_data = product_data[1:]
			params = json.loads(product_data)
			parent_product_id=0
			qry_conditions = ""
			for parent_id,varient_props in params.items():
				parent_product_id=parent_id
				for serch_params in varient_props:
					search_param='"{}"'.format(serch_params)
					qry_conditions +="and varient_value like '%%{}%%'".format(search_param)
			qry = "select id,selling_price from shopify_products where parent_id={} {}".format(parent_product_id,qry_conditions)
			resulted_data = Products.objects.raw(qry)

			response["price"] = resulted_data[0].selling_price
			images_list=[]
			images = Images.objects.filter(product__id=resulted_data[0].id)
			if images:
				for image in images:
					images_list.append(image.image.url)
			if images_list:
					response["images"]=images_list
			response["status"]="success"
			return HttpResponse(json.dumps(response),content_type="application/json")
		except Exception as e:
			response["status"]="fail"
			return HttpResponse(json.dumps(response),content_type="application/json")
