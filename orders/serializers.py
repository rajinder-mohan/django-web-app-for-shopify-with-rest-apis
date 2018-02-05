from rest_framework import serializers
from .models import Orders, OrderProducts
from images.models import Images
from shopify.models import Products, Commission
import json
from shopify.utils.userdetails import UserDetail

class OrdersSerializer(serializers.ModelSerializer):

	# image = serializers.SerializerMethodField('image_serializer')

	# title = serializers.SerializerMethodField('product_detail')

	#calculated_price = serializers.SerializerMethodField('calculate_price')

	# def image_serializer(self, obj):
	# 	images_list = []

	# 	url="/images/view/"

	# 	image_detail = Images.objects.filter(product_id=obj.product_id)
	# 	if image_detail:
	# 		image_name = image_detail[0].image_name
	# 		image_id = image_detail[0].id
	# 		token = image_detail[0].token
	# 		if token:
	# 			image_path = "https://"+self.context['request'].META['HTTP_HOST'] + url + str(token) + "/" + str(image_id)
	# 	else:
	# 		image_path = "https://app.fashioncircle.de/media/default_image.gif"
	# 	return image_path

	# def product_detail(self, obj):
	# 	detail = Products.objects.get(id=obj.product_id)
	# 	title = detail.title
	# 	return title

	# def calculate_price(self, obj):
	# 	products = json.loads(obj.products)
	# 	calculated = 0
	# 	for product in products:
	# 		try:
	# 			detail = Products.objects.get(id=product['product_id'])
	# 			user_id = detail.user_id
	# 			commission = 0
	# 			commission_detail = Commission.objects.filter(user_id=user_id)
	# 			if commission_detail:
	# 				commission = commission_detail[0].commission
	# 			dropshipping_price = detail.dropshipping_price
	# 			total_price = product['ProductQty'] * dropshipping_price

	# 			total_price = total_price + total_price * commission / 100
	# 			calculated += total_price
	# 		except:
	# 			pass
	# 	return calculated


	class Meta:
		model = Orders
		fields = '__all__'


class OrderProductsSerializer(serializers.ModelSerializer):

	total_price = serializers.SerializerMethodField('calculate_price')

	def calculate_price(self, obj):
		if self.context['user_type'] == "admin":
			commission = 0
			commission_detail = Commission.objects.filter(user_id=obj.user_id)
			if commission_detail:
				commission = commission_detail[0].commission

			productprice = obj.ProductQty * obj.product_price
			productprice = productprice + productprice * commission / 100
			return productprice
		else:
			productprice = obj.ProductQty * obj.product_price
			return productprice


	class Meta:
		model = OrderProducts
		fields = '__all__'
