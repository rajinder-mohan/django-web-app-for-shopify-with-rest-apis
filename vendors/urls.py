from django.conf.urls import url
from .views import *

urlpatterns = [
	url(r'^add$', AddVendor.as_view(), name='add_vendor'),
	url(r'^add_product$', AddProduct.as_view(), name='add_product'),
	url(r'^delete_product$',DeleteProduct.as_view(),name='delete_product'),
	url(r'^uninstall_vendor$',UninstallVendor.as_view(),name='uninstall_vendor'),
	url(r'^place_vendor_product$',PlaceVendorProduct.as_view(),name='place_vendor'),
	url(r'^all_merchant_list$',MerchantList.as_view(),name='merchant_list'),
	url(r'^change_merchant_status$',ChangeMerchant.as_view(),name='change_merchant_status'),
	url(r'^all_vendor_orders$',AllVendorOrders.as_view(),name='all_vendor_orders'),
	url(r'^update_order$', UpdateOrder.as_view(), name='update_order'),
	url(r'^update_paypal$',UpdatePayPAl.as_view(),name='update_paypal')
]
