from django.conf.urls import url
from mvpadmin import views
from shopify.views import add_product, dashboard, orders_list


urlpatterns=[
	url(r'^$',views.index,name="mvpadmin"),
	url(r'^labels$',views.vendors_list, name="vendors"),
	url(r'^merchants$', views.merchants_list, name="merchants"),
	url(r'^merchant_status$', views.merchant_status, name="merchant_status"),
	url(r'^labels/products',views.vendors, name="vendors_products"),
	url(r'^products$', dashboard),
	url(r'^products/add$', add_product, name="add_product"),
	url(r'^user_status', views.user_status),
	url(r'^denyaccess', views.denyaccess, name="denyaccess"),
	url(r'^orders', orders_list, name="orderslist"),
	url(r'^labels_orders', views.labels_orders, name="labels_orders"),
	url(r'^label_order', views.label_order, name='label_order'),
	url(r'^add_commision$', views.add_commision, name='add_commision')
]
