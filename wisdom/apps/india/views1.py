from django.http import HttpResponse,JsonResponse
import requests,json
from django.views import View
from apps.india.utils import json_response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@method_decorator(csrf_exempt, name='dispatch')
class Test(View):

    def post(self, request, format=None):
        return JsonResponse({'status':'500'})
    
    def get(self, request, format=None):
        #return JsonResponse({'status': 'user with {} not exist'.format('username')}, status=404)
        #return JsonResponse({"message": "Okjj"}, status=200)
        return JsonResponse({'status':'500'})
        #return JsonResponse({'foo': 'bar'})


