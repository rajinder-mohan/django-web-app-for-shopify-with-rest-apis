from django.shortcuts import render, redirect
from .forms import LoginForm, RegisterForm, ProductForm, ForgotPasswordForm
from .models import Account, Products,AccountType,Vendor, Categories, Commission
from images.models import Images
from django.http import HttpResponse
import hashlib
import random
import json
from django.conf import settings
from django.template.loader import render_to_string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from passlib.hash import django_pbkdf2_sha256 as handler
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.core.paginator import Paginator ,PageNotAnInteger,EmptyPage
from shopify.utils.userdetails import UserDetail
import sys

from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView

from orders.serializers import OrderProductsSerializer

from django_datatables_view.base_datatable_view import BaseDatatableView

from .tables import AccountTable

from table.views import FeedDataView

from mailjet_rest import Client
import os

from orders.models import Orders, OrderProducts

from datetime import date

import pycountry

import requests

from merchants.models import ProductDetail, AccountDetail

from django.conf import settings

from django.db import connection

# api_key = '3b114125714480a4a3b24cc9cd32bcb5'
# api_secret = '15332d66a5ec71ff5b42e9077aa624bd'
mailjet = Client(auth=(settings.MAILJET_API_KEY, settings.MAILJET_API_SECRET))


class AccountDataView(FeedDataView):

	token = AccountTable.token

	def get_queryset(self):
		return super(AccountDataView, self).get_queryset().filter(id=1)

def people(request):
	people = AccountTable(Account.objects.filter(account_id=3))
	return render(request, "table_data.html", {'people': people})


class AccountListJson(BaseDatatableView):
	model = Account

	columns = ['first_name', 'last_name', 'emailid']

	order_columns = ['first_name', 'last_name', '']

	max_display_length = 10

	def render_column(self, row, column):
		if column == "first_name":
			return '{0} {1}'.format(row.first_name, row.last_name)
		else:
			return super(AccountListJson, self).render_column(row, column)

	def filter_queryset(self, qs):
		search = self.request.GET.get(u'search[value]', None)
		if search:
			qs = qs.filter(first_name__isstartswith=search)
		return qs


class AccountsList(ListView):
	model = Account
	context_object_name = "all_accounts"


class CategoryDetailView(DetailView):
	model = Categories

	def get_context_data(self, **kwargs):
		context = super(CategoryDetailView, self).get_context_data(**kwargs)
		products = Products.objects.all()
		context['products_list'] = products
		return context


# class Vendor(TemplateView):
# 	model = Vendor
# 	template_name = "vendor.html"


class ImagesView(ListView):
	model = Images

	def get(self, *args, **kwargs):
		last_image = self.get_queryset().latest('created_date')
		response = HttpResponse('')
		response['image_name'] = last_image.image_name
		return HttpResponse(response)

	def render_to_response(self, context, **reponse_kwargs):
		return self.response

def login(request):
	posted_data = {}
	user=UserDetail(request).getLoginUser()
	if  user:
		if UserDetail(request).is_vendor():
			return redirect("/dashboard")
		else:
			return redirect("/mvpadmin")
	if request.method == "POST":
		posted_data = request.POST
		emailid = request.POST['emailid']
		password = request.POST['password']

		form = LoginForm(request.POST, request=request)

		if form.is_valid():
			user = Account.objects.get(emailid=emailid)
			# user_id = user.id
			# user_type= user.account_id
			# request.session['user_id'] = user_id
			UserDetail(request).setSession(user)
			if UserDetail(request).is_admin():
				return redirect('/mvpadmin')
			return redirect('/dashboard')
	else:
		form = LoginForm(request=request)
	return render(request, "login.html", {'form': form, 'posted_data': posted_data})

