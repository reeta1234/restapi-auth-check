from django.http import HttpResponse
import requests,json
from rest_framework import status 
from rest_framework.response import Response 
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.conf import settings
from rest_framework.views import APIView


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

# def external_api_view(request):
#     return HttpResponse("Hello, external_api_view.")

@api_view(['GET'])
#@renderer_classes((JSONRenderer,)) 
def external_api_view(request): 
     #url = 'http://localhost:9200/job1/_search?q=Dummy PDF file?pretty=true'
     #url = 'http://localhost:9200/twitter374/_search?pretty' 
     url = settings.BASE_URL + '/twitter374/_search?pretty'
     r = requests.get(url) 
     data = r.json() 
     return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
def view(request):
    headers = {"content-type": "application/json"}
    payload = {
    "user" : "kimchy",
    "post_date" : "2009-11-15T14:12:12",
    "message" : "trying out Elasticsearch"
}
    r = requests.post("http://localhost:9200/twitter374/_doc/?pretty",headers=headers,data=json.dumps(payload))
    return Response(r, status=status.HTTP_200_OK)


class Test(APIView):

    def post(self, request, format=None):
        return Response('POST METHOD')

    def get(self, request, format=None):
        return Response('GET METHOD')