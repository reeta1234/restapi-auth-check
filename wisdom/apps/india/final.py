@method_decorator(csrf_exempt, name='dispatch')
class IngestPipline(View):

    def post(self, request, format=None):
        payload = {
            "description" : "describe pipeline",
            "processors" : [
                {
                    "attachment" : {
                            "field" : "data"
                    }
                }
            ]
        }
        headers = {"content-type": "application/json"}
        url = settings.BASE_URL + '/_ingest/pipeline/my-pipeline'
        r = requests.put(url,headers=headers,data=json.dumps(payload))
        data = r.json() 
        return JsonResponse({"data":data,"status":"success"})


    def get(self, request, format=None):
        url = settings.BASE_URL + "/_ingest/pipeline/my-pipeline?pretty"
        r = requests.get(url) 
        data = r.json() 
        return JsonResponse({"data":data,"status":"success"})