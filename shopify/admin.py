from django.contrib import admin
from .models import Products, Account, AccountType, Vendor, Categories, Commission

admin.site.register(AccountType)
admin.site.register(Account)
admin.site.register(Vendor)
admin.site.register(Categories)
admin.site.register(Products)
admin.site.register(Commission)
