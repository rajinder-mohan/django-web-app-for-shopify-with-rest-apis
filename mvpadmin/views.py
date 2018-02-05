from django.shortcuts import render,redirect
from shopify.utils.userdetails import UserDetail
from django.http import HttpResponse
from shopify.models import Account, Products, Vendor, Commission
from django.db.models import Q
from django.template.loader import render_to_string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.conf import settings
import json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from merchants.models import ProductDetail, AccountDetail, DenyAccess

import os
from shopify.views import send_template
from orders.models import Orders, OrderProducts
from orders.serializers import OrderProductsSerializer
from datetime import date
from images.models import Images


def index(request):

	user=UserDetail(request).getLoginUser()	

	if not user:
		return redirect("/")

	if UserDetail(request).is_vendor():
		if request.path == '/mvpadmin/':
			return redirect('/dashboard')

	products_list = []
	merchants_list = []

	try:
		raw_query = "select * from merchants_productdetail where vendor_id={user} group by product_id".format(user=user['id'])
		products_count = ProductDetail.objects.raw(raw_query)
		for p in products_count:
			products_list.append(p.id)
	except:
		pass

	try:
		query = "select * from merchants_productdetail where vendor_id={user} group by merchant_id".format(user=user['id'])
		merchants_count = ProductDetail.objects.raw(query)

		for m in merchants_count:
			merchant_id = m.merchant_id
			detail = AccountDetail.objects.get(id=merchant_id)
			merchants_list.append({'username': detail.username, 'email': detail.email, 'platform': detail.platform, 'shopify_domain': detail.shopify_domain, 'main_domain': detail.main_domain, 'merchant_id': merchant_id})
	except:
		pass

	products_length = 0
	if products_list:
		products_length = len(products_list)
		
	total_merchants = AccountDetail.objects.all().count()

	today = date.today()

	total_orders = 0

	user_id = user['id']

	if UserDetail(request).is_vendor():
		total_orders = OrderProducts.objects.filter(user_id=user_id, date__month=today.month, date__year=today.year).values_list('order_id').distinct().count()
	else:
		total_orders = Orders.objects.filter(date__month=today.month, date__year=today.year).count()

	total_vendors = Account.objects.filter(account_id=3).count()
	return render(request,"index.html", {'total_vendors': total_vendors, 'page_name': 'Dashboard', 'products_length': products_length, 'merchants_list': merchants_list, 'total_merchants': total_merchants, 'total_orders': total_orders})

def vendors(request):

	user=UserDetail(request).getLoginUser()	
	if not user:
		return redirect("/")
	else:
		account_type = user['account_type']['admin']

		if account_type == False:
			return render(request, "not_allowed.html", {})

	user_id = request.GET['user_id']
	
	products_list = []
	sql='SELECT dp.*, di.* FROM shopify_products AS dp LEFT JOIN (SELECT t1.* FROM images_images t1 WHERE t1.updated_date =(SELECT MAX(t2.updated_date) FROM images_images t2 WHERE t2.product_id = t1.product_id) ) di ON dp.id = di.product_id  where dp.user_id={0} ORDER BY di.product_id'.format(user_id)
	products = Products.objects.raw(sql)
	paginator=Paginator(list(products),6)
	page=request.GET.get("page")
	try:
		products=paginator.page(page)
	except PageNotAnInteger:
		products=paginator.page(1)
	except EmptyPage:
		products=paginator.page(paginator.num_pages)

	login_user = "vendor"
	page_name = "Dashboard"

	if UserDetail(request).is_vendor():
		login_user = "vendor"
	else:
		login_user = "admin"
		page_name = "vendors_list"

	vendor_detail = Vendor.objects.get(user_id=user_id)
	vendor_name = vendor_detail.vendor

	page_name = "vendors_list"

	return render(request, "dashboard.html", {'products_list': products, 'login_user': login_user, 'page': page, 'vendor_name': vendor_name, 'page_name': page_name, 'user_id': user_id})

