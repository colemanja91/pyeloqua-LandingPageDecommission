##### This is a test to see if we can update a landing page to redirect for the purpose of decomissioning

import requests
import os
import json
from pyeloqua import Eloqua
from copy import deepcopy
from csv import DictWriter

## Get asset IDs

ids = []

with open('test.csv') as f:
    for row in f:
        ids.append(str(row).replace('\n', ''))

## setup new Eloqua session
elq = Eloqua(username=os.environ['ELOQUA_USER'], password=os.environ['ELOQUA_PASSWORD'], company=os.environ['ELOQUA_COMPANY'])

results = []

success = 0
failure = 0
current = 0

for row in ids:

    assetId = row
    current += 1
    print(current)

    resultRow = {}
    resultRow['assetId'] = assetId

    url = elq.restBase + "assets/landingPage/" + assetId

    getAsset = requests.get(url, auth=elq.auth)

    if getAsset.status_code==200:

        data = getAsset.json()

        ## Backup config

        dataCopy = deepcopy(data)

        dataCopyHTML = dataCopy['htmlContent']['html']

        with open("./archive/json/" + assetId + ".json", "w") as f:
            f.write(json.dumps(dataCopy))

        with open("./archive/html/" + assetId + ".html", "w") as f:
            f.write(dataCopyHTML)

        data['autoRedirectUrl'] = 'http://www.redirecttest.com'
        data['autoRedirectWaitFor'] = 1

        req = requests.put(url, auth=elq.auth, json=data)

        if req.status_code==200:
            print(assetId + ": Success!")
            resultRow['redirectPUT'] = 'success'
            success += 1
        else:
            print(assetId + ": Fail!")
            resultRow['redirectPUT'] = 'failure'
            failure += 1

        resultRow['assetStatus'] = ''

    else:
        print("Asset " + assetId + " not found")
        resultRow['assetStatus'] = 'not found'
        resultRow['redirectPUT'] = ''
        failure += 1

    results.append(resultRow)

print('total: ' + str(current))
print('success: ' + str(success))
print('failure: ' + str(failure))
print('writing by-asset results to csv')

with open('redirect_results.csv', 'w') as f:
    csvwriter = DictWriter(f, fieldnames=results[0].keys())
    csvwriter.writeheader()
    for row in results:
        csvwriter.writerow(row)
