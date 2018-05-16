
##FINAL PROJECT


import http.server
import json
import socketserver
import http.client


# To prevent Port Already in use Error after CTRL + C, letting us run the script over and over: 
socketserver.TCPServer.allow_reuse_address = True

# We define the PORT and the IP:
PORT = 8000
IP = '127.0.0.1'

class OpenFDAClient():

    def send_query(self, params):
        
        # For desired parameters for example -> ?limit = 10
        

        # User agent
        headers = {'User-Agent': 'http-client'}

        # Connection to the HTTPS client (api.fda.gov doesn't allow http so we must use HTTPS)
        con = http.client.HTTPSConnection("api.fda.gov")

        # Params
        given_url = "/drug/label.json"
        if params:
            given_url += "?" + params

        print("fetching", given_url)

        con.request("GET", given_url, None, headers)
        
        response = con.getresponse()
        print("Status:", response.status, response.reason)
        data = response.read().decode("utf-8")
        con.close()

        # parse json response
        result = json.loads(data)
        return result['results'] if 'results' in result else []
            
        

        

    def search_drugs(self, active_ingredient, limit=10):
        
        # Search for drugs given an active ingredient drug_name with limit default is 10
        
        params = 'search=active_ingredient:"{}"'.format(active_ingredient)
        
        if limit: 
            params += "&limit=" + str(limit)
        drugs = self.send_query(params) 
        return drugs['results'] if 'results' in drugs else []

    def search_companies_info(self, company_name, limit=10):
        
        # Search for companies_info given a company_name with optional limit default is 10
        
        params = 'search=openfda.manufacturer_name:"%s"' % company_name
        if limit:
            params += "&limit=" + str(limit)
        drugs = self.send_query(params)

        return drugs



    def list_drugs(self, limit=10):
        
        # List default drugs from the api the default limit is 10
        

        params = "limit=" + str(limit)

        drugs = self.send_query(params)

        return drugs

   

# EXTENSION III: Includes the logic to extract the data from drugs result. 
class OpenFDAParser():


    def parse_drugs(self, drugs):
       
        # parse drugs information from the openfda api
        

        drugs_labels = []

        for drug in drugs:
            drug_label = drug['id']
            if 'active_ingredient' in drug:
                drug_label += " " + drug['active_ingredient'][0]
            if 'openfda' in drug and 'manufacturer_name' in drug['openfda']:
                drug_label += " " + drug['openfda']['manufacturer_name'][0]

            drugs_labels.append(drug_label)

        return drugs_labels

    def parse_companies_info(self, drugs):
        
        # Parse extracted drugs data and list all company info
        
        companies_info = []
        for drug in drugs:
            if 'openfda' in drug and 'manufacturer_name' in drug['openfda']:
                companies_info.append(drug['openfda']['manufacturer_name'][0])
            else:
                companies_info.append("Unknown")

            companies_info.append(drug['id'])

        return companies_info

    # EXTENSION I: list warnings
    def parse_warnings(self, drugs):
        
        # Parse the warnings data and extract warnings         
        

        warnings = []

        for drug in drugs:
            if 'warnings' in drug and drug['warnings']:
                warnings.append(drug['warnings'][0])
            else:
                warnings.append("Unknown")
        return warnings


# EXTENSION III: includes the logic to the HTML visualization.
class OpenFDAHTML():

    def build_html_list(self, result):
        
        # Build the unorder list of html from the result
        

        html_list = "<ul>"
        for item in result:
            html_list += "<li>" + item + "</li>"
        html_list += "</ul>"

        return html_list

    # EXTENSION II: 404 PAGE
    def show_page_not_found(self):
        with open("page_not_found.html") as html_file:
            return html_file.read()

        

# Refactored HTTPRequestHandler class
class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    # Handle all the GET Requests
    def do_GET(self):
        """
        All the paths will be responded by the server: /, searchDrug?drug=<drug_name>
        searchCompany?company=<company_name>, listDrugs, listcompanies_info, listWarnings
        additionally it will also keep track of limits for each of these listings
        on GET cmd
        """

        # initialize the classes objects
        client = OpenFDAClient()
        html = OpenFDAHTML()
        parser = OpenFDAParser()

        
        # generic response for any urls except the defined one
        response_code = 404
        response = html.show_page_not_found()

        if self.path == "/":
            # Return home page
            with open("index.html") as f:
                response = f.read()        
        
        if 'searchDrug' in self.path:
            active_ingredient = None
            limit = 10
            params = self.path.split("?")[1].split("&")
            for param in params:
                param_name = param.split("=")[0]
                param_value = param.split("=")[1]
                if param_name == 'active_ingredient':
                    active_ingredient = param_value
                elif param_name == 'limit':
                    limit = param_value
            result = client.search_drugs(active_ingredient, limit)
            response = html.build_html_list(parser.parse_drugs(result))
        
        elif 'listDrugs' in self.path:
            limit = None
            if len(self.path.split("?")) > 1:
                limit = self.path.split("?")[1].split("=")[1]
            result = client.list_drugs(limit)
            response = html.build_html_list(parser.parse_drugs(result))
        
        elif 'searchCompany' in self.path:
            company_name = None
            limit = 10
            params = self.path.split("?")[1].split("&")
            for param in params:
                param_name = param.split("=")[0]
                param_value = param.split("=")[1]
                if param_name == 'company':
                    company_name = param_value
                elif param_name == 'limit':
                    limit = param_value
            result = client.search_companies_info(company_name, limit)
            response = html.build_html_list(parser.parse_companies_info(result))

        elif 'listCompanies' in self.path:
            limit = None
            if len(self.path.split("?")) > 1:
                limit = self.path.split("?")[1].split("=")[1]
            result = client.list_drugs(limit)
            response = html.build_html_list(parser.parse_companies_info(result))

        # EXTENSION I: List Warnings
        elif 'listWarnings' in self.path:
            limit = None
            if len(self.path.split("?")) > 1:
                limit = self.path.split("?")[1].split("=")[1]
            result = client.list_drugs(limit)
            response = html.build_html_list(parser.parse_warnings(result))
        
        
        # Extension IV: Redirect and Authentication
        if 'secret' in self.path:
            # set response code
            response_code = 401
            # send additonal header
            self.send_header('WWW-Authenticate', ' WWW-Authenticate de basic Realm')
        elif 'redirect' in self.path:
            # set response code 
            response_code = 302
            # send redirect headers
            self.send_header('Location', 'http://localhost:8000/')

        # Send response status code
        self.send_response(response_code)

        # Send generic headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # show html response
        self.wfile.write(bytes(response, "utf8"))


Handler = testHTTPRequestHandler

httpd = socketserver.TCPServer((IP, PORT), Handler)
print("serving at port", PORT)
httpd.serve_forever()