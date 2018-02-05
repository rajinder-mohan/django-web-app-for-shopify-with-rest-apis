from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from shopify.models import Account, Products, Categories, AccountType, Vendor
from .serializers import AccountSerializer, ProductsSerializer, CategoriesSerializer, AccountTypeSerializer, VendorSerializer
from images.models import Images
from rest_framework import generics

from rest_framework.decorators import api_view

from rest_framework.views import APIView

from django.http import JsonResponse
from merchants.models import AccountDetail, AccessToken
from django.http import HttpResponse
import json
import validators


#####################################
# 1.) Vendor List
class VendorList(APIView):

	def get(self, request):
		if 'HTTP_ACCESS_TOKEN' not in request.META or not request.META['HTTP_ACCESS_TOKEN']:
			response = {"error": "You don't havssssse access to view vendors."}
			return HttpResponse(json.dumps(response))

		access_token = request.META['HTTP_ACCESS_TOKEN']
		existing_token = AccessToken.objects.filter(access_token=access_token)
		if not existing_token:
			response = {"error": "You don't have asccess to view vendors."}
			return HttpResponse(json.dumps(response))

		if 'domain' not in request.GET or not request.GET['domain']:
			response = {"error": "Please enter domain."}
			return HttpResponse(json.dumps(response))

		domain = request.GET['domain']

		verify_domain = validators.domain(domain)
		if verify_domain is not True:
			response = {"error": "Please enter valid Domain."}
			return HttpResponse(json.dumps(response))

		vendors = Vendor.objects.all()
		serializer = VendorSerializer(vendors, many=True, context={'request': request})
		vendor = {'Vendors': serializer.data}
		return JsonResponse(vendor, safe=False)


class ProductsList(APIView):

	def get(self, request, user_id):
		if 'HTTP_ACCESS_TOKEN' not in request.META or not request.META['HTTP_ACCESS_TOKEN']:
			response = {"error": "You don't have access to view vendor products."}
			return HttpResponse(json.dumps(response))

		access_token = request.META['HTTP_ACCESS_TOKEN']
		existing_token = AccessToken.objects.filter(access_token=access_token)
		if not existing_token:
			response = {"error": "You don't have access to view vendor products."}
			return HttpResponse(json.dumps(response))

		existing_user = Account.objects.filter(id=user_id)
		if not existing_user:
			response = {"error": "Vendor does not Exist."}
			return HttpResponse(json.dumps(response))

		if 'domain' not in request.GET or not request.GET['domain']:
			response = {"error": "Please enter Domain."}
			return HttpResponse(json.dumps(response))

		products = Products.objects.filter(user_id=user_id)
		serializer = ProductsSerializer(products, many=True, context={'request': request})
		product = {'Products': serializer.data}
		return JsonResponse(product, safe=False)


class AllProductsList(APIView):

	def get(self, request):
		products = Products.objects.all()
		serializer = ProductsSerializer(products, many=True, context={'request': request})
		product = {'Products': serializer.data}
		return Response(product)



########################
## vendor products api
class VendorDetail(APIView):

	def get(self, request):
		vendor = Vendor.objects.all()
		serializer = VendorSerializer(vendor, many=True)

		all_vendors = []

		for user in serializer.data:

			vendors = {}

			vendors['vendor'] = user['vendor']

			all_products = []

			products = Products.objects.filter(user_id=user['user'])

			for d in products:

				products_list = {}
				product_id = d.id
				products_list['product_id'] = product_id

				title = d.title
				products_list['title'] = title

				description = d.description
				products_list['description'] = description

				selling_price = d.selling_price
				products_list['selling_price'] = selling_price

				dropshipping_price = d.dropshipping_price
				products_list['dropshipping_price'] = dropshipping_price

				wholesale_price = d.wholesale_price
				products_list['wholesale_price'] = wholesale_price

				is_tax = d.is_tax
				products_list['is_tax'] = is_tax

				sku = d.sku
				products_list['sku'] = sku

				barcode = d.barcode
				products_list['barcode'] = barcode

				category = d.category

				products_list['category_name'] = category.title

				url="/images/view/"

				images_list = []

				images = Images.objects.filter(product_id=product_id)
				for image in images:
					image_path = ''
					image_id = image.id
					token = image.token
					if token:
						image_path = "http://"+request.META['HTTP_HOST'] + url + str(token) + "/" + str(image_id)
						images_list.append(image_path)

				products_list['images'] = images_list
				all_products.append(products_list)
			vendors['products'] = all_products

			all_vendors.append(vendors)

		vendors_list = {'vendors': all_vendors}

		return Response(vendors_list)


