from django.shortcuts import redirect
from django.contrib import messages
from shopify.models import Account
from merchants.models import AccountDetail
import datetime
import random
import uuid
from django.utils import timezone
def session_check(function):
    def wrap(request, *args, **kwargs):
        try:
            token=request.session['vendor_token']
            account_obj=Account.objects.get(token=token)
            if account_obj:
                token_generated_time=account_obj.token_time
                currenttime=timezone.now()
                differance=currenttime-token_generated_time
                m = divmod((differance.total_seconds()),60) #minutes
                if int(m[0])>15:
                    random_new_token=str(uuid.uuid4())
                    account_obj.token=random_new_token
                    account_obj.token_time=datetime.datetime.now(timezone.utc)
                    account_obj.save()
                    request.session['vendor_token']=random_new_token
            else:
                return redirect('/magento/vendor_login')
        except Exception as r:
            return redirect('/magento/vendor_login')


        return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def merchant_session_check(function):
    def wrap(request, *args, **kwargs):
        try:
            token=request.session['merchant_token']
            account_obj=AccountDetail.objects.get(token=token)
            if account_obj:
                token_generated_time=account_obj.token_time
                currenttime=datetime.datetime.now(timezone.utc)
                differance=currenttime-token_generated_time
                m = divmod((differance.total_seconds()),60) #minutes
                if int(m[0])>15:
                    random_new_token=str(uuid.uuid4())
                    account_obj.token=random_new_token
                    account_obj.token_time=datetime.datetime.now(timezone.utc)
                    account_obj.save()
                    request.session['merchant_token']=str(random_new_token)
            else:
                return redirect('/magento/merchant-logout')
        except AccountDetail.DoesNotExist:
            return redirect('/magento/merchant-logout')
        except Exception as e:
            print(e)
            print("Exception in merchant decorator")
            return redirect('/magento/merchant-logout')

        return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
