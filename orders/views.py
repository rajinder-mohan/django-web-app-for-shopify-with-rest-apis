from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
import json
from merchants.models import AccountDetail, ProductDetail, AccessToken
from .models import Orders, OrderProducts
from shopify.models import Vendor, Products, Account, Commission, ApiAuth
from shopify.views import send_template
import requests
import datetime


class PlaceOrder(APIView):
	def post(self, request):

		response = {}
		print(request.META)

		if 'HTTP_ACCESS_TOKEN' not in request.META or not request.META['HTTP_ACCESS_TOKEN']:
			print("token not found")
			response = {"error": "You don't have access to send order email to vendor."}
			return Response(response)

		access_token = request.META['HTTP_ACCESS_TOKEN']
		verify_shop = request.META['HTTP_SHOP']

		existing_token = ApiAuth.objects.filter(platform_key=access_token,platform_name=verify_shop)
		if not existing_token:
			response = {"error": "You don't have access to send order email to vendor."}
			return Response(response)

		OrderId = request.POST['OrderId']

		domain = request.POST['domain']

		OrderUrl = request.POST['OrderUrl']

		financial_status = request.POST['financial_status']

		platform = request.POST['platform']

		products = request.POST['products']

		paymentMethod = request.POST['paymentMethod']


		customer_email=request.POST['customer_email']

		customer_first_name=request.POST['first_name']

		customer_last_name=request.POST['last_name']

		customer_address=request.POST['customer_address']

		customer_city=request.POST['city']
		customer_province=request.POST['province']

		customer_phone=request.POST['phone']
		customer_zipcode=request.POST['zipcode']
		customer_country=request.POST['country']
		paid_by_merchant = request.POST['paid_by_merchant']



		domain_detail = AccountDetail.objects.get(shop_domain=domain)
		merchant_id = domain_detail.id
		merchant_name = domain_detail.username

		existing_order = Orders.objects.filter(OrderId=OrderId)

		if not existing_order:
			order_obj = Orders(merchant_id=merchant_id, platform=platform, OrderId=OrderId, paymentMethod=paymentMethod, financial_status=financial_status, OrderUrl=OrderUrl,customer_email=customer_email,customer_first_name=customer_first_name,customer_last_name=customer_last_name,customer_address=customer_address,customer_city=customer_city,customer_province=customer_province,customer_phone=customer_phone,customer_zipcode=customer_zipcode,customer_country=customer_country,updated_status='',vendorPlateformOrderId='',paid_by_merchant=paid_by_merchant,vendor_order_number='')
			order_obj.save()
			order_id = order_obj.id
			order_date = order_obj.date
			order_time = order_obj.time

			calculated = 0

			for value in products.values():

				try:
					product_detail = ProductDetail.objects.get(PlatformProductId=int(value["id"]))
					vendor_products = []
					user_id = product_detail.vendor_id
					vendor_email = product_detail.vendor.emailid
					first_name = product_detail.vendor.first_name
					shopify_domain = product_detail.vendor.website
					token = product_detail.vendor.token

					commission = 0

					commission_detail = Commission.objects.filter(user_id=user_id)
					if commission_detail:
						commission = commission_detail[0].commission

					ProductQty = value['ProductQty']

					vendor_lis = []
					merchant_lis = []

					try:
						product_id = product_detail.product_id
						merchant_id = product_detail.merchant_id

						productdetail = Products.objects.get(id=product_id)
						product_name = productdetail.title.encode('utf-8')
						existing_quantity = productdetail.quantity

						vendor_platformid = productdetail.PlatformProductId

						new_quantity = int(existing_quantity) - int(ProductQty)
						productdetail.quantity = new_quantity
						productdetail.save()

						platform = productdetail.platform

						dropshipping_price = productdetail.dropshipping_price
						productprice = ProductQty * dropshipping_price

						calculated_commission = productprice + productprice * commission / 100
						calculated += calculated_commission

						product_obj = OrderProducts(order_id=order_id, product_id=product_id, product_name=product_name, product_price=dropshipping_price, user_id=user_id, ShopifyProductId=ShopifyProductId, ProductQty=ProductQty, date=order_date, time=order_time)
						product_obj.save()
						vendor_products.append({"product_name": product_name, "product_quantity": ProductQty, 'product_price': productprice})

						vendor_lis.append({'ProductQuantity':new_quantity,'platform':platform,'PlatformProductId':vendor_platformid,'shopify_domain':shopify_domain,'token':token})
						vendor_link = "https://shopify.fashioncircle.de/vendorApp/webhooks/update_product_inventory.php"
						# resp = requests.post(vendor_link, data=json.dumps(vendor_lis), headers={'content-type': 'application/json'})


						all_merchants = ProductDetail.objects.filter(product_id=product_id)
						for one_product in all_merchants:
							merchant_id = one_product.merchant_id

							merchant_detail = AccountDetail.objects.get(id=merchant_id)
							merch_platform = merchant_detail.platform
							merchant_domain = merchant_detail.shopify_domain
							merch_productid = one_product.PlatformProductId
							merchant_token = merchant_detail.token
							merchant_lis.append({'platform':merch_platform,'PlatformProductId':merch_productid,'ProductQuantity':new_quantity,'shopify_domain':merchant_domain,'token':merchant_token})
						merchant_link = "https://shopify.fashioncircle.de/fashioncircle/webhooks/update_product_inventory.php"
						# resp = requests.post(merchant_link, data=json.dumps(merchant_lis), headers={'content-type': 'application/json'})
					except Exception as e:
						print(e)
						pass
					template_id = "139248"
					Vars = {"first_name": first_name, "merchant_name": merchant_name, "mj-invoice-item": vendor_products, "order_price": calculated}
					send_template(vendor_email, Vars, template_id)
				except:
					pass
			# update product
			Orders.objects.filter(id=order_id).update(total_amount=calculated)
		else:
			pass

		response['success'] = "Successfully placed order."
		return Response(response)


