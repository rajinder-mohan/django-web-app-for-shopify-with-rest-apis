





            # MAGENTO URLS






from django.conf.urls import url
from django.contrib.auth import views
from .views import *

urlpatterns = [
	url(r'^vendor_register$', VendorRegister.as_view(), name="mag_vend_register"),
	url(r'^vendor_login$', VendorLogin.as_view(), name="mag_vend_login"),
	url(r'^vendor_forget-password$', VendorForgetPassword.as_view(), name="mag_vend_forget_password"),
	url(r'^vendor_dashboard$',VendorDashboard.as_view(),name="mag_vend_dashboard"),
	url(r'^merchant-register$', MerchantRegister.as_view(), name="mag_mer_register"),
	url(r'^merchant-login$', MerchantLogin.as_view(), name="mag_mer_login"),
	url(r'^merchant-forget-password$', MerchantForgetPassword.as_view(), name="mag_mer_forget_password"),
	url(r'^merchant-dashboard$',MerchantDashboard.as_view(),name="mag_mer_dashboard"),
	url(r'^merchant-add-products$',AddProducts.as_view(),name="mag_mer_add_product"),
	url(r'^merchant-remove-product$',RemoveProduct.as_view(),name="mag_mer_remove_product"),
	url(r'^merchant-logout/$',views.logout, {'next_page': '/magento/merchant-login'}),
	url(r'^vendor-logout/$',views.logout, {'next_page': '/magento/vendor_login'}),
	url(r'^payment$',PaypalAdaptivePayment.as_view(),name="mag_mer_paypal"),
	url(r'^payment/fail$',FailPayment.as_view(),name="mag_mer_paypal_fail"),
	url(r'^vendor-add-products$',AddVendorProduct.as_view(),name="mag_ven_add_product"),
	url(r'^vendor-remove-products$',VendorRemoveProduct.as_view(),name="mag_ven_remove_product"),
	url(r'^allow-mercahnts$',ControlMerchantAccess.as_view(),name="allowmerchants"),
	url(r'^vendor_update_paypal$',PaypalEmail.as_view(),name='vendor_update_paypal'),
	url(r'^availability$', ProductAvailable.as_view(), name="product_available"),
	url(r'^merchant_uninstall$', UninstallMerchant.as_view(), name="merchant_uninstall"),
	url(r'^view_varient_product$', ViewVarientProduct.as_view(), name="view_varient_product"),
]
