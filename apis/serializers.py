from rest_framework import serializers
from shopify.models import Account, Categories, Products, AccountType, Vendor, Commission
from passlib.hash import django_pbkdf2_sha256 as handler
from images.models import Images
from django.conf import settings
from merchants.models import ProductDetail, AccountDetail, DenyAccess


class AccountSerializer(serializers.ModelSerializer):

	class Meta:
		model = Account
		fields = ('id', 'first_name', 'last_name', 'emailid')
		extra_kwargs = {'password': {'write_only': True}, 'activation_key': {'write_only': True}}
		#fields = '__all__'
		#exclude = ('status', 'activation_key', 'password')

		def create(self, validated_data):
			record = Account(first_name=validated_data['first_name'], last_name=validated_data['last_name'], emailid=validated_data['emailid'])
			encrypted_password = handler.encrypt(validated_data['password'])
			record.set_password(encrypted_password)
			record.save()
			return record


class AccountTypeSerializer(serializers.ModelSerializer):
	accounts = AccountSerializer(source='account_set', many=True)
	class Meta:
		model = AccountType
		fields = '__all__'


class ProductsSerializer(serializers.ModelSerializer):

	user_id = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(),source='user.id')

	vendor_mvp_platform_id=serializers.SerializerMethodField('vendor_or_mvp')

	vendor = serializers.SerializerMethodField('vendor_detail')

	is_app_uninstall=serializers.SerializerMethodField('check_is_app')

	images = serializers.SerializerMethodField('image_serializer')

	platformProductId = serializers.SerializerMethodField('platform_serializer')

	commission = serializers.SerializerMethodField('vendor_commission')

	vendor_access = serializers.SerializerMethodField('vendoraccess')

	def vendor_or_mvp(self,obj):
		proo_id=Products.objects.get(id=obj.id)
		PlatformProductId=proo_id.PlatformProductId

		return PlatformProductId



	def check_is_app(self,obj):
		is_uninstall=Account.objects.get(id=obj.user_id)
		is_app=is_uninstall.is_app_uninstall

		return is_app

	def image_serializer(self, obj):
		images_list = []

		url="/media/products/"
		
		image_detail = Images.objects.filter(product_id=obj.id)
		
		for image in image_detail:
			image_name = image.image_name
			split_image=image_name.split('_')
			folder=split_image[0]
			image_id = image.id
			token = image.token
			crop_image=str(400)+'_'+image_name
			original_size = "https://"+self.context['request'].META['HTTP_HOST'] + url + folder + "/" + image_name
			images_list.append(original_size)
		if not images_list:
			default_image = "https://app.fashioncircle.de/media/default_image.gif"
			images_list.append(default_image)
		images_list=images_list[::-1]
		return images_list

	def vendor_detail(self, obj):
		vendordetail = Vendor.objects.get(user_id=obj.user_id)
		vendor = vendordetail.vendor
		return vendor

	def platform_serializer(self, obj):
		if 'domain' in self.context['request'].GET:
			domain = self.context['request'].GET['domain']

			domain_detail = AccountDetail.objects.filter(main_domain=domain)
			if domain_detail:
				merchant_id = domain_detail[0].id
				product_detail = ProductDetail.objects.filter(merchant_id=merchant_id, product_id=obj.id)
				if product_detail:
					productid = product_detail[0].PlatformProductId
					return productid
		
	def vendor_commission(self, obj):
		commission = 0
		existing = Commission.objects.filter(user_id=obj.user_id)
		if existing:
			commission = existing[0].commission
		return commission

	def vendoraccess(self, obj):
		if 'domain' in self.context['request'].GET:
			domain = self.context['request'].GET['domain']

			domain_detail = AccountDetail.objects.filter(main_domain=domain)
			if domain_detail:
				merchant_id = domain_detail[0].id
				access_denied = DenyAccess.objects.filter(vendor_id=obj.user_id, merchant_id=merchant_id)
				if access_denied:
					return "no"
				else:
					return "yes"


	class Meta:
		model = Products
		fields=('id','user_id','vendor_mvp_platform_id','vendor','is_app_uninstall','images','platformProductId','commission','vendor_access','description','selling_price','dropshipping_price','wholesale_price','sku','quantity','title','barcode', 'weight', 'weight_unit')


class CategoriesSerializer(serializers.ModelSerializer):
	products = ProductsSerializer(source='products_set', many=True)

	class Meta:
		model = Categories
		fields = '__all__'


class VendorSerializer(serializers.ModelSerializer):
	
	vend = serializers.SerializerMethodField('vendor_access')

	def vendor_access(self, obj):
		if 'domain' in self.context['request'].GET:
			domain = self.context['request'].GET['domain']
			
			domain_detail = AccountDetail.objects.filter(main_domain=domain)
			if domain_detail:
				merchant_id = domain_detail[0].id
				access_denied = DenyAccess.objects.filter(vendor_id=obj.user_id, merchant_id=merchant_id)
				if access_denied:
					return 'Access Denied'
				else:
					vendor_detail = Vendor.objects.get(user_id=obj.user_id)
					name_vendor = vendor_detail.vendor
					return name_vendor
	



	is_app_uninstall=serializers.SerializerMethodField('check_status')

	def check_status(self,obj):
		is_uninstall=Account.objects.get(id=obj.user_id)
		is_app=is_uninstall.is_app_uninstall

		return is_app


	class Meta:
		model = Vendor
		fields=('user_id','vend','is_app_uninstall')
