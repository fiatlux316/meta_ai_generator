import requests
import json


total_body = {
    "type": "messageCard",
    "attachments": [
        {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "msteams": {
                    "width": "Full"
                },
                "version": "1.2",
                "body": []
            }
        }
    ]
}

url = "https://prod2-27.southeastasia.logic.azure.com:443/workflows/cdc325994d9d476a817b93deea646bdf/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=ElgT6FQ81IpAxlLqFj-R4LymUI0Vrm9fq2RQF0tBDuc"
headers = {"Content-Type": "application/json"}
json_data = json.dumps(total_body)
response = requests.post(url, data=json_data, headers=headers)
print(response.text)