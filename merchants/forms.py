from django import forms
from .models import AccountDetail, AccessToken
from shopify.models import Account, Products
import json
from django.utils.translation import gettext as _
from django.core.validators import validate_email
import validators


class AddAccountForm(forms.Form):
	def __init__(self, *args, **kwargs):
		self.request = kwargs['request']
		self.request = kwargs.pop('request', None)
		super(AddAccountForm, self).__init__(*args, **kwargs)

	def clean(self):

		email = self.request.POST['email']
		try:
			validate_email(email)
		except:
			raise forms.ValidationError(_("Please enter valid Email."))

		shopify_domain = self.request.POST['myshopify_domain']

		verify_shopifydomain = validators.domain(shopify_domain)
		if verify_shopifydomain is not True:
			raise forms.ValidationError(_("Please enter valid Shopify Domain."))

		main_domain = self.request.POST['domain']
		verify_domain = validators.domain(main_domain)
		if verify_domain is not True:
			raise forms.ValidationError(_("Please enter valid Domain."))

		# existing_email = AccountDetail.objects.filter(email=email)
		# if existing_email:
		# 	raise forms.ValidationError(_("Email Already Exists."))

		# existing_main_domain = AccountDetail.objects.filter(main_domain=main_domain)
		# if existing_main_domain:
		# 	raise forms.ValidationError(_("Domain Already Exists."))

		return self.cleaned_data


class AddProductForm(forms.Form):
	def __init__(self, *args, **kwargs):
		self.request = kwargs['request']
		self.request = kwargs.pop('request', None)
		super(AddProductForm, self).__init__(*args, **kwargs)

	def clean(self):

		if 'HTTP_ACCESS_TOKEN' not in self.request.META or not self.request.META['HTTP_ACCESS_TOKEN']:
			error_list = {"error": "You don't have access to add product."}
			raise forms.ValidationError(_(json.dumps(error_list)))

		access_token = self.request.META['HTTP_ACCESS_TOKEN']
		existing_token = AccessToken.objects.filter(access_token=access_token)
		if not existing_token:
			error_list = {"error": "You don't have access to add product."}
			raise forms.ValidationError(_(json.dumps(error_list)))

		if 'domain' not in self.request.POST or not self.request.POST['domain']:
			error_list = {"error": "Please enter Domain."}
			raise forms.ValidationError(_(json.dumps(error_list)))

		if 'vendor_id' not in self.request.POST or not self.request.POST['vendor_id']:
			error_list = {"error": "Please enter Vendor."}
			raise forms.ValidationError(_(json.dumps(error_list)))

		if 'product_id' not in self.request.POST or not self.request.POST['product_id']:
			error_list = {"error": "Please enter Product."}
			raise forms.ValidationError(_(json.dumps(error_list)))

		if 'platform' not in self.request.POST or not self.request.POST['platform']:
			error_list = {"error": "Please enter Platform."}
			raise forms.ValidationError(_(json.dumps(error_list)))

		if 'PlatformProductId' not in self.request.POST or not self.request.POST['PlatformProductId']:
			error_list = {"error": "Please enter PlatformProductId."}
			raise forms.ValidationError(_(json.dumps(error_list)))

		domain = self.request.POST['domain']
		verify_domain = validators.domain(domain)
		if verify_domain is not True:
			error_list = {"error": "Please enter valid Domain."}
			raise forms.ValidationError(_(json.dumps(error_list)))

		existing_domain = AccountDetail.objects.filter(main_domain=domain)
		if not existing_domain:
			error_list = {"error": "Domain Does Not Exist"}
			raise forms.ValidationError(_(json.dumps(error_list)))

		status = existing_domain[0].status
		if int(status) == 0:
			error_list = {"error": "You don't have access to add product. Please contact to adminitrator to activate your account."}
			raise forms.ValidationError(_(json.dumps(error_list)))

		vendor_id = self.request.POST['vendor_id']
		existing_vendor = Account.objects.filter(id=vendor_id)
		if not existing_vendor:
			error_list = {"error": "Vendor does not exist."}
			raise forms.ValidationError(_(json.dumps(error_list)))

		product_id = self.request.POST['product_id']
		existing_product = Products.objects.filter(id=product_id)
		if not existing_product:
			error_list = {"error": "Product does not exist."}
			raise forms.ValidationError(_(json.dumps(error_list)))
		return self.cleaned_data
