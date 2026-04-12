import math
import random
import os
import datetime
import requests

# generate members
# generate games
# games = []
# generate sessions

# for each session

# members 
# games
# pick a number of games for the session
# subdivide the time into that number of slots

DATA_FOLDER_PATH = os.path.dirname(__file__)

AVG_SESSION_START = datetime.time(20)
AVG_SESSION_END = datetime.time(22)

MIN_GAMES = 1
MAX_GAMES = 5
MIN_MEMBERS = 2
MAX_MEMBERS = 8
NUMBER_OF_SESSIONS = 200

MEMBERS = [
    "dalbington",
    "burwellish",
    "adibob88",
    "alexzerouk",
    "shlee53",
    "sonicreaction",
    "spaceg00se",
    "revdgoldfish",
    "monkeynuts_",
    "uberg00ber",
    "marksimus0",
]

API_URL = "http://localhost:8000/api/v1"
API_TOKEN = "k235bk1jb35lj3524535kjb"

api_session = requests.Session()
api_session.headers = { "token": API_TOKEN }

def post(url: str, data: dict):
    response = api_session.post(f"{API_URL}/{url}", json=data)
    if response.status_code != 201 and response.status_code != 400: raise Exception(response.text)
    return response.json()

def random_timedelta(min_value, max_value) -> datetime.timedelta:
    minutes = int(math.floor(random.random() * (max_value - min_value) + min_value))
    return datetime.timedelta(seconds=minutes*60)

def upload_members() -> list[int]:
    file_path = os.path.join(DATA_FOLDER_PATH, "members.csv")
    member_ids = []
    with open(file_path, "r") as file:
        lines = [line.strip() for line in file.readlines()][1:]
        for line in lines:
            discord_name, name = line.split(",")
            member_id = post("members", {
                "name": name,
                "discord_name": discord_name,
            })
            member_ids.append(member_id)
    return member_ids

def upload_games() -> list[int]:
    file_path = os.path.join(DATA_FOLDER_PATH, "games.csv")
    game_ids = []
    with open(file_path, "r") as file:
        lines = [line.strip() for line in file.readlines()][1:]
        for name in lines:
            game_id = post("games", {
                "name": name
            })
            game_ids.append(game_id)
    return game_ids

def generate_session(session_date: datetime.date, member_ids: list[int], game_ids: list[int]):
    session_id = post("sessions", { "date": session_date.strftime("%d/%m/%Y") })

    session_start = datetime.datetime(session_date.year, session_date.month, session_date.day, AVG_SESSION_START.hour, AVG_SESSION_START.minute) + random_timedelta(-60, 60)
    session_end = datetime.datetime(session_date.year, session_date.month, session_date.day, AVG_SESSION_END.hour, AVG_SESSION_END.minute) + random_timedelta(-60, 60)
    print(f"{session_end=}")

    session_duration_s = session_end - session_start
    session_duration_m = int(session_duration_s.seconds / 60)
    print(f"{session_duration_m=}")

    number_of_session_games = random.randint(MIN_GAMES, MAX_GAMES)
    game_sessions = distribute(session_duration_m, number_of_session_games)
    print(f"{number_of_session_games=}")
    print(f"{game_sessions=}")

    # select members for session
    available_member_ids = list(member_ids)
    session_members = []
    number_of_members = random.randint(MIN_MEMBERS, MAX_MEMBERS)
    for _ in range(number_of_members):
        member_id = random.choice(available_member_ids)
        available_member_ids.remove(member_id)
        session_member_start = session_start + random_timedelta(0, 30)
        session_member_end = session_end + random_timedelta(-30, 0)
        session_member_id = post(f"sessions/{session_id}/members",{
            "member_id" : member_id,
            "start" : session_member_start.strftime("%d/%m/%Y %H:%M:%S"),
            "end" : session_member_end.strftime("%d/%m/%Y %H:%M:%S"),
        })
        session_members.append((member_id, [(session_member_id, session_member_start, session_member_end)]))

    # add games to the session
    available_game_ids = list(game_ids) 
    min_game_session_start = session_start
    for max_game_session_length in game_sessions:
        max_game_session_end = min_game_session_start + datetime.timedelta(seconds=max_game_session_length*60)
        game_id = random.choice(available_game_ids)
        available_game_ids.remove(game_id)
        
        print(f"{game_id=}")
        print(f"{min_game_session_start=}")
        print(f"{max_game_session_end=}")

        # for members which are online, they start playing this game with a random delay
        for member_id, member_sessions in session_members:
            for session_member_id, session_member_start, session_member_end in member_sessions:
                if (session_member_start < max_game_session_end and 
                    session_member_end > min_game_session_start):
                    member_game_session_start = max(min_game_session_start, session_member_start)
                    member_game_session_end = min(max_game_session_end, session_member_end)
                    print(f"{member_game_session_start=}")
                    print(f"{member_game_session_end=}")

                    post(f"sessions/{session_id}/members/{session_member_id}",{
                        "game_id" : game_id,
                        "start" : member_game_session_start,
                        "end" : member_game_session_end,
                    })
        min_game_session_start = max_game_session_end

def distribute(value, number_of_chunks, max_chunk_size=1):
    result = [1] * number_of_chunks
    value -= number_of_chunks
    while value > 0:
        amount = min(value, random.randint(1, max(number_of_chunks, max_chunk_size)))
        i = random.randint(0, number_of_chunks-1)
        result[i] += amount
        value -= amount
    return result

if __name__ == "__main__":

    member_ids = upload_members()
    game_ids = upload_games()
    generate_session(datetime.date(2026, 1, 1), member_ids, game_ids)