####################################
# all products api
@api_view(['GET'])
def products_detail(request):
	products = Products.objects.all()
	serializer = ProductsSerializer(products, many=True)
	data = serializer.data

	all_products = []

	for d in data:
		products_list = {}
		product_id = d['id']
		products_list['product_id'] = product_id

		title = d['title']
		products_list['title'] = title

		description = d['description']
		products_list['description'] = description

		selling_price = d['selling_price']
		products_list['selling_price'] = selling_price

		wholesale_price = d['wholesale_price']
		products_list['wholesale_price'] = wholesale_price

		dropshipping_rice = d['dropshipping_rice']
		products_list['dropshipping_rice'] = dropshipping_rice

		is_tax = d['is_tax']
		products_list['is_tax'] = is_tax

		sku = d['sku']
		products_list['sku'] = sku

		user = d['user']

		vendor_detail = Vendor.objects.get(user_id=user)
		vendor = vendor_detail.vendor
		products_list['vendor'] = vendor

		barcode = d['barcode']
		products_list['barcode'] = barcode

		category = Categories.objects.get(id=d['category'])
		category_name = category.title
		products_list['category_name'] = category_name

		url="/images/view/"

		images_list = []

		images = Images.objects.filter(product_id=product_id)
		for image in images:
			image_path = ''
			image_id = image.id
			token = image.token
			if token:
				image_path = "http://"+request.META['HTTP_HOST'] + url + str(token) + "/" + str(image_id)
				images_list.append(image_path)

		products_list['images'] = images_list
		all_products.append(products_list)
	products = {'Products': all_products}

	return Response(products)


############# api functions
@api_view(['GET', 'POST'])
def accounts_detail(request):
	if request.method == "GET":
		records = Account.objects.all()
		serializer = AccountSerializer(records, many=True)
		return Response(serializer.data)

	elif request.method == "POST":
		serializer = AccountSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def categories_detail(request):
	if 'HTTP_ACCESS_TOKEN' not in request.META or not request.META['HTTP_ACCESS_TOKEN']:
		response = {"error": "You don't have access to view products."}
		return HttpResponse(json.dumps(response))

	access_token = request.META['HTTP_ACCESS_TOKEN']
	existing_token = AccessToken.objects.filter(access_token=access_token)
	if not existing_token:
		response = {"error": "You don't have access to view products."}
		return HttpResponse(json.dumps(response))

	if 'domain' not in request.GET or not request.GET['domain']:
		response = {'error': 'Please enter Domain.'}
		return HttpResponse(json.dumps(response))
	domain = request.GET['domain']
	existing_domain = AccountDetail.objects.filter(main_domain=domain)
	if existing_domain:
		status  = existing_domain[0].status
		if int(status) == 0:
			response = {'isEnabled': False}
			return HttpResponse(json.dumps(response))
	else:
		response = {}
		return HttpResponse(json.dumps(response))
	categories = Categories.objects.all()
	serializer = CategoriesSerializer(categories, many=True, context={'request': request})
	return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def account_types(request):
	types = AccountType.objects.all()
	serializer = AccountTypeSerializer(types, many=True)
	return Response(serializer.data)


########### api classes
class AccountList(APIView):
	def get(self, request):
		accounts = Account.objects.all()
		serializer = AccountSerializer(accounts, many=True)
		return Response(serializer.data)

	def post(self, request):
		serializer = AccountSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class AccountsDetail(APIView):

	def get(self, request, id):
		account = Account.objects.get(id=id)
		serializer = AccountSerializer(account)
		return Response(serializer.data)



################# api generics
class AccountGenericList(generics.ListCreateAPIView):
	queryset = Account.objects.all()
	serializer_class = AccountSerializer


class AccountUpdateGenericList(generics.RetrieveUpdateDestroyAPIView):
	queryset = Account.objects.all()
	serializer_class = AccountSerializer


class AccountListView(generics.ListAPIView):
	queryset = Account.objects.all()
	serializer_class = AccountSerializer


class AccountRetrieveView(generics.RetrieveAPIView):
	queryset = Account.objects.all()
	serializer_class = AccountSerializer


class getVendor(APIView):

	def post(self, request, *args, **kwargs):

		response = {}

		if 'HTTP_ACCESS_TOKEN' not in request.META or not request.META['HTTP_ACCESS_TOKEN']:
			response["error"] = "You don't have access to place order."
			return Response(response)

		access_token = request.META['HTTP_ACCESS_TOKEN']
		existing_token = AccessToken.objects.filter(access_token=access_token)
		if not existing_token:
			response["error"] = "You don't have access to place order."
			return Response(response)

		if 'vendorName' not in request.POST or not request.POST['vendorName']:
			response['error'] = "Please enter vendor name."
			return Response(response)

		vendor = request.POST['vendorName']

		existing = Vendor.objects.filter(vendor=vendor)
		if not existing:
			response['error'] = "Vendor Name does not exist."
			return HttpResponse(json.dumps(response))

		user_id = existing[0].user_id
		detail = Account.objects.get(id=user_id)
		paypal_emailid = detail.paypal_emailid
		response['emailid'] = paypal_emailid
		return HttpResponse(json.dumps(response))
