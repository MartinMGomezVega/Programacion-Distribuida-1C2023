import json
import requests

api_url = "https://jsonplaceholder.typicode.com/todos"
todo = {"userId": 1, "title": "Buy milk", "completed": False}
# response = requests.post(api_url, json=todo)
headers =  {"Content-Type":"application/json"}
response = requests.post(api_url, data=json.dumps(todo), headers=headers)
print(response.json())
print(response.status_code)
print(response.headers["Content-Type"])