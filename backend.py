import requests

url = "https://apis.openapi.sk.com/transit/routes"

payload = {
    "startX": "126.926493082645",
    "startY": "37.6134436427887",
    "endX": "127.126936754911",
    "endY": "37.5004198786564",
    "lang": 0,
    "format": "json",
    "count": 10,
    "searchDttm": "202301011200"
}
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "appKey": "YEWVxfrK4j8xTNQZURJ4z1Te4JTZs26v45fgmfn7"
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)