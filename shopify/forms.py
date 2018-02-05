from django import forms
from .models import Account,AccountType,Vendor, Products
from passlib.hash import django_pbkdf2_sha256 as handler
from django.utils.translation import gettext as _
from shopify.utils.userdetails import UserDetail


class LoginForm(forms.Form):
	def __init__(self, *args, **kwargs):
		self.request = kwargs['request']
		self.request = kwargs.pop('request', None)
		super(LoginForm, self).__init__(*args, **kwargs)

	def clean(self):
		emailid = self.request.POST['emailid']
		password = self.request.POST['password']

		user = Account.objects.filter(emailid=emailid)
		if user:
			user_status = user[0].status

			if int(user_status) == 0:
				raise forms.ValidationError(_("Disabled Account. Please contact the administrator."))
			hash_password = user[0].password
			verify_password = handler.verify(password, hash_password)
			if verify_password is False:
				raise forms.ValidationError(_("Invalid Password"))
		else:
			raise forms.ValidationError(_("Invalid Emailid"))
		return self.cleaned_data


class RegisterForm(forms.Form):
	def __init__(self, *args, **kwargs):
		self.request = kwargs['request']
		self.request = kwargs.pop('request', None)
		super(RegisterForm, self).__init__(*args, **kwargs)

	def clean(self):
		emailid = self.request.POST['emailid']
		vendor = self.request.POST['vendor']

		user_email = Account.objects.filter(emailid=emailid)
		if user_email:
			raise forms.ValidationError(_("Emailid Already Exists"))

		user_vendor = Vendor.objects.filter(vendor=vendor)
		if user_vendor:
			raise forms.ValidationError(_("Label Already Exists"))
		return self.cleaned_data


class ProductForm(forms.Form):
	def __init__(self, *args, **kwargs):
		self.request = kwargs['request']
		self.request = kwargs.pop('request', None)
		super(ProductForm, self).__init__(*args, **kwargs)

	def clean(self):
		title = self.request.POST['title']

		user=UserDetail(self.request).getLoginUser()
		user_id=user['id']

		existing_title = Products.objects.filter(user_id=user_id, title=title)
		if existing_title:
			raise forms.ValidationError(_("Title Already Exists."))

		sku = self.request.POST['sku']
		if sku:
			existing = Products.objects.filter(sku=sku)
			if existing:
				raise forms.ValidationError(_("SKU Already Exists"))
		return self.cleaned_data


class ForgotPasswordForm(forms.Form):
	def __init__(self, *args, **kwargs):
		self.request = kwargs['request']
		self.request = kwargs.pop('request', None)
		super(ForgotPasswordForm, self).__init__(*args, **kwargs)

	def clean(self):
		emailid = self.request.POST['emailid']
		existing_emailid = Account.objects.filter(emailid=emailid)
		if not existing_emailid:
			raise forms.ValidationError(_("Sorry, this email does not exist."))
		return self.cleaned_data
