from __future__ import unicode_literals

from django.db import models
from orders.models import Orders
# Create your models here.

class PaypalAdaptive(models.Model):
    order = models.ForeignKey(Orders, blank=True, null=True,on_delete=models.CASCADE)
    uiid = models.CharField(max_length=500)
    pay_key = models.CharField(max_length=500)
    status = models.BooleanField(default=False)
