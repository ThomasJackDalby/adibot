import requests
import json
import datetime

API_URL = "http://192.168.0.100:8000/api/v1"
API_TOKEN = "hjf53jhg45fj31lkj4h"

# data = {'input': open('export.members.csv','rb')}

# r = requests.post(f"{API_URL}/import", headers={"token": API_TOKEN}, data=data)
# print(r)
# print(r.text)
# print(r.json())

# with open("legacy.csv", "r") as file:
#     lines = [line.strip() for line in file.readlines()]
#     for line in lines:
#         date, gm = line.split("\t")
#         print(date, gm)

#         requests.post(f"{API_URL}/sessions", json={

#         })

def upload_members(file_path):
    with open(file_path, "r") as file:
        lines = [line.strip() for line in file.readlines()][1:]
        for line in lines:
            discord_name, name = line.split(",")
            response = requests.post(
                f"{API_URL}/members", 
                json={ 
                    "name": name,
                    "discord_name": discord_name
                },
                headers={ "token": API_TOKEN })
            print(f"Uploaded {name} [{discord_name}] : {response.json()}")

upload_members("members.csv")
print(requests.get(f"{API_URL}/sessions", headers={"token": API_TOKEN}))