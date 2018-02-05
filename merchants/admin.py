from django.contrib import admin
from .models import AccountDetail, ProductDetail, AccessToken, DenyAccess

admin.site.register(AccountDetail)
admin.site.register(ProductDetail)
admin.site.register(AccessToken)
admin.site.register(DenyAccess)
