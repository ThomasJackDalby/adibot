# generate.py - Generates fake data for test purposes.

import requests
import datetime
import random

# for each session
# decide randomly who will turn up, and at what times
# decide what they will play
# upload it

NUMBER_OF_SESSIONS = 200
API_URL = "http://localhost:8000/api/v1"
API_TOKEN = "hjf53jhg45fj31lkj4h"

api_session = requests.Session()
api_session.headers = { "token": API_TOKEN }

# upload members
with open("members.csv", "r") as file:
    lines = [line.strip() for line in file.readlines()][1:]
    for line in lines:
        discord_name, name = line.split(",")
        response = api_session.post(f"{API_URL}/members", json={
            "name": name,
            "discord_name": discord_name,
        })
        
        if response.status_code != 201 and response.status_code != 400: raise Exception(response.text)

response = api_session.get(f"{API_URL}/members")
if response.status_code != 200: raise Exception()
members = response.json()

# upload games
with open("games.csv", "r") as file:
    lines = [line.strip() for line in file.readlines()][1:]
    for line in lines:
        name = line
        response = api_session.post(f"{API_URL}/games", json={
            "name": name,
        })
        if response.status_code != 201: raise Exception(f"{response.status_code} {response.text}")

response = api_session.get(f"{API_URL}/games")
if response.status_code != 200: raise Exception(f"{response.status_code} {response.text}")
games = response.json()

session_date = datetime.datetime.today()
while session_date.weekday() != 4:
        session_date -= datetime.timedelta(days=1)

for session_index in range(NUMBER_OF_SESSIONS):
    print(f"Requesting: {session_date.strftime("%d/%m/%Y")}")
    response = api_session.post(f"{API_URL}/sessions", json={
        "date": session_date.strftime("%d/%m/%Y")
    })
    if response.status_code != 201: raise Exception(f"{response.status_code} {response.text}")

    session_id = response.json()
    print(f"session id is..:{session_id}")

    session_start_time = datetime.datetime.combine(session_date, datetime.time(18, 0, 0))
    session_end_time = datetime.datetime.combine(session_date + datetime.timedelta(days=1), datetime.time(3, 0, 0))

    def get_start_end(origin, delay, duration):
        delay = datetime.timedelta(minutes=random.randint(0, delay))
        duration = datetime.timedelta(minutes=random.randint(0, duration))
        start = origin + delay
        end = start + duration
        if end > session_end_time: end = session_end_time
        return start, end

    # pick some members
    earliest_start = session_end_time
    latest_end = session_start_time
    potential_session_members = list(members)
    session_members = []
    number_of_members = random.randint(1, len(potential_session_members))

    for _ in range(number_of_members):
        member = random.choice(potential_session_members)
        potential_session_members.remove(member)
        session_members.append(member)

        start, end = get_start_end(session_start_time, 120, 240)
        if start < earliest_start: earliest_start = start
        if end > latest_end: latest_end = end

        response = api_session.post(f"{API_URL}/sessions/{session_id}/members", json={
            "member_id" : member["id"],
            "start" : start.strftime("%d/%m/%Y %H:%M:%S"),
            "end" : end.strftime("%d/%m/%Y %H:%M:%S"),
        })
        if response.status_code != 201: raise Exception(f"{response.status_code} {response.text}")

    games_master = random.choice(session_members)
    response = api_session.put(f"{API_URL}/sessions/{session_id}", json={
            "games_master_id" : games_master["id"],
        })
    if response.status_code != 200: raise Exception(f"{response.status_code} {response.text}")

    session_start_time = earliest_start
    session_end_time = latest_end

    # play some games
    earliest_game_start_time = session_start_time
    while earliest_game_start_time < session_end_time:
        game = random.choice(games)
        start, end = get_start_end(earliest_game_start_time, 30, 120)

        # need to add this game for each member, within a session they're in
        


        response = api_session.post(f"{API_URL}/sessions/{session_id}/games", json={
            "game_id" : game["id"],
            "start" : start.strftime("%d/%m/%Y %H:%M:%S"),
            "end" : end.strftime("%d/%m/%Y %H:%M:%S"),
        })
        if response.status_code != 201: raise Exception(f"{response.status_code} {response.text}")

        earliest_game_start_time = end

    session_date -= datetime.timedelta(days=7)