def dashboard(request):
	user=UserDetail(request).getLoginUser()
	if not user:
		#messages.add_message(request, messages.INFO, 'Please login firstly !!')
		return redirect("/")
	user_id=user['id']
	products_list = []
	products=[]
	# sql='SELECT dp.*, di.* FROM shopify_products AS dp LEFT JOIN (SELECT t1.* FROM images_images t1 WHERE t1.updated_date =(SELECT MAX(t2.updated_date) FROM images_images t2 WHERE t2.product_id = t1.product_id) ) di ON dp.id = di.product_id LEFT JOIN shopify_account as ac ON dp.user_id=ac.id WHERE dp.user_id={0} AND ac.is_app_uninstall=False ORDER BY di.product_id'.format(user_id)
	accounts=Account.objects.filter(id=user_id)
	check_status=accounts[0].is_app_uninstall
	if check_status is False:
		product=Products.objects.filter(user_id=user_id)
		for prod in product:
			id=prod.id
			title=prod.title
			description=prod.description
			selling_price=prod.selling_price
			dropshipping_price=prod.dropshipping_price
			wholesale_price=prod.wholesale_price
			sku=prod.sku
			quantity=prod.quantity
			image=Images.objects.filter(user_id=user_id,product_id=prod.id).order_by('-id')[0]
			image=image.image
			weight = prod.weight
			weight_unit = prod.weight_unit
			# image=image[-1]
			products.append({'id':id,'title':title,'description':description,'selling_price':selling_price,'dropshipping_price':dropshipping_price,'wholesale_price':wholesale_price,'sku':sku,'quantity':quantity,'image':image, 'weight': weight, 'weight_unit': weight_unit})
	else:
		product=Products.objects.filter(user_id=user_id,PlatformProductId=0)
		for prod in product:
			id=prod.id
			title=prod.title
			description=prod.description
			selling_price=prod.selling_price
			dropshipping_price=prod.dropshipping_price
			wholesale_price=prod.wholesale_price
			sku=prod.sku
			quantity=prod.quantity
			image=Images.objects.filter(user_id=user_id,product_id=prod.id).order_by('-id')[0]
			image=image.image
			weight = prod.weight
			weight_unit = prod.weight_unit

			products.append({'id':id,'title':title,'description':description,'selling_price':selling_price,'dropshipping_price':dropshipping_price,'wholesale_price':wholesale_price,'sku':sku,'quantity':quantity,'image':image, 'weight': weight, 'weight_unit': weight_unit})


	paginator=Paginator(list(products),6)
	page=request.GET.get("page")
	try:
		products=paginator.page(page)
	except PageNotAnInteger:
		products=paginator.page(1)
	except EmptyPage:
		products=paginator.page(paginator.num_pages)

	login_user = "vendor"
	page_name = "My Products"

	all_images=Images.objects.filter(user_id=user_id)

	if UserDetail(request).is_vendor():
		login_user = "vendor"
	else:
		login_user = "admin"
		page_name = "My Products"

	vendor_name = "My Products"

	return render(request, "dashboard.html", {'products_list': products, 'login_user': login_user, 'page': page, 'vendor_name': vendor_name, 'page_name': page_name})

def logout(request):
	UserDetail(request).clearSession()
	return redirect('/')

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

def register(request):
	posted_data = {}
	#get the current page url request.build_absolute_uri()
	if request.method == "POST":

		posted_data = request.POST
		form = RegisterForm(request.POST, request=request)
		if form.is_valid():
			first_name = request.POST['first_name']
			last_name = request.POST['last_name']
			emailid = request.POST['emailid']
			password = request.POST['password']
			website = request.POST['website']
			country = request.POST['country']

			if not website.startswith("http://"):
				website = "http://" + website


			encrypted_password = handler.encrypt(password)

			if 'vendor' in request.POST:
				account_type=AccountType.objects.get(type="vendor")
			else:
				account_type=AccountType.objects.get(type="user")


			detail = Account(first_name=first_name, last_name=last_name, emailid=emailid,  paypal_emailid=emailid, password=encrypted_password,account_id=account_type.id, website=website, country=country)
			detail.save()
			if account_type.type=="vendor":
				vendor_detail=Vendor(user_id=detail.id,vendor=request.POST['vendor'])
				vendor_detail.save()

				link = "http://"+request.META['HTTP_HOST']

				admin_detail = UserDetail(request).get_admin()
				admin_email = admin_detail.emailid

				# add commission
				add_commission = Commission(user_id=detail.id, commission=10)
				add_commission.save()

				# email1
				Vars1 = {"account_type": "label"}
				template_id1 = "138014"
				send_template(admin_email, Vars1, template_id1)

				# email2
				Vars = {"first_name": first_name, "label_name": request.POST['vendor']}
				template_id = "136350"
				send_template(emailid, Vars, template_id)

				messages.add_message(request, messages.SUCCESS, 'Registered Successfully. We will send you an email once your application and account has been approved.')
			return redirect("/")

			#return HttpResponse("Registered Successfully. Please check your mail to activate your account.")
	else:
		form = RegisterForm(request=request)

	all_countries = []

	countries_list = list(pycountry.countries)
	for country in countries_list:
		all_countries.append(country.name)

	return render(request, "register.html", {'form': form, 'posted_data': posted_data, 'all_countries': all_countries})

