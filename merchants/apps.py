from __future__ import unicode_literals

from django.apps import AppConfig


class MerchantsConfig(AppConfig):
    name = 'merchants'

    def ready(self):
    	import merchants.signals
