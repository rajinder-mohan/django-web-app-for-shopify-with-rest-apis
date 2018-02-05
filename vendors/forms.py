from django import forms
from django.utils.translation import gettext as _
from shopify.models import Account, Vendor
import json


class AddVendorForm(forms.Form):

	def __init__(self, *args, **kwargs):
		self.request = kwargs['request']
		self.request = kwargs.pop('request', None)
		super(AddVendorForm, self).__init__(*args, **kwargs)

	def clean(self):
		# ap=self.request.POST
		# print (dir(ap))
		print ('in formmmm')




		# if 'api_key' not in self.request.POST or not self.request.POST['api_key']:
		# 	raise forms.ValidationError(_("Please enter API."))

		if 'email' not in self.request.GET or not self.request.GET.get('email'):
			raise forms.ValidationError(_("Please enter Email."))

		if 'platform' not in self.request.GET or not self.request.GET.get('platform'):
			raise forms.ValidationError(_("Please enter Platform."))

		if 'name' not in self.request.GET or not self.request.GET.get('name'):
			raise forms.ValidationError(_("Please enter Name."))

		if 'website' not in self.request.GET or not self.request.GET.get('website'):
			raise forms.ValidationError(_("Please enter Website"))


		if 'country' not in self.request.GET or not self.request.GET.get('country'):
			raise forms.ValidationError(_("Please enter Country."))


		api_key=self.request.GET.get('api_key')
		emailid = self.request.GET.get('email')
		platform= self.request.GET.get('platform')
		vendor = self.request.GET.get('name')
		new_website = self.request.GET.get('website')
		print ('IN FORMS',vendor)

		if api_key != "pbkdf2_sha256$29000$p7lpJChcK4Lo$IHMul9j5lcPNJP4f/W1nXZknVi2N+GJIR1tZCo5C7uM=":
			raise forms.ValidationError(_("You don't have access to create vendor account."))

		existing_email = Account.objects.filter(emailid=emailid)
		if existing_email:
			raise forms.ValidationError(_("Vendor Email Already Exists"))

		existing_website = Account.objects.filter(website=new_website)
		if existing_website:
			raise forms.ValidationError(_("Vendor Website Already Exists"))

		existing_name = Vendor.objects.filter(vendor=vendor)
		print ('duhh')
		print ('\n\n')
		print ('\n'+str(existing_name))
		print (vendor)
		if existing_name:
			raise forms.ValidationError(_("Vendor Name Already Exists"))


		return self.cleaned_data


class AddProductForm(forms.Form):

	def __init__(self, *args, **kwargs):
		self.request = kwargs['request']
		self.request = kwargs.pop('request', None)
		super(AddProductForm, self).__init__(*args, **kwargs)

	def clean(self):
		if 'HTTP_API_KEY' not in self.request.META or not self.request.META['HTTP_API_KEY']:
			raise forms.ValidationError(_("You don't have to create vendor account."))

		api_key = self.request.META['HTTP_API_KEY']

		if api_key != "pbkdf2_sha256$29000$p7lpJChcK4Lo$IHMul9j5lcPNJP4f/W1nXZknVi2N+GJIR1tZCo5C7uM=":
			raise forms.ValidationError(_("You don't have access to create vendor account."))

		if 'product_id' not in self.request.POST or not self.request.POST['product_id']:
			raise forms.ValidationError(_("Please enter ProductId."))



		if 'title' not in self.request.POST or not self.request.POST['title']:
			raise forms.ValidationError(_("Please enter Title."))

		if 'category' not in self.request.POST or not self.request.POST['category']:
			raise forms.ValidationError(_("Please enter Category."))

		if 'platform' not in self.request.POST or not self.request.POST['platform']:
			raise forms.ValidationError(_("Please enter Platform."))

		if 'myshopify_domain' not in self.request.POST or not self.request.POST['myshopify_domain']:
			raise forms.ValidationError(_("Please enter Shopify Domain."))

		if 'description' not in self.request.POST:
			raise forms.ValidationError(_("Please enter Description."))

		if 'quantity' not in self.request.POST or not self.request.POST['quantity']:
			raise forms.ValidationError(_("Please enter Quantity."))

		if 'selling_price' not in self.request.POST or not self.request.POST['selling_price']:
			raise forms.ValidationError(_("Please enter Selling Price."))

		if 'dropshipping_price' not in self.request.POST:
			raise forms.ValidationError(_("Please enter Dropshipping Price."))

		if 'sku' not in self.request.POST or not self.request.POST['sku']:
			raise forms.ValidationError(_("Please enter SKU."))

		if 'image' not in self.request.POST:
			raise forms.ValidationError(_("Please enter Image."))

		if 'wholesale_price' not in self.request.POST:
			raise forms.ValidationError(_("Please enter Whole Sale Price."))

		myshopify_domain = self.request.POST['myshopify_domain']
		vendor_detail = Account.objects.filter(website=myshopify_domain)
		if not vendor_detail:
			raise forms.ValidationError(_("Vendor does not Exist."))
		return self.cleaned_data


# class PlaceVendorProductForm(forms.Form):

# 	def __init__(self, *args, **kwargs):
# 		self.request = kwargs['request']
# 		self.request = kwargs.pop('request', None)
# 		super(PlaceVendorProductForm, self).__init__(*args, **kwargs)

# 	def clean(self):
# 		if 'HTTP_API_KEY' not in self.request.META or not self.request.META['HTTP_API_KEY']:
# 			raise forms.ValidationError(_("No HTTP_API_KEY found"))

# 		api_key = self.request.META['HTTP_API_KEY']

# 		if api_key != "pbkdf2_sha256$29000$p7lpJChcK4Lo$IHMul9j5lcPNJP4f/W1nXZknVi2N+GJIR1tZCo5C7uM=":
# 			raise forms.ValidationError(_("Wrong Api Key"))

# 		products=self.request.POST['products']
# 		print products
# 		print '\n'
# 		print type(products)

# 		if not self.request.POST['products']:
# 			print 'error'
# 			raise forms.ValidationError(_("Please enter Product Qty."))



# 		return self.cleaned_data
