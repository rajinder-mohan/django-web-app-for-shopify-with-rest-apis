from django.http import HttpResponse


class SimpleMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        # if 'user_id' not in request.session:
        #     return HttpResponse("not login")

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        #return HttpResponse("test")

        return response