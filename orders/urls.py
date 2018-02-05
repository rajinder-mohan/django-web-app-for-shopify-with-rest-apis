from django.conf.urls import url
from .views import PlaceOrder, OrderPaid,FulfillmentStatus
from shopify.views import orders_list

urlpatterns = [
	url(r'^$', orders_list, name="all_orders"),
	url(r'^place$', PlaceOrder.as_view(), name="place_order"),
	url(r'^paid$', OrderPaid.as_view(), name='order_paid'),
	url(r'^fulfillment_status$',FulfillmentStatus.as_view(),name='fulfilment')
]
