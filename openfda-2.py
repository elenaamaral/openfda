import http.client
import json

headers = {'User-Agent': 'http-client'}

conn = http.client.HTTPSConnection("api.fda.gov")
conn.request("GET", "/drug/label.json?limit=10", None, headers)
r1 = conn.getresponse()
print(r1.status, r1.reason)
repos_raw = r1.read().decode("utf-8")
conn.close()

repos = json.loads(repos_raw)


for elements in repos ["results"]:
    print (elements['id'])
	
	
for i in range(len((repos['results']))):
    try:
         print("The manufacturers are:", repos['results'][i]["openfda"]["manufacturer_name"])
    except KeyError:
        continue