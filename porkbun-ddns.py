import json
import requests
import re
import sys

def getRecord(domain, subdomain=""): #grabs the record for the specified sub/domain
	allRecords=json.loads(requests.post(apiConfig["endpoint"] + '/dns/retrieve/' + domain, data = json.dumps(apiConfig)).text)
	if allRecords["status"]=="ERROR":
		print('Error getting domain. Check to make sure you specified the correct domain, and that API access has been switched on for this domain.');
		sys.exit();
	for i in allRecords["records"]:
		if i["name"]==fqdn and (i["type"] == 'A' or i["type"] == 'ALIAS' or i["type"] == 'CNAME'):
			record = i
			return(record)

def getMyIP():
	ping = json.loads(requests.post(apiConfig["endpoint"] + '/ping/', data = json.dumps(apiConfig)).text)
	return(ping["yourIp"])

def editRecord():
	i = getRecord(rootDomain, subDomain)
	print("Checking", i['name'])
	if i["content"] == myIP:
		print("IP is the same, not changing anything")
	else:
		print("Editing existing " + i["type"] + " Record with " + myIP)
		createObj=apiConfig.copy()
		createObj.update({'content': myIP, 'ttl': i['ttl'], 'type': i["type"]})
		editRecord = json.loads(requests.post(apiConfig["endpoint"] + '/dns/edit/' + rootDomain + "/" + i["id"], data = json.dumps(createObj)).text)
		print(editRecord['status'])

if len(sys.argv)>2: #at least the config and root domain is specified
	apiConfig = json.load(open(sys.argv[1])) #load the config file into a variable
	rootDomain=sys.argv[2].lower()
		
	if len(sys.argv)>3 and sys.argv[3]!='-i': #check if a subdomain was specified as the third argument
		subDomain=sys.argv[3].lower()
		fqdn=subDomain + "." + rootDomain
	else:
		subDomain=''
		fqdn=rootDomain

	if len(sys.argv)>4 and sys.argv[3]=='-i': #check if IP is manually specified. There's probably a more-elegant way to do this
		myIP=sys.argv[4]
	elif len(sys.argv)>5 and sys.argv[4]=='-i':
		myIP=sys.argv[5]
	else:
		myIP=getMyIP() #otherwise use the detected exterior IP address
	
	editRecord()
	
else:
	print("Porkbun Dynamic DNS client, Python Edition\n\nError: not enough arguments. Examples:\npython porkbun-ddns.py /path/to/config.json example.com\npython porkbun-ddns.py /path/to/config.json example.com www\npython porkbun-ddns.py /path/to/config.json example.com '*'\npython porkbun-ddns.py /path/to/config.json example.com -i 10.0.0.1\n")
