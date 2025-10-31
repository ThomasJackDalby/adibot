from data import DataBaseSession
from fastapi import FastAPI

app = FastAPI()

@app.get("/sessions")
async def get_sessions():
    with DataBaseSession() as db:
        return [{ 
            "id" : session.id, 
            "date" : session.date 
        } for session in db.get_sessions()]

@app.get("/members")
async def get_members():
    with DataBaseSession() as db:
        return [{
                "id" : member.id,
                "name" : member.name,
                "discord_name" : member.discord_name,
            } for member in db.get_members()]

@app.get("/members/{id}")
async def get_member_by_id(id: int):
    with DataBaseSession() as db:
        member = db.get_member_by_id(id)
        if member is None: return None

        return {
            "id" : member.id,
            "name" : member.name,
            "discord_name" : member.discord_name,
        }
    
@app.get("/sessions/{id}")
async def get_session_by_id(id: int):
    with DataBaseSession() as db:
        session = db.get_session_by_id(id)
        if session is None: return None

        session_members = db.get_session_members_for_session(session.id)
        return {
            "id" : session.id,
            "date" : session.date,
            "games_master" : None,
            "members" : [{ 
                "id" : session_member.member.id,
                "name" : session_member.member.name,
                "start" : session_member.start,
                "end" : session_member.end,
            } for session_member in session_members],
            "games" : None
        }