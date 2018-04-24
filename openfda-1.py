import http.client
import json

headers = {'User-Agent': 'http-client'}

conn = http.client.HTTPSConnection("api.fda.gov")
conn.request("GET", "/drug/label.json?limit=1", None, headers)
r1 = conn.getresponse()
print(r1.status, r1.reason)
repos_raw = r1.read().decode("utf-8")
conn.close()

repos = json.loads(repos_raw)


print("The id is:", repos['results'][0]["id"]) # enter dictionary {} inside another dictionary
print("The purpose is.", repos['results'][0]["purpose"])
print("The purpose is:", repos['results'][0]["openfda"]["manufacturer_name"])