def vendors_list(request):

	user=UserDetail(request).getLoginUser()	
	if not user:
		#messages.add_message(request, messages.INFO, 'Please login firstly !!')
		return redirect("/")
	else:
		account_type = user['account_type']['admin']

		if account_type == False:
			return render(request, "not_allowed.html", {})
	users = Account.objects.filter(account_id=3).order_by('id').reverse()

	users_list = []

	for user in users:
		fname = user.first_name
		lname = user.last_name
		user_name = fname + " " + lname
		user_name = user_name.title()
		status = user.status
		user_id = user.id

		#commission
		commission = 0
		com = Commission.objects.filter(user_id=user_id)
		if com:
			commission = com[0].commission
		try:
			vendor_detail = Vendor.objects.get(user_id=user_id)
			vendor_name = vendor_detail.vendor
			users_list.append({'user_name': vendor_name, 'status': status, 'user_id': user_id, 'commission': commission})
		except:
			pass

	paginator=Paginator(list(users_list),10)
	page=request.GET.get("page")
	try:
		users_list=paginator.page(page)
	except PageNotAnInteger:
		users_list=paginator.page(1)
	except EmptyPage:
		users_list=paginator.page(paginator.num_pages)

	return render(request, "vendors_list.html", {'page_name': 'vendors_list', 'users_list': users_list})

def merchants_list(request):
	user=UserDetail(request).getLoginUser()

	merchants_accounts = AccountDetail.objects.all().order_by('id').reverse()
	paginator=Paginator(list(merchants_accounts),10)
	page=request.GET.get("page")
	try:
		merchants_accounts=paginator.page(page)
	except PageNotAnInteger:
		merchants_accounts=paginator.page(1)
	except EmptyPage:
		merchants_accounts=paginator.page(paginator.num_pages)

	if not user:
		#messages.add_message(request, messages.INFO, 'Please login firstly !!')
		return redirect("/")
	else:
		account_type = user['account_type']['admin']

		if account_type == False:
			vendor_id = user['id']
			deniedusers = []
			denied_users = DenyAccess.objects.filter(vendor_id=vendor_id).order_by('id').reverse()
			for denied_user in denied_users:
				deniedusers.append(denied_user.merchant_id)
			return render(request, "show_merchants.html", {'page_name': 'merchants_list', 'merchants_accounts': merchants_accounts, 'deniedusers': deniedusers})
			#return render(request, "not_allowed.html", {})

	return render(request, "merchants_list.html", {'page_name': 'merchants_list', 'merchants_accounts': merchants_accounts})

def user_status(request):
	user_id = request.POST['user_id']
	status = request.POST['status']

	user_detail = Account.objects.get(id=user_id)
	first_name = user_detail.first_name
	emailid = user_detail.emailid
	existing_status = user_detail.status

	vendor_detail = Vendor.objects.get(user_id=user_id)
	vendor = vendor_detail.vendor

	if int(existing_status) == int(status):
		response = {'already_updated': 'Label Account is already updated.'}
		return HttpResponse(json.dumps(response))

	try:
		Account.objects.filter(id=user_id).update(status=status)
		
		Vars = {"first_name": first_name, "label_name": vendor}

		if int(status) == 1:
			template_id = "128328"
			send_template(emailid, Vars, template_id)
		else:
			template_id = "136406"
			send_template(emailid, Vars, template_id)
	except:
		response = {'error': 'Sorry, Error while Updating.'}
		return HttpResponse(json.dumps(response))
	response = {'success': 'Successfully Updated.'}
	return HttpResponse(json.dumps(response))

def merchant_status(request):
	id = request.POST['id']
	status = request.POST['status']

	user_detail = AccountDetail.objects.get(id=id)
	username = user_detail.username
	existing_status = user_detail.status
	email = user_detail.email
	shopify_domain = user_detail.shopify_domain

	if int(existing_status) == int(status):
		response = {'already_updated': 'Merchant Account is already updated.'}
		return HttpResponse(json.dumps(response))

	try:
		AccountDetail.objects.filter(id=id).update(status=status)

		Vars = {"first_name": username, "merchant_name": shopify_domain}

		if int(status) == 1:
			template_id = "136349"
			send_template(email, Vars, template_id)
		else:
			template_id = "138010"
			send_template(email, Vars, template_id)
	except:
		response = {'error': 'Sorry, Error while Updating.'}
		return HttpResponse(json.dumps(response))
	response = {'success': 'Successfully Updated.'}
	return HttpResponse(json.dumps(response))

def denyaccess(request):
	merchant_id = request.POST['merchant_id']
	status = request.POST['status']

	user=UserDetail(request).getLoginUser()
	vendor_id = user['id']

	response = {}

	existing_access = DenyAccess.objects.filter(merchant_id=merchant_id, vendor_id=vendor_id)

	if status == "yes":
		if not existing_access:
			try:
				detail = DenyAccess(merchant_id=merchant_id, vendor_id=vendor_id)
				detail.save()
				response = {"success": "Merchant is not allowed to access your products."}
			except:
				response = {"error": "Error while updating!"}
		else:
			response = {"already_updated": "Merchant is not allowed to access your products."}
	else:
		if existing_access:
			DenyAccess.objects.filter(merchant_id=merchant_id, vendor_id=vendor_id).delete()
			response = {"success": "Merchant is allowed to access your products."}
	return HttpResponse(json.dumps(response))

