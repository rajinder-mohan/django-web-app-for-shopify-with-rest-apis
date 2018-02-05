from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import AccountDetail, AccessToken
import binascii
import os


@receiver(post_save, sender=AccountDetail)
def model_post_save(sender, **kwargs):
	data = kwargs['instance']
