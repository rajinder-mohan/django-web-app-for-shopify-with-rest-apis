from django.conf.urls import url
from .views import AddMerchant, AddProduct, DeleteMerchant


urlpatterns = [
	url(r'^add$', AddMerchant.as_view()),
	url(r'^delete$', DeleteMerchant.as_view()),
	url(r'^products/add$', AddProduct.as_view()),
	url(r'^products/delete$', AddProduct.as_view()),
]