class OrderPaid(APIView):

	def post(self, request, *args, **kwargs):


		response = {}

		if 'HTTP_ACCESS_TOKEN' not in request.META or not request.META['HTTP_ACCESS_TOKEN']:
			response = {"error": "You don't have access to send order email to vendor."}
			return Response(response)

		access_token = request.META['HTTP_ACCESS_TOKEN']
		existing_token = AccessToken.objects.filter(access_token=access_token)
		if not existing_token:
			response = {"error": "You don't have access to send order email to vendor."}
			return Response(response)

		if 'vendorName' not in request.POST or not request.POST['vendorName']:
			response['error'] = "Please enter vendorName."
			return Response(response)

		if 'OrderID' not in request.POST or not request.POST['OrderID']:
			response['error'] = "Please enter OrderID."
			return Response(response)

		vendor = request.POST['vendorName']
		order_ids = request.POST['OrderID']




		try:
			vendor_detail = Vendor.objects.get(vendor=vendor)
		except:
			response['error'] = "Vendor does not exist."
			return Response(response)
		user_id = vendor_detail.user_id

		user_detail = Account.objects.get(id=user_id)
		user_name = user_detail.first_name
		vendor_email = user_detail.emailid
		vendorShopDomain = user_detail.website

		orders = []

		commission = 0

		commission_detail = Commission.objects.filter(user_id=user_id)
		if commission_detail:
			commission = commission_detail[0].commission

		if ',' not in order_ids:
			orders.append(order_ids)
		else:
			orders = order_ids.split(",")

		calculated = 0

		calculated_commission = 0

		order_products = []
		order_list=[]
		final_product_list=[]
		final_order_list=[]

		merchant_name = ''

		for orderId in orders:
			today = datetime.date.today()
			updated_status = today.strftime("%d/%m/%Y")
			existing_record = Orders.objects.get(OrderId=orderId)
			check_status = existing_record.paid_by_merchant

			if check_status != 'paid':
				order_update = Orders.objects.filter(OrderId=orderId).update(paid_by_merchant='paid', updated_status=updated_status)
				order_detail = Orders.objects.get(OrderId=orderId)
				merchant_id = order_detail.merchant_id
				order_id = order_detail.id
				customer_email=order_detail.customer_email
				first_name=order_detail.customer_first_name
				last_name=order_detail.customer_last_name
				customer_address=order_detail.customer_address
				city=order_detail.customer_city
				province=order_detail.customer_province
				phone=order_detail.customer_phone
				zipcode=order_detail.customer_zipcode
				country=order_detail.customer_country
				order_list.append({'Order_Details':{'OrderId':orderId,'customer_email':customer_email,'first_name':first_name,'last_name':last_name,'customer_address':customer_address,'city':city,'province':province,'phone':phone,'zipcode':zipcode,'country':country,'commission':commission,'vendorShopDomain':vendorShopDomain}})

				merchant_detail = AccountDetail.objects.get(id=merchant_id)
				merchant_name = merchant_detail.username

				products = OrderProducts.objects.filter(order_id=order_id)

				for product in products:
					product_name = product.product_name
					product_price=product.product_price
					product_id=product.product_id
					try:
						product_object=Products.objects.filter(id=product_id)
						PlatformProductId=product_object[0].PlatformProductId
					except:
						PlatformProductId=''

					ProductQty = product.ProductQty
					product_price = product.product_price
					productprice = ProductQty * product_price
					product_commission = productprice * commission / 100
					price = productprice + product_commission
					calculated += price
					calculated_commission += product_commission

					final_product_list.append({'ProductName':product_name,'ProductPrice':product_price,'PlatformProductId':PlatformProductId,'ProductQty':ProductQty})

					order_products.append({"product_name": product_name, "product_quantity": ProductQty, 'product_price': productprice})

				order_list.append(final_product_list)
				final_order_list.append(order_list)
				order_list=[]
				final_product_list=[]

		template_id = "161720"

		Vars = {"first_name": user_name, "merchant_name": merchant_name, "mj-invoice-item": order_products, "total_price": calculated, "commission": calculated_commission}
		send_template(vendor_email, Vars, template_id)
		# response['success'] = "Mail sent successfully."
		vendor_link = "https://shopify.fashioncircle.de/vendorApp/webhooks/create_merchant_order.php"
		resp = requests.post(vendor_link, data=json.dumps(final_order_list), headers={'content-type': 'application/json'})
		return HttpResponse(json.dumps(final_order_list))


