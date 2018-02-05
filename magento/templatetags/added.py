from django import template
from merchants.models import ProductDetail
from orders.models import OrderProducts
from shopify.models import Account
import json
register = template.Library()


@register.filter(name='added')
def added(product_id, merchant_id):
    try:
        product=ProductDetail.objects.get(product__id=product_id,merchant__id=merchant_id)
        return product.PlatformProductId
    except ProductDetail.DoesNotExist:
        return False

@register.filter(name='varientdata')
def varientdata(varientvalue):

    try:
        values = json.loads(varientvalue)
        elmnts=""
        for key,value in values.items():
            elmnts +=" <select name='{}' id='{}' onchange='varients(this)'>".format(key,key)
            attrb_name = key.split("_")
            elmnts += "<option value='false'>{}</option> Select ".format(attrb_name[-1])
            for prps in value:
                elmnts += "<option value='{}'>{}</option>".format(prps,prps)
            elmnts +="</select>"
        return elmnts
    except Exception as e:
        print(e)
        return False

@register.filter(name='vendors')
def vendors(order_id):

    try:
        productdetails = OrderProducts.objects.filter(order__id=order_id).values("user").distinct()

        elmnts=""
        for productdetail in productdetails:
            vendor = Account.objects.get(id=productdetail["user"])
            elmnts +="{} {},".format(vendor.first_name,vendor.last_name)
        if elmnts:
            elmnts = elmnts[:-1]
            return elmnts
        else:
            return "Name not found"
    except Exception as e:
        print(e)
        return "Error occur while fetching names."
