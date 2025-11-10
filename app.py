import fastapi
import fastapi.security
import pydantic
import functools
import constants
from data import DataBaseSession
from typing import Optional, Annotated

def get_auth_user(token: str = fastapi.Depends(fastapi.security.APIKeyHeader(name="token"))):
    print(f"{token=}")
    return token == constants.MASTER_API_TOKEN

public = fastapi.APIRouter(prefix="/api/v1")
authenticated = fastapi.APIRouter(prefix="/api/v1", dependencies=[fastapi.Depends(get_auth_user)])

# -- sessions

@public.get("/sessions")
async def get_sessions():
    with DataBaseSession() as db:
        return [{ 
            "id" : session.id, 
            "date" : session.date 
        } for session in db.get_sessions()]
    
@public.get("/sessions/{id}")
async def get_session_by_id(id: int):
    with DataBaseSession() as db:
        session = db.get_session_by_id(id)
        if session is None: return None

        session_members = db.get_session_members_for_session(session.id)
        session_games = db.get_session_games_for_session(session.id)

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
            "games" : [{ 
                "id" : session_game.game.id,
                "name" : session_game.game.name,
                "start" : session_game.start,
                "end" : session_game.end,
            } for session_game in session_games]
        }



# -- members

@public.get("/members")
async def get_members():
    with DataBaseSession() as db:
        return [{
                "id" : member.id,
                "name" : member.name,
                "discord_name" : member.discord_name,
            } for member in db.get_members()]

@public.get("/members/{id}")
async def get_member_by_id(id: int):
    with DataBaseSession() as db:
        member = db.get_member_by_id(id)
        if member is None: return None

        member_games = db.get_member_games_for_member(member.id)
        session_members = db.get_session_members_for_member(member.id)

        return {
            "id" : member.id,
            "name" : member.name,
            "discord_name" : member.discord_name,
            "number_of_games" : len(member_games),
            "number_of_sessions" : len(session_members),
            "games" : [{
                "id" : member_game.game.id,
                "name" : member_game.game.name,
            } for member_game in member_games],
            "sessions" : [{
                "id" : session_member.session.id,
                "date" : session_member.session.date,
                "start" : session_member.start,
                "end" : session_member.end,
                "duration" : session_member.get_duration(),
            } for session_member in session_members]
        }

class PostMemberRequest(pydantic.BaseModel):
    name: str
    discord_name: str
    is_admin: bool | None = None

@authenticated.post("/members")
async def post_members(request: PostMemberRequest):
    with DataBaseSession() as db:
        member = db.get_member_by_discord_name(request.discord_name)
        if member is not None: raise fastapi.HTTPException(status_code=400, detail=f"Member with discord_name [{request.discord_name}] already exists.")  
        db.add_member(request.name, request.discord_name, request.is_admin if request.is_admin is not None else False)

# -- games

@public.get("/games")
async def get_games():
    with DataBaseSession() as db:
        return [{
                "id" : game.id,
                "name" : game.name,
            } for game in db.get_games()]
    
@public.get("/games/{id}")
async def get_game_by_id(id: int):
    with DataBaseSession() as db:
        game = db.get_game_by_id(id)
        if game is None: return None

        member_games = db.get_member_games_for_game(game.id)
        session_games = db.get_session_games_for_game(game.id)

        return {
            "id" : game.id,
            "name" : game.name,
            "number_of_members" : len(member_games),
            "number_of_sessions" : len(session_games),
            "members" : [{
                "id" : member_game.member.id,
                "name" : member_game.member.name,
            } for member_game in member_games],
            "sessions" : [{
                "id" : session_game.session.id,
                "date" : session_game.session.date,
                "start" : session_game.start,
                "end" : session_game.end,
                "duration" : session_game.get_duration(),
            } for session_game in session_games]
        }

app = fastapi.FastAPI()
app.include_router(public)
app.include_router(authenticated)
