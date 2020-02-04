from django.http import HttpResponse,JsonResponse
import requests,json
from django.shortcuts import render
from django.conf import settings
from django.views import View
from apps.india.utils import json_response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime
from elasticsearch import Elasticsearch
import base64,os
import PyPDF2

import requests
from rest_framework import status 
from rest_framework.response import Response 
from rest_framework.decorators import api_view, renderer_classes 
from rest_framework.renderers import JSONRenderer
es = Elasticsearch()


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

# def external_api_view(request):
#     return HttpResponse("Hello, external_api_view.")
 
def external_api_view(request): 
     #url = 'http://localhost:9200/job1/_search?q=Dummy PDF file?pretty=true'
     #url = 'http://localhost:9200/twitter374/_search?pretty' 
     url = settings.BASE_URL + '/twitter374/_search?pretty'
     #url = "http://dummy.restapiexample.com/api/v1/employees"
     r = requests.get(url) 
     data = r.json() 
     return json_response({"data":data,"status":"success"})

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
    #return JsonResponse('postdata METHOD')


@method_decorator(csrf_exempt, name='dispatch')
class Test(View):

    def post(self, request, format=None):
        try:
            headers = {"content-type": "application/json"}
            payload1 = {
                "description" : "Extract attachment information",
                "processors" : [
                    {
                        "attachment5" : {
                            "field" : "data"
                        }
                    }
                ]
            }
            payload = {
                "data": "e1xydGYxXGFuc2kNCkxvcmVtIGlwc3VtIGRvbG9yIHNpdCBhbWV0DQpccGFyIH0="
            }
            #r = requests.put("http://localhost:9200/_ingest/pipeline/reet_attachment",headers=headers,data=json.dumps(payload))
            r = requests.put("http://localhost:9200/pdfindex2/_doc/4?pipeline=reet_attachment",headers=headers,data=json.dumps(payload))
            return json_response({"data":r.json() , "status66":status.HTTP_300_MULTIPLE_CHOICES})
        except TypeError as e:
            return json_response({"data":e , "status66":status.HTTP_300_MULTIPLE_CHOICES})


    def get(self, request, format=None):
        #url = settings.BASE_URL + '/twitter374/_search?pretty'
        url = "http://localhost:9200/pdfindex/_search?pretty"
        r = requests.get(url) 
        data = r.json() 
        return json_response({"data":data,"status":"success"})
        #return JsonResponse({'status': 'user with {} not exist'.format('username')}, status=404)
        #return JsonResponse({"message": "Okjj"}, status=200)
        #return JsonResponse({'foo': 'bar'})


@api_view(['GET'])
@renderer_classes((JSONRenderer,)) 
def external_api_view2(request): 
     url = 'http://dummy.restapiexample.com/api/v1/employees' 
     r = requests.get(url,headers={'x-foo': 'fdsfsd'}) 
     data = r.json() 
     return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
@renderer_classes((JSONRenderer,)) 
def testIndex(requests):
    payload = {
        'author': 'kimchy',
        'text': 'Elasticsearch: cool. bonsai cool.',
        'timestamp': datetime.now(),
    }
    res = es.index(index="test-index", id=1, body=payload)
    return Response(res, status=status.HTTP_200_OK)
    # print(res['result'])
    # res = es.get(index="test-index", id=1)
    # print(res['_source'])
    # es.indices.refresh(index="test-index")
    # res = es.search(index="test-index", body={"query": {"match_all": {}}})
    # print("Got %d Hits:" % res['hits']['total']['value'])
    # for hit in res['hits']['hits']:
    #     print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])