class FulfillmentStatus(APIView):

	def post(self, request, *args, **kwargs):

		if 'HTTP_API_KEY' not in self.request.META or not self.request.META['HTTP_API_KEY']:
			response = {"error":" You Dont Have Access To Api"}
			return Response(response)

		api_key = self.request.META['HTTP_API_KEY']
		if api_key != "pbkdf2_sha256$29000$p7lpJChcK4Lo$IHMul9j5lcPNJP4f/W1nXZknVi2N+GJIR1tZCo5C7uM=":

			response = {"error":" Wrong Api Key"}
			return Response(response)



		VendorPlatformOrderID=request.POST.get('OrderId')
		tracking_company=request.POST.get('tracking_company')
		if not tracking_company:
			tracking_company=''
		vendor_domain=request.POST.get('Domain')
		tracking_number=request.POST.get('tracking_number')
		if not tracking_number:
			tracking_number=''
		tracking_url=request.POST.get('tracking_url')
		if not tracking_url:
			tracking_url=''
		line_items=request.POST.get('line_items')
		final_lis=[]
		new_list=[]
		dicts={}

		line_items=json.loads(line_items)








		# hit the webhook first
		details=Orders.objects.filter(vendorPlateformOrderId=VendorPlatformOrderID)
		order_id=details[0].id
		merchantOrderId=details[0].OrderId
		merchant_id=details[0].merchant_id
		tracking_company=tracking_company
		tracking_url=tracking_url
		tracking_number=tracking_number

		acc_obj=AccountDetail.objects.filter(id=merchant_id)
		if acc_obj:
			token=acc_obj[0].token
			shopify_domain=acc_obj[0].shopify_domain


			for items in line_items:
				product_obj=Products.objects.get(PlatformProductId=items['product_id'])
				product_detail_obj=ProductDetail.objects.get(product_id=product_obj.id)
				merchant_platform_id=product_detail_obj.PlatformProductId
				order_pro=OrderProducts.objects.get(product_id=product_obj.id,order_id=order_id)
				dicts={'product_id':merchant_platform_id,'quantity':items['quantity'],'fulfillment_status':items['fulfillment_status']}
				new_list.append(dicts)




			final_lis.append({'line_items':new_list,'tracking_company':tracking_company,'tracking_url':tracking_url,'tracking_number':tracking_number,'merchantOrderId':str(merchantOrderId),'token':str(token),'shopify_domain':str(shopify_domain)})

			vendor_link = "https://shopify.fashioncircle.de/fashioncircle/webhooks/update_order_fulfill_status.php"
			resp = requests.post(vendor_link, data=json.dumps(final_lis), headers={'content-type': 'application/json'})



		else:
			response={'error':'No mercahnt with this PLatform ID'}
			return Response(response)






		backend_product_id=[]
		order_obj=Orders.objects.get(vendorPlateformOrderId=VendorPlatformOrderID)
		if order_obj:

			order_id=order_obj.id

			for items in line_items:

				product_obj=Products.objects.get(PlatformProductId=items['product_id'])
				order_pro=OrderProducts.objects.get(order_id=order_id,product_id=product_obj.id)
				fulfillment_status=items['fulfillment_status']
				fulfillment_status=str(fulfillment_status)

				if fulfillment_status=='fulfilled':

					xx=OrderProducts.objects.filter(order_id=order_id,product_id=product_obj.id).update(fulfillment_status='fulfilled',fulfillment_quantity=items['quantity'])
				if fulfillment_status=='partial':

					backend_fulfillment_quantity=order_pro.fulfillment_quantity
					new_ful_quan=int(backend_fulfillment_quantity)+int(items['quantity'])
					OrderProducts.objects.filter(order_id=order_id,product_id=product_obj.id).update(fulfillment_status='partial',fulfillment_quantity=new_ful_quan)
			axx=Orders.objects.filter(vendorPlateformOrderId=VendorPlatformOrderID).update(tracking_company=tracking_company,tracking_url=tracking_url,tracking_number=tracking_number)



			# check_all_products_status
			all_pro_status=OrderProducts.objects.filter(order_id=order_id)

			final_status_of_order_lis=[]
			for all_pro in all_pro_status:

				if all_pro.fulfillment_status=='fulfilled':
					pass
				else:
					final_status_of_order_lis.append('random')
			if not final_status_of_order_lis:

				Orders.objects.filter(vendorPlateformOrderId=VendorPlatformOrderID).update(fulfillment_status='fulfilled')
			else:
				Orders.objects.filter(vendorPlateformOrderId=VendorPlatformOrderID).update(fulfillment_status='partial')

			response={"success": "Order Updated Successfully"}
			return Response(response)



		else:
			response={"error": "This Order Id Does Not Exists"}
			return Response(response)
