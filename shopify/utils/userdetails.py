from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseRedirect
from shopify.models import Account,AccountType


class UserDetail(object):

	def __init__(self,request):
		self.request=request

		#return true if login user has type=1
	def is_admin(self):
		if self.request.session['user']['type']==1:
			return True


	def is_vendor(self):
		if self.request.session['user']['type']==3:
			return True

	def getLoginUser(self):
		user=None
		if 'user' in self.request.session:
			user= self.request.session['user']

		return user

	def setSession(self,user):
			account_type={"admin":False,"user":False,"vendor":False}
			user_name = user.first_name + " " + user.last_name
			user_name=user_name.title()
			accounttype = AccountType.objects.get(id=user.account_id)
			account_type[accounttype.type] = True
			self.request.session['user'] = {"id":user.id,"type":user.account_id,"first_name":user.first_name,"last_name":user.last_name,"user_name":user_name,"account_type":account_type}

	def clearSession(self):
		del self.request.session['user']

	def get_admin(self):
		admin_detail = Account.objects.get(id=1)
		return admin_detail
