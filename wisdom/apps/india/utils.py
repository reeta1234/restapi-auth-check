#from django.http import HttpResponse,JsonResponse
from django.http.response import JsonResponse
from rest_framework.response import Response

def json_response(response_dict):
    # try:
    #     return Response({"message": "Ok"}, status=200)
    # except Exception as e:
    #     return Response({"Error": e}, status=400) 
    # print(response)
    # return response
    return JsonResponse(response_dict)