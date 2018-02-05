from django.conf.urls import url
from .views import *
from django.views.generic import TemplateView
from mvpadmin.views import index

urlpatterns = [
	url(r'^$', login, name='login'),
	url(r'^dashboard', index),
	url(r'^logout', logout,name="logout"),
	url(r'^apply', register),
	url(r'^products$', dashboard),
	url(r'^products/add$', add_product, name="add_product"),
	url(r'^products/delete$', delete_product, name="delete_product"),
	url(r'^forgot_password$', forgot_password, name="forgot_password"),
	url(r'^reset_password$', reset_password, name="reset_password"),
	url(r'^activate_account/(?P<user_id>\d+)/(?P<activation_key>\w+)', activate_account),
	url(r'^accounts', AccountsList.as_view(template_name="shopify/accounts.html")),
	url(r'^categories', CategoryDetailView.as_view()),
	url(r'^testing', TemplateView.as_view(template_name="shopify/accounts.html")),
	#url(r'^vendor', Vendor.as_view()),
	url(r'^latest_image', ImagesView.as_view()),
	url(r'^datatable/data', AccountListJson.as_view(), name='account_list_json'),
	url(r'^people', people),
	url(r'^table/data/$', AccountDataView.as_view(), name='table_data')
]

# Shopify Urls