def add_product(request):
	posted_data = {}
	user=UserDetail(request).getLoginUser()
	if not user:
		#messages.add_message(request, messages.INFO, 'Please login firstly !!')
		return redirect("/")

	user_id=user['id']
	login_user = "vendor"
	page_name = "add_product"

	if UserDetail(request).is_vendor():
		login_user = "vendor"
	else:
		login_user = "admin"

	if request.method == "POST":
		posted_data = request.POST
		title = request.POST['title']
		description = request.POST['description']
		category = request.POST['category']
		selling_price = float(request.POST['selling_price'])
		dropshipping_price = float(request.POST['dropshipping_price'])
		wholesale_price = float(request.POST['wholesale_price'])
		quantity = request.POST['quantity']

		token = request.POST['token']

		weight = request.POST['weight']

		weight_unit = request.POST['weight_unit']

		if 'is_tax' in request.POST:
			is_tax=request.POST['is_tax']
		else:
			is_tax=0
		if 'sku' in request.POST:
			sku = request.POST['sku']
		else:
			sku=0
		barcode = request.POST['barcode']
		user_id=user_id

		form = ProductForm(request.POST, request=request)
		if form.is_valid():
			product_detail = Products(user_id=user_id, title=title, description=description, selling_price=selling_price, dropshipping_price=dropshipping_price, wholesale_price=wholesale_price, sku=sku, barcode=barcode, category_id=category, quantity=quantity, weight=weight, weight_unit=weight_unit)
			product_detail.save()
			product_id = product_detail.id

			# images
			Images.objects.filter(token=token).update(product_id=product_id)

			#messages.add_message(request, messages.SUCCESS, 'Products saved successfully')
			if login_user == "vendor":
				return redirect("/dashboard")
			else:
				return redirect('/mvpadmin/products')
	else:
		form = ProductForm(request=request)


	vendor = ''

	categories_list = []

	categories = Categories.objects.filter(user_id=1)
	for category in categories:
		category_id = category.id
		category_name = category.title
		categories_list.append({'category_id': category_id, 'category_name': category_name})
	user_detail = Account.objects.filter(id=user_id)
	# if user_detail:
	# 	vendor = user_detail[0].account_id
	return render(request, "add_product.html", {'categories_list': categories_list, 'login_user': login_user, 'form': form, 'page_name': page_name, 'posted_data': posted_data})

def activate_account(request, user_id, activation_key):
	Account.objects.filter(id=user_id, activation_key=activation_key).update(status=1)
	link = "http://"+request.META['HTTP_HOST']

	html = "<h3>Account Activated</h3><p>Your account is activated. Click <a href='{link}'>here</a> to login account.</p>".format(link=link)
	return HttpResponse(html)

def all_products(request):
	user_id = request.session['user_id']

	users = Account.objects.filter(~Q(id=user_id))

	vendors_list = []

	for user in users:

		products_list = []
		vendor_id = user.id

		vendor = user.vendor

		products = Products.objects.filter(user_id=vendor_id)
		for product in products:
			title = product.title
			description = product.description
			selling_price = product.selling_price
			dropshipping_price = product.dropshipping_price
			wholesale_price = product.wholesale_price
			sku = product.sku
			weight = product.weight
			weight_unit = product.weight_unit
			products_list.append({'title': title, 'description': description, 'selling_price': selling_price, 'wholesale_price': wholesale_price, 'dropshipping_price': dropshipping_price, 'sku': sku, 'weight': weight, 'weight_unit': weight_unit})

	vendors_list.append({'vendor': vendor, 'products_list': products_list})

	return render(request, "all_products.html", {'vendors_list': vendors_list})

def orders_list(request):
	user=UserDetail(request).getLoginUser()
	if not user:
		return redirect("/")

	user_id=user['id']

	today = date.today()

	orders = OrderProducts.objects.filter(user_id=user_id, date__month=today.month, date__year=today.year)
	serializer = OrderProductsSerializer(orders, many=True, context={'user_type': "vendor"})
	total_amount = sum([order['total_price'] for order in serializer.data])

	filtered_orders = OrderProducts.objects.filter(user_id=user_id, date__month=today.month, date__year=today.year).values_list('order_id').distinct()

	order_list = []

	for order in filtered_orders:
		order_id = order[0]
		existing_order = Orders.objects.get(id=order_id)
		OrderId = existing_order.OrderId
		order_date = existing_order.date.strftime("%d %B, %Y")
		orderdetail = OrderProducts.objects.filter(order_id=order_id, user_id=user_id)

		all_orders = []

		for detail in orderdetail:
			product_name = detail.product_name
			product_price = detail.product_price
			ProductQty = detail.ProductQty
			total_price = 0.00
			if UserDetail(request).is_vendor():
				total_price = ProductQty * product_price
			else:
				commission = 0
				commission_detail = Commission.objects.filter(user_id=user_id)
				if commission_detail:
					commission = commission_detail[0].commission

				productprice = ProductQty * product_price
				total_price = productprice + productprice * commission / 100

			image = "https://app.fashioncircle.de/media/default_image.gif"

			product_id = detail.product_id
			image_detail = Images.objects.filter(product_id=product_id)
			if image_detail:
				image_name = image_detail[0].image_name
				image_id = image_detail[0].id
				token = image_detail[0].token
				if token:
					image = "https://"+ request.META['HTTP_HOST'] + "/images/view/" + str(token) + "/" + str(image_id)
			all_orders.append({'product_name': product_name, 'total_price': total_price, 'ProductQty': ProductQty, 'image': image})
		order_list.append({order_id: all_orders, 'OrderId': OrderId, 'order_date': order_date})

	paginator=Paginator(list(order_list),6)
	page=request.GET.get("page")
	try:
		order_list=paginator.page(page)
	except PageNotAnInteger:
		order_list=paginator.page(1)
	except EmptyPage:
		order_list=paginator.page(paginator.num_pages)

	date_obj = today.strftime("%B")

	vendor_name = "Orders of Month : " + str(date_obj)
	return render(request, "dashboard.html", {'page_name': 'Orders', 'vendor_name': vendor_name, 'products_type': 'orders_products', 'total_amount': total_amount, 'order_list': order_list})

