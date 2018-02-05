from django import template
from shopify.models import Products
from merchants.models import DenyAccess
register = template.Library()


@register.assignment_tag
def exists(product_id, vendor_id):
    try:

        product_details=Products.objects.get(PlatformProductId=product_id,user__id=vendor_id)
        return product_details
    except Products.DoesNotExist:
        return False

@register.filter
def controlMerchant(merchant_id,vendor_id):
    try:
        DenyAccess.objects.get(vendor__id=vendor_id,merchant__id=merchant_id)
        return True
    except DenyAccess.DoesNotExist:
        return False
