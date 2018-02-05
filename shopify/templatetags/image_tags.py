from django import template
from django.template import Template
from shopify.models import Products
from images.models import Images
register=template.Library()



@register.simple_tag
def image_products_id(product,thumb_size):
	url="/media/products/"

	if category.image_name:
		image_path=url+str(category.id)+"/"+str(thumb_size)+"_"+category.image_name
	else:
		image_path=url+"/"+str(thumb_size)+"_"+"default.png"

	return image_path


@register.simple_tag
def image_products(product,thumb_size):
	url="/images/view/"

	image_path = ''

	image=product.images_set.all()
	length = len(image)

	if length > 0:
		image_id = image[length-1].id
		token = image[length-1].token
		if token:
			image_path = url + str(token) + "/" + str(image_id)
	else:
		image_path=url+str(thumb_size)
	return image_path


@register.simple_tag
def product_url(product,thumb_size):

	return True
