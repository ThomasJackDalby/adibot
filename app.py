import data
from fastapi import FastAPI
from model import Member

app = FastAPI()

@app.get("/sessions")
async def get_sessions():
    return [{ "id" : session.id, "date" : session.date } for session in data.get_sessions()]

@app.get("/members")
async def get_members():
    return [{
            "id" : member.id,
            "name" : member.name,
            "discord_name" : member.discord_name,
        } for member in data.get_members()]

@app.get("/members/{id}")
async def get_member_by_id(id: int):
    member = data.get_member_by_id(id)
    if member is None: return None
    return _format_member(member)

def _format_member(member: Member):
    return {
            "id" : member.id,
            "name" : member.name,
            "discord_name" : member.discord_name,
        }