import constants
import datetime
import fastapi
import fastapi.responses
import fastapi.security
import fastapi.staticfiles
import fastapi.middleware.cors
import logging
import model
import os
from data import DataBaseSession
import dotenv
import uvicorn
import asyncio
import data
from schemas import (
    PostSessionRequest,
    PutSessionRequest,
    PostGamesRequest,
    PostMemberRequest,
    PostSessionMemberRequest
)

logger = logging.getLogger("adibot")

MASTER_API_TOKEN = os.environ['MASTER_API_TOKEN']

def get_auth_user(token: str = fastapi.Depends(fastapi.security.APIKeyHeader(name="token"))):
    logger.debug(f"token: {token} vs {MASTER_API_TOKEN}")
    return token == MASTER_API_TOKEN

public = fastapi.APIRouter(prefix="/api/v1")
authenticated = fastapi.APIRouter(prefix="/api/v1", dependencies=[fastapi.Depends(get_auth_user)])

# -- sessions

@public.get("/sessions")
async def get_sessions(date_str: str | None = None):
    with DataBaseSession() as db:
        if date_str is None:
            return [{ 
                "id" : session.id, 
                "date" : session.date 
            } for session in db.get_sessions()]
        else:
            date = datetime.datetime.strptime(date_str, "%d/%m/%Y").date()
            return [db.get_session_with_date(date)]
    
@public.get("/sessions/{session_id}")
async def get_session_by_id(session_id: int):
    with DataBaseSession() as db:
        session = db.get_session_with_id(session_id)
        if session is None: raise fastapi.HTTPException(status_code=403, detail=f"No session with id [{session_id}] exists.")
        games_master = db.get_member_with_id(session.games_master_id) if session.games_master_id is not None else None
        session_members = db.get_session_members_for_session(session.id)

        members = db.get_members_for_session(session_id)
        games = db.get_games_for_session(session_id)

        return {
            "id" : session.id,
            "date" : session.date,
            "gamesMaster" : games_master.name if games_master is not None else None,
            "members" : [{"id" : member.id, "name": member.name, "discordName" : member.discord_name } for member in members],
            "games" : [{"id" : game.id, "name": game.name } for game in games]
        }
    
@public.get("/sessions/{session_id}/full")
async def get_session_by_id_full(session_id: int):
    with DataBaseSession() as db:
        session = db.get_session_with_id(session_id)
        if session is None: raise fastapi.HTTPException(status_code=403, detail=f"No session with id [{session_id}] exists.")
        games_master = db.get_member_with_id(session.games_master_id) if session.games_master_id is not None else None

        return {
            "id" : session.id,
            "date" : session.date,
            "gamesMaster" : games_master.name if games_master is not None else None,
            "members" : [{
                "id" : session_member.id,
                "memberId" : session_member.member.id,
                "memberName": session_member.member.name,
                "discordName" : session_member.member.discord_name,
                "start" : session_member.start,
                "end" : session_member.end,
                "games" : [{
                    "id" : session_member_game.id,
                    "gameId" : session_member_game.game.id,
                    "gameName" : session_member_game.game.name,
                    "start" : session_member.start,
                    "end" : session_member.end,
                    } for session_member_game in session_member.session_member_games]
                } for session_member in session.session_members],
        }

@authenticated.post("/sessions", status_code=201)
async def post_sessions(request: PostSessionRequest):
    with DataBaseSession() as db:
        date = datetime.datetime.strptime(request.date, "%d/%m/%Y").date()

        session = db.get_session_with_date(date)
        if session is not None: raise fastapi.HTTPException(status_code=403, detail=f"session with date [{date}] already exists.")  
        session = db.add_session_with_date(date)
        if session is None: raise fastapi.HTTPException(status_code=500, detail=f"Unable to add session to the database.")    
        return session.id

@authenticated.put("/sessions/{session_id}", status_code=200)
async def put_session(request: PutSessionRequest, session_id: int):
    with DataBaseSession() as db:
        session = db.get_session_with_id(session_id)
        if session is None: raise fastapi.HTTPException(status_code=403, detail=f"No session with id [{session_id}] exists.")

        if request.date is not None: session.date = datetime.datetime.strptime(request.date, "%d/%m/%Y")
        if request.games_master_id is not None:
            member = db.get_member_with_id(request.games_master_id)
            if member is None: raise fastapi.HTTPException(status_code=403, detail=f"No member with id [{request.games_master_id}] exists.")
            session.games_master_id = member.id
            db._session.commit()