def delete_product(request):
	response = {}
	try:
		product_id = request.POST['product_id']
	except:
		response['error'] = "Please provide Product id to delete."

	products_list = []
	product_vendor = Products.objects.get(id=product_id)
	user_id = product_vendor.user_id
	title = product_vendor.title
	vendor_detail = Vendor.objects.get(user_id=user_id)
	vendor = vendor_detail.vendor

	all_records = ProductDetail.objects.filter(product_id=product_id)
	for record in all_records:
		merchant_id = record.merchant_id
		PlatformProductId = record.PlatformProductId
		platform = record.platform

		merchant_detail = AccountDetail.objects.get(id=merchant_id)
		shopify_domain = merchant_detail.shopify_domain
		token = merchant_detail.token
		username = merchant_detail.username
		email = merchant_detail.email

		products_list.append({'shopify_domain': shopify_domain, 'PlatformProductId': PlatformProductId, 'token': token, 'platform': platform})
		# send mail
		Vars = {"first_name": username, "label_name": vendor, "product_name": title}
		template_id = "138018"
		send_template(email, Vars, template_id)

	second_lis=[]

	prod_detai=Products.objects.filter(id=product_id)
	if prod_detai:
		PlatforProduId=prod_detai[0].PlatformProductId
		userr_id=prod_detai[0].user_id
		acc=Account.objects.filter(id=userr_id)
		if acc:
			website=acc[0].website
			acc_token=acc[0].token
			acc_platform=acc[0].platform
			second_lis.append({'shopify_domain':website,'PlatformProductId':PlatforProduId,'token':acc_token,'platform':acc_platform})

	Products.objects.filter(id=product_id).delete()


	data = {'products': products_list}
	link = settings.SHOPIFY_DOMAIN + "/fashioncircle/webhooks/getShopDataOnDelete.php"
	resp = requests.post(link, data=json.dumps(products_list), headers={'content-type': 'application/json'})



	vendor_mvp_link = 'https://shopify.fashioncircle.de/vendorApp/webhooks/VendorProdDeleteFromMVP.php'
	respon = requests.post(vendor_mvp_link, data=json.dumps(second_lis), headers={'content-type': 'application/json'})

	response['success'] = str("Successfully Deleted.")

	return HttpResponse(json.dumps(response))

def forgot_password(request):
	posted_data = {}
	if request.method == "POST":
		posted_data = request.POST
		form = ForgotPasswordForm(request.POST, request=request)
		if form.is_valid():
			emailid = request.POST['emailid']
			detail = Account.objects.get(emailid=emailid)
			first_name = detail.first_name
			url = "https://"+request.META['HTTP_HOST']+"/reset_password?emailid="+emailid
			Vars = {"first_name": first_name, "URL_reset": url}
			template_id = "136352"
			send_template(emailid, Vars, template_id)
			messages.add_message(request, messages.SUCCESS, 'Thank you. Please check your email to change your password.')
	else:
		form = ForgotPasswordForm(request=request)
	return render(request, "forgot_password.html", {'form': form, 'posted_data': posted_data})

def reset_password(request):
	emailid = request.GET['emailid']
	if request.method == "POST":
		password = request.POST['password']
		encrypted_password = handler.encrypt(password)
		Account.objects.filter(emailid=emailid).update(password=encrypted_password)
		messages.add_message(request, messages.SUCCESS, 'Congratulations, your password has been reset. Please Sign In your account here!')
		return redirect('/')
	return render(request, "reset_password.html", {'emailid': emailid})
