from __future__ import unicode_literals
from django.db import models
from shopify.models import Products, Account
from django.conf import settings
import time
import PIL
from PIL import Image
import os
from django.utils import timezone

def get_image_path(self,filename):
	file_path=settings.MEDIA_ROOT

	save_path = ''
	thumbnails=Thumbnails.objects.all()


	if (self.token):
		file_name=self.token+"_"+filename
		self.image_name=file_name
		file_path=file_path + "/products/"+str(self.token)
		save_path="products/"+str(self.token)+"/"+file_name
	else:
		currenttime=str(int(time.time()))
		file_name=currenttime+"_"+filename
		self.image_name=file_name
		file_path=file_path + "/products/"+str(currenttime)
		save_path="products/"+str(currenttime)+"/"+file_name
		if(not os.path.exists(file_path)):
			os.makedirs(file_path)
		for thumbnail in thumbnails:
			img = Image.open(self.image)
			width = thumbnail.width
			height = thumbnail.height
			original_width, original_height = img.size
			new_width = width
			if int(original_width) < width:
				new_width = original_width
			img = img.resize((new_width,height), PIL.Image.ANTIALIAS)
			filename=file_path+"/"+str(width)+"_"+file_name
			img.save(filename)
		self.token = currenttime


	# if(self.product):
	# 	file_path=file_path + "/products/"+str(self.product.id)
	# 	save_path="products/"+str(self.product.id)+"/"+file_name
	# 	if(not os.path.exists(file_path)):
	# 		os.makedirs(file_path)
	# 	for thumbnail in thumbnails:
	# 		img = Image.open(self.image)
	# 		width = thumbnail.width
	# 		height = thumbnail.height
	# 		img = img.resize((width,height), PIL.Image.ANTIALIAS)
	# 		filename=file_path+"/"+str(width)+"_"+file_name
	# 		img.save(filename)
		#print  'product_{0}/{1}'.format(self.product.id, filename)
	return save_path


class Images(models.Model):
	user = models.ForeignKey(Account, on_delete=models.CASCADE)
	product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True)
	image=models.ImageField(upload_to=get_image_path, default='default/image.jpg', max_length=500)
	image_name=models.CharField(max_length=200,blank=True,null=True)
	created_date=models.DateTimeField(default=timezone.now)
	updated_date=models.DateTimeField(default=timezone.now)
	token = models.CharField(max_length=50, blank=True)
	def __str__(self):

		return str(self.id)


class Thumbnails(models.Model):
	width=models.IntegerField()
	height=models.IntegerField()
