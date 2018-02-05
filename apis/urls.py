from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from .views import accounts_detail, products_detail, categories_detail, account_types, AccountList, AccountsDetail, AccountGenericList, AccountUpdateGenericList, AccountListView, AccountRetrieveView, VendorDetail, VendorList, ProductsList, AllProductsList, getVendor

urlpatterns = [
	url(r'^accounts$', accounts_detail),
	url(r'^accounts/types', account_types),
	url(r'^products', AllProductsList),
	#url(r'^products', products_detail),
	url(r'^all_products', categories_detail),
	url(r'^accounts_by_class$', AccountList.as_view()),
	url(r'^account_by_class/(?P<id>\d+)', AccountsDetail.as_view()),
	url(r'^vendor_products', VendorDetail.as_view()),
	url(r'^accounts_by_generics', AccountGenericList.as_view()),
	url(r'^update_by_generics/(?P<pk>\d+)', AccountUpdateGenericList.as_view()),
	url(r'^account_list', AccountListView.as_view()),
	url(r'^retrieve_account/(?P<pk>\d+)', AccountRetrieveView.as_view()),
	url(r'^vendors', VendorList.as_view()),
	url(r'^vendorproducts/(?P<user_id>\d+)', ProductsList.as_view()),
	url(r'^get_vendor$', getVendor.as_view(), name='get_vendor')
]
