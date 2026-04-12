import pydantic
import datetime

class PostSessionRequest(pydantic.BaseModel):
    date: str

class PutSessionRequest(pydantic.BaseModel):
    date: str | None = None
    games_master_id: int | None = None

class PostSessionMemberRequest(pydantic.BaseModel):
    member_id: int
    start: str 
    end: str

class PostMemberRequest(pydantic.BaseModel):
    name: str
    discord_name: str
    is_admin: bool | None = None
    last_games_master_session_date: datetime.date | None

class PostGamesRequest(pydantic.BaseModel):
    name: str