@api_view(['GET'])
@renderer_classes((JSONRenderer,)) 
def getBase64Data(requests):
    print(settings.BASE_DIR+"/docs/sample.txt")
    data = open(settings.BASE_DIR+"/docs/sample.txt", "r").read()
    encoded = base64.urlsafe_b64encode(data.encode('UTF-8')).decode('ascii')
    tt = base64.decodestring(encoded.encode('UTF-8'))
    # if settings.IS_EXIST(settings.BASE_DIR+"/docs/sample.txt"):
    #     data = open("/home/reeta/Reeta/wisdom/wisdom/docs/sample.txt", "r").read()
    #     encoded = base64.b64encode(data)
    # else:
    #     pass
    return Response(tt, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class Base64Test(View):

    def post(self, request, format=None):
        try:
            headers = {"content-type": "application/json"}
            if settings.IS_EXIST(settings.BASE_DIR+"/docs"):
                for a,i in enumerate(os.listdir(settings.BASE_DIR+"/docs")):
                    if i.endswith('.pdf'):
                        id = int(a+6)
                        pdfContent = self.readPDF(settings.BASE_DIR+"/docs/"+i)
                        encoded = base64.urlsafe_b64encode(pdfContent.encode('UTF-8')).decode('ascii')
                        payload = {
                            "data": encoded
                        }
                        postUrl = "http://localhost:9200/pdfindex2/_doc/{}?pipeline=reet_attachment".format(id)
                        print(postUrl)
                        print(pdfContent)
                        r = requests.put(postUrl,headers=headers,data=json.dumps(payload))
                        print(r)
                        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                    else:
                        pass

                print(id)
            else:
                pass
            #r = requests.put("http://localhost:9200/_ingest/pipeline/reet_attachment",headers=headers,data=json.dumps(payload))
            
            # pdfContent = self.readPDF(settings.BASE_DIR+"/docs/sample.pdf")
            # encoded = base64.urlsafe_b64encode(pdfContent.encode('UTF-8')).decode('ascii')
            # payload = {
            #     "data": encoded
            # }
            # r = requests.put("http://localhost:9200/pdfindex2/_doc/6?pipeline=reet_attachment",headers=headers,data=json.dumps(payload))
            return json_response({"data":r.json() , "status66":status.HTTP_300_MULTIPLE_CHOICES})
            #return json_response({"data":'encoded','msg':'pdfContent' , "status66":status.HTTP_300_MULTIPLE_CHOICES})
        except TypeError as e:
            return json_response({"data":e , "status66":status.HTTP_300_MULTIPLE_CHOICES})


    def get(self, request, format=None):
        text_files = [f for f in os.listdir(settings.BASE_DIR+"/docs") if f.endswith('.pdf')]
        # if settings.IS_EXIST(settings.BASE_DIR+"/docs"):
        #     for i in os.listdir(settings.BASE_DIR+"/docs"):
        #         if i.endswith('.pdf'):
        #             print(settings.BASE_DIR+"/docs/"+i)
        #         else:
        #             pass
        # else:
        #     pass
        filedata = open(settings.BASE_DIR+"/docs/sample.pdf", "rb")
        pdfReader = PyPDF2.PdfFileReader(filedata)
        pageObj = pdfReader.getPage(0) 
        data = pageObj.extractText()

        tt = ''
        with open(settings.BASE_DIR+"/docs/sample.pdf", 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfFileReader(pdf_file)

            # printing first page contents
            # pdf_page = pdf_reader.getPage(0)
            # print(pdf_page.extractText())
            
            # reading all the pages content one by one
            for page_num in range(pdf_reader.numPages):
                pdf_page = pdf_reader.getPage(page_num)
                tt += '\n'+pdf_page.extractText()
                print(f'Number of Pages in PDF File is {pdf_reader.getNumPages()}')
                print(f'PDF Metadata is {pdf_reader.documentInfo}')
                # print(f'PDF File Author is {pdf_reader.documentInfo["/Author"]}')
                # print(f'PDF File Creator is {pdf_reader.documentInfo["/Creator"]}')
                print(pdf_page.extractText())
                print('********************************')
            print(tt)
        pdfContent = self.readPDF(settings.BASE_DIR+"/docs/sample.pdf")
        encoded = base64.urlsafe_b64encode(pdfContent.encode('UTF-8')).decode('ascii')
        #tt = base64.decodestring(encoded.encode('UTF-8'))
        return json_response({"data":encoded,'msg':pdfContent,"status":"success"})

    def readPDF(self,file):
        pdfContent = ''
        with open(file, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfFileReader(pdf_file)
            for page_num in range(pdf_reader.numPages):
                pdf_page = pdf_reader.getPage(page_num)
                pdfContent += '\n'+pdf_page.extractText()
                # print(f'Number of Pages in PDF File is {pdf_reader.getNumPages()}')
                # print(f'PDF Metadata is {pdf_reader.documentInfo}')
                # # print(f'PDF File Author is {pdf_reader.documentInfo["/Author"]}')
                # # print(f'PDF File Creator is {pdf_reader.documentInfo["/Creator"]}')
                # print(pdf_page.extractText())
                # print('********************************')
        return pdfContent



@api_view(['GET'])
@renderer_classes((JSONRenderer,)) 
def extractPDFContent(requests):
    with open(settings.BASE_DIR+"/docs/dummy.pdf", 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)
        information = pdf_reader.getDocumentInfo()
        print(information)
        pageObj = pdf_reader.getPage(0) 
        data = pageObj.extractText()
        # print(f'Number of Pages in PDF File is {pdf_reader.getNumPages()}')
        # print(f'PDF Metadata is {pdf_reader.documentInfo}')
        # print(f'PDF File Author is {pdf_reader.documentInfo["/Author"]}')
        # print(f'PDF File Creator is {pdf_reader.documentInfo["/Creator"]}')
        pdf_file.close()

    # filedata = open(settings.BASE_DIR+"/docs/dummy.pdf", "rb")
    # pdfReader = PyPDF2.PdfFileReader(filedata)
    # pageObj = pdfReader.getPage(0) 
    # data = pageObj.extractText()
    return Response(data, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class PDFIndex(View):

    def post(self, request, format=None):
        payload = {
            "data": "e1xydGYxXGFuc2kNCkxvcmVtIGlwc3VtIGRvbG9yIHNpdCBhbWV0DQpccGFyIH0="
        }
        headers = {"content-type": "application/json"}
        url = settings.BASE_URL + '/mypipelineindex/_doc/45?pipeline=my-pipeline'
        r = requests.put(url,headers=headers,data=json.dumps(payload))
        data = r.json() 
        return JsonResponse({"data":data,"status":"success"})


    def get(self, request, format=None):
        url = settings.BASE_URL + "/_ingest/pipeline/my-pipeline?pretty"
        r = requests.get(url) 
        data = r.json() 
        return JsonResponse({"data":data,"status":"success"})

@method_decorator(csrf_exempt, name='dispatch')
class SimpleTest(View):
    def post(self,request,id,format=None):
        print(id)
        print(request.POST.get('price_lte'))
        return JsonResponse({"data":'Post Data',"status":"success"})
    def get(self,request,id,format=None):
        print(id)
        print(request.GET.get('price_lte'))
        print(request.headers)
        if(request.headers['X-Api-Key']=='abc'):
            return JsonResponse({"data":'Get Data auth get success',"status":"success"})
        else:
            return JsonResponse({"data":'Get Data auth get failed',"status":"success"})