def labels_orders(request):
	user=UserDetail(request).getLoginUser()	
	if not user:
		return redirect("/")
	else:
		account_type = user['account_type']['admin']

		if account_type == False:
			return render(request, "not_allowed.html", {})

	users = Account.objects.filter(account_id=3).order_by('id').reverse()

	users_list = []

	today = date.today()

	for user in users:
		user_id = user.id
		try:
			vendor_detail = Vendor.objects.get(user_id=user_id)
			vendor_name = vendor_detail.vendor

			orders_count = OrderProducts.objects.filter(user_id=user_id, date__month=today.month, date__year=today.year).values_list('order_id').distinct().count()

			orders = OrderProducts.objects.filter(user_id=user_id, date__month=today.month, date__year=today.year)

			serializer = OrderProductsSerializer(orders, many=True, context={'user_id': user_id, 'user_type': 'admin'})

			total_amount = sum([order['total_price'] for order in serializer.data])

			if orders_count != 0:
				users_list.append({'label': vendor_name, 'user_id': user_id, 'orders_count': orders_count, 'total_amount': total_amount})
		except:
			pass

	paginator=Paginator(list(users_list),10)
	page=request.GET.get("page")
	try:
		users_list=paginator.page(page)
	except PageNotAnInteger:
		users_list=paginator.page(1)
	except EmptyPage:
		users_list=paginator.page(paginator.num_pages)

	return render(request, "labels_orders.html", {'page_name': 'labels_orders', 'users_list': users_list})

def label_order(request):
	user=UserDetail(request).getLoginUser()	
	if not user:
		return redirect("/")
	else:
		account_type = user['account_type']['admin']

		if account_type == False:
			return render(request, "not_allowed.html", {})

	try:
		label = request.GET['label']
	except:
		response = {"Error": "Please enter label."}
		return HttpResponse(json.dumps(response))

	today = date.today()
	date_obj = today.strftime("%B")
	vendor_name = "Orders of Month : " + str(date_obj)

	label_detail = Vendor.objects.get(vendor=label)
	user_id = label_detail.user_id

	existing_label = label
	
	filtered_orders = OrderProducts.objects.filter(user_id=user_id, date__month=today.month, date__year=today.year).values_list('order_id').distinct()

	order_list = []

	for order in filtered_orders:
		order_id = order[0]
		existing_order = Orders.objects.get(id=order_id)
		OrderId = existing_order.OrderId
		merchant_id = existing_order.merchant_id
		platform = existing_order.platform
		order_date = existing_order.date.strftime("%d %B, %Y")

		# merchant detail
		merchant_detail = AccountDetail.objects.get(id=merchant_id)
		shopify_domain = merchant_detail.shopify_domain

		orderdetail = OrderProducts.objects.filter(order_id=order_id, user_id=user_id)

		all_orders = []

		for detail in orderdetail:
			product_name = detail.product_name
			product_price = detail.product_price
			ProductQty = detail.ProductQty

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
		order_list.append({order_id: all_orders, 'OrderId': OrderId, 'platform': platform, 'shopify_domain': shopify_domain, 'order_date': order_date})

	paginator=Paginator(list(order_list),6)
	page=request.GET.get("page")
	try:
		order_list=paginator.page(page)
	except PageNotAnInteger:
		order_list=paginator.page(1)
	except EmptyPage:
		order_list=paginator.page(paginator.num_pages)

	orders = OrderProducts.objects.filter(user_id=user_id, date__month=today.month, date__year=today.year)
	serializer = OrderProductsSerializer(orders, many=True, context={'user_type': 'admin'})
	total_amount = sum([order['total_price'] for order in serializer.data])

	return render(request, "dashboard.html", {'page_name': 'Label Orders', 'vendor_name': vendor_name, 'products_type': 'orders_products', 'total_amount': total_amount, 'order_list': order_list, 'existing_label': existing_label})

def add_commision(request):
	response = {}
	if request.method == "POST":
		ids_list = request.POST.getlist("labels_id[]")
		vals_list = request.POST.getlist("labels_val[]")

		for i in range(len(ids_list)):
			user_id = ids_list[i]
			commission = vals_list[i]
			existing = Commission.objects.filter(user_id=user_id)
			if existing:
				Commission.objects.filter(user_id=user_id).update(commission=commission)
			else:
				add = Commission(user_id=user_id, commission=commission)
				add.save()

		response = {"Success": "Saved Successfully."}
	return HttpResponse(response)