def _format_session_member(session_member: model.SessionMember):
    return {
        "member_id" : session_member.member.id,
        "member_name" : session_member.member.name,
        "start" : session_member.start,
        "end" : session_member.end,
        "games" : [_format_session_member_game(session_member_game) for session_member_game in session_member.session_member_games],
    }

def _format_session_member_game(session_member_game: model.SessionMemberGame):
    return {
        "game_id" : session_member_game.game.id,
        "game_name" : session_member_game.game.name,
        "start" : session_member_game.start,
        "end" : session_member_game.end,
    }

# -- session-members
@public.get("/sessions/{session_id}/members")
async def get_session_members(session_id: int):
    with DataBaseSession() as db:
        return [_format_session_member(session_member) for session_member in db.get_session_members_for_session(session_id)]

@authenticated.post("/sessions/{session_id}/members", status_code=201)
async def post_session_members(session_id: int, request: PostSessionMemberRequest):
    with DataBaseSession() as db:
        session = db.get_session_with_id(session_id)
        if session is None: raise fastapi.HTTPException(status_code=403, detail=f"No session with id [{session_id}] exists.")  

        member = db.get_member_with_id(request.member_id)
        if member is None: raise fastapi.HTTPException(status_code=400, detail=f"No member with id [{request.member_id}] exists.")
         
        start = datetime.datetime.strptime(request.start, "%d/%m/%Y %H:%M:%S")
        end = datetime.datetime.strptime(request.end, "%d/%m/%Y %H:%M:%S")

        session_member = db.add_session_member(session.id, member.id, start, end)
        if session_member is None: raise fastapi.HTTPException(status_code=500, detail=f"Unable to add session_member to the database.")    
        return session_member.id
    
# -- session-member-games

@authenticated.post("/sessions/{session_id}/members/{member_id}/", status_code=201)
async def post_session_member_games(session_id: int, request: PostSessionMemberRequest):
    with DataBaseSession() as db:
        session = db.get_session_with_id(session_id)
        if session is None: raise fastapi.HTTPException(status_code=403, detail=f"No session with id [{session_id}] exists.")  

        member = db.get_member_with_id(request.member_id)
        if member is None: raise fastapi.HTTPException(status_code=400, detail=f"No member with id [{request.member_id}] exists.")
         
        start = datetime.datetime.strptime(request.start, "%d/%m/%Y %H:%M:%S")
        end = datetime.datetime.strptime(request.end, "%d/%m/%Y %H:%M:%S")
        # check before/after?

        session_member = db.add_session_member(session.id, member.id, start, end)
        if session_member is None: raise fastapi.HTTPException(status_code=500, detail=f"Unable to add session_member to the database.")    
        return session_member.id


# -- session-games

# @public.get("/sessions/{session_id}/games")
# async def get_session_games(session_id: int):
#     with DataBaseSession() as db:
#         return [_format_session_game(session_game) for session_game in db.get_session_games_for_session(session_id)]

# class PostSessionGameRequest(pydantic.BaseModel):
#     game_id: int
#     start: str
#     end: str

# @authenticated.post("/sessions/{session_id}/games", status_code=201)
# async def post_session_games(session_id: int, request: PostSessionGameRequest):
#     with DataBaseSession() as db:
#         session = db.get_session_by_id(session_id)
#         if session is None: raise fastapi.HTTPException(status_code=403, detail=f"No session with id [{session_id}] exists.")  

#         game = db.get_game_by_id(request.game_id)
#         if game is None: raise fastapi.HTTPException(status_code=400, detail=f"No game with id [{request.member_id}] exists.")
         
#         start = datetime.datetime.strptime(request.start, "%d/%m/%Y %H:%M:%S")
#         end = datetime.datetime.strptime(request.end, "%d/%m/%Y %H:%M:%S")
#         # check before/after?

#         session_game = db.add_session_game(session.id, game.id, start, end)
#         if session_game is None: raise fastapi.HTTPException(status_code=500, detail=f"Unable to add session_game to the database.")    
#         return session_game.id

# -- members

@public.get("/members")
async def get_members():

    def format(member):
        last_gm_session = db.get_last_games_master_session_for_member_by_id(member.id)
        today = datetime.datetime.today().date()
        return {
            "id" : member.id,
            "name" : member.name,
            "discord_name" : member.discord_name,
            "games_master_count" : db.get_games_master_count_for_member_by_id(member.id),
            "total_attendance" : db.get_total_attendance_for_member_by_id(member.id),
            "last_games_master_session_id" : last_gm_session.id if last_gm_session is not None else None,
            "last_games_master_session_date" : last_gm_session.date if last_gm_session is not None else None,
            "days_since_gm" : (today - last_gm_session.date).days if last_gm_session is not None else None,
        }
    
    with DataBaseSession() as db:
        return [format(member) for member in db.get_members()]

