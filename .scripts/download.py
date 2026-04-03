import requests
import json
import datetime

API_URL = "http://localhost:8000/api/v1"
API_TOKEN = "hjf53jhg45fj31lkj4h"
TABLE_NAMES = [
    "members",
    "sessions",
    "games",
    "session_members",
    "session_games",
    "member_games",
]

def download_table(table_name):
    response = requests.get(f"{API_URL}/export?table_name={table_name}", headers={"token": API_TOKEN})
    if response.status_code != 200: raise Exception()
    with open(f"export.{table_name}.csv", "w") as file:
        file.write(response.text)
        file.flush()

if __name__ == "__main__":
    for table_name in TABLE_NAMES:
        download_table(table_name)