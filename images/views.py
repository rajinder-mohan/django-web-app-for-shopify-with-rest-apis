from django.shortcuts import render
from django.http import HttpResponse
from shopify.utils.userdetails import UserDetail
from .models import Images
import json
from django.conf import settings
import os

def add_image(request):
	if 'token' in request.POST:
		token = request.POST['token']

	userdetail = UserDetail(request).getLoginUser()
	user_id = userdetail['id']

	data = {}

	if 'file' in request.FILES:
		image = request.FILES.get('file')
		file_type = image.content_type.split('/')[0]

		if str(file_type) != "image":
			data = {'is_valid': False, 'message': 'Please upload Images Only.'}
			return HttpResponse(json.dumps(data))
		try:
			images=Images(user_id=user_id,image=request.FILES.get('file'))
			images.save()
			token = images.token
			image_id = images.id
			image_name = images.image_name
			url = "http://"+request.META['HTTP_HOST']+"/images/view/"+str(token)+"/"+str(image_id)
			data = {'is_valid': True, 'name': image_name, 'url': url, 'token': token}
		except:
			data = {'is_valid': False, 'message': 'Cannot Be Uploaded.'}
	return HttpResponse(json.dumps(data))

def view_image(request, token=0, image_id=0, thumb_size=''):
	file_path=settings.MEDIA_ROOT
	file_name = ''

	if image_id != 0:
		file_path=file_path + "/products/"+str(token)
		image_detail = Images.objects.get(id=image_id)
		file_name = image_detail.image_name
		if thumb_size:
			thumbsize = thumb_size.split("_")
			size = thumbsize[1]
			file_name = str(size)+"_"+file_name
		else:
			file_name = "400_" + file_name
	else:
		file_name = str(token)+"_"+"default.png"

	image_data = ''
	image_path = file_path + "/" + file_name
	if image_path:
		image_data = open(image_path, "rb").read()

	return HttpResponse(image_data, content_type="image/png")
