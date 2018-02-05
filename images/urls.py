from django.conf.urls import url
from .views import *

urlpatterns = [
	url(r'^add', add_image, name="add_image"),
	url(r'^view/(?P<token>\w+)$', view_image),
	url(r'^view/(?P<token>\w+)/(?P<image_id>\d+)$', view_image),
	url(r'^view/(?P<token>\w+)/(?P<image_id>\d+)/(?P<thumb_size>\w+)', view_image),
]