@public.get("/members/{member_id}")
async def get_member_by_id(member_id: int):
    with DataBaseSession() as db:
        member = db.get_member_with_id(member_id)
        if member is None: return None

        # TODO: Compile list of all games that member has played
        member_games = db.get_games_for_member(member.id)
        session_members = db.get_session_members_for_member(member.id)
        last_gm_session = db.get_last_games_master_session_for_member_by_id(member.id)

        return {
            "id" : member.id,
            "name" : member.name,
            "discord_name" : member.discord_name,
            "games_master_count" : db.get_games_master_count_for_member_by_id(member.id),
            "last_games_master_session_id" : last_gm_session.id if last_gm_session is not None else None,
            "last_games_master_session_date" : last_gm_session.date if last_gm_session is not None else None,
            "days_since_gm" : (datetime.datetime.today().date() - last_gm_session.date).days if last_gm_session is not None else None,
            # "number_of_games" : len(member_games),
            "number_of_sessions" : len(session_members),
            # "games" : [{
            #     "id" : member_game.game.id,
            #     "name" : member_game.game.name,
            # } for member_game in member_games],
            "sessions" : [{
                "id" : session_member.session.id,
                "date" : session_member.session.date,
                "start" : session_member.start,
                "end" : session_member.end,
                "duration" : session_member.get_duration(),
            } for session_member in session_members]
        }

@authenticated.post("/members", status_code=201)
async def post_members(request: PostMemberRequest):
    with DataBaseSession() as db:
        member = db.get_member_by_discord_name(request.discord_name)
        if member is not None: raise fastapi.HTTPException(status_code=400, detail=f"Member with discord_name [{request.discord_name}] already exists.")  
        member = db.add_member(request.name, request.discord_name, request.is_admin if request.is_admin is not None else False)
        return member.id

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

        member_games = []
        session_games = []

        # TODO: Sort this
        # member_games = db.get_member_games_for_game(game.id)
        # session_games = db.get_session_games_for_game(game.id)

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

@authenticated.post("/games", status_code=201)
async def post_games(request: PostGamesRequest):
    with DataBaseSession() as db:
        game = db.get_game_by_name(request.name)
        if game is not None: raise fastapi.HTTPException(status_code=400, detail=f"Game with name [{request.name}] already exists.")  
        db.add_game(request.name)

# -- stats

@public.get("/games-master-succession")
async def get_games_master_succession():
    with DataBaseSession() as db:
        today = datetime.datetime.today().date()
        
        def format(member):
            last_gm_session = db.get_last_games_master_session_for_member_by_id(member.id)
            days_since_gm = (today - last_gm_session.date).days if last_gm_session is not None else -1
            return { 
                "member_id" : member.id,
                "member_name" : member.name,
                "days_since_gm" : days_since_gm
            }
        return list(sorted((format(member) for member in db.get_members() if member.in_rotation == True), key=lambda item: item["days_since_gm"], reverse=True))

# -- export

@public.get("/export")
async def export_table(table_name: str):
    with DataBaseSession() as db:
        table = db.get_table_from_name(table_name)
        if table is None: raise fastapi.HTTPException(status_code=400, detail=f"No table with name {table_name} exists.") 
        file_data = _create_table_csv_file_data(table, db.get_rows(table))
        return fastapi.responses.Response(file_data, headers={'Content-Disposition': f'filename="{table_name}.csv"'}, media_type="text/csv")

def _create_table_csv_file_data(table, table_data) -> str:
    lines = []
    lines.append(",".join((column.name for column in table.columns)))
    for row in table_data:
        lines.append(",".join((str(c) for c in row)))
    return "\n".join(lines)

@public.post("/import")
async def import_table(files: list[fastapi.UploadFile]):
    return {"filenames": [file.filename for file in files]}
    # with DataBaseSession() as db:
        # table = db.get_table_from_name(table_name)
        # if table is None: raise fastapi.HTTPException(status_code=400, detail=f"No table with name {table_name} exists.") 
        
app = fastapi.FastAPI()
app.include_router(public)
app.include_router(authenticated)
app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
static_path = os.environ["STATIC_PATH"]
app.mount("/", fastapi.staticfiles.StaticFiles(directory=static_path, html = True), name="static")

async def main():
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8000, log_config=None)
    server = uvicorn.Server(config=config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())