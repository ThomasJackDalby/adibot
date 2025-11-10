import os
import datetime
import constants
import sqlalchemy
import utils
import sqlalchemy.orm
from sqlalchemy import select
from typing import Optional
from model import Base, Member, Session, SessionMember, Game, SessionGame, MemberGame

engine = sqlalchemy.create_engine(constants.CONNECTION_STRING, echo=True)
Base.metadata.create_all(engine)

class DataBaseSession:

    def __init__(self):
        self._session = sqlalchemy.orm.Session(engine)

    def __enter__(self):
        self._session.__enter__()
        return self
    
    def __exit__(self, exception_type, exception_value, exception_traceback):
        self._session.__exit__(exception_type, exception_value, exception_traceback)

# --- Session ---

    def get_sessions(self) -> list[Session]:
        """Gets all sessions from the database."""
        return self._session.scalars(select(Session)).all()

    def get_session_by_id(self, id: int) -> Optional[Session]:
        return self._session.scalars(select(Session)
            .where(Session.id == id)).first()
    
    def get_session_by_date(self, date: datetime.date) -> Session:
        """Checks the database for a session which matches the datetime."""
        return self._session.scalars(select(Session)
            .where(Session.date == date)).first()
    
    def get_or_create_session(self, current_date: datetime.date) -> Session:
        """Gets or creates a session for the provided date"""
        session = self.get_session_by_date(current_date)
        if session is None: session = self.add_session(current_date)
        return session

    def add_session(self, date: datetime.date):
        """Adds a new session to the database."""
        session = Session(date=date)
        self._session.add(session)
        self._session.commit()
        return session
    
# --- Member ---

    def get_members(self) -> list[Member]:
        """Gets all members from the database."""
        return self._session.scalars(select(Member)).all()
    
    def get_member_by_id(self, id: int) -> Optional[Member]:
        return self._session.scalars(select(Member)
            .where(Member.id == id)).first()
    
    def get_member_by_name(self, name: str) -> Optional[Member]:
        return self._session.scalars(select(Member)
            .where(Member.name == name)).first()
    
    def get_member_by_discord_name(self, discord_name: str) -> Optional[Member]:
        return self._session.scalars(select(Member)
            .where(Member.discord_name == discord_name)).first()

    def add_member(self, name: str, discord_name: str, is_admin: bool=False):
        member = Member(name=name,
                        discord_name=discord_name,
                        is_admin=is_admin)
        self._session.add(member)
        self._session.commit()
        return member
    
    def remove_member_by_id(self, id: int):
        member = self.get_member_by_id(id)
        if member is None: return False 

        self._session.remove(member)
        self._session.commit()
        return True
        
# --- SessionMember ---

    def get_session_member(self, session_id: int, member_id: int) -> Optional[SessionMember]:
        return self._session.scalars(select(SessionMember)
            .where(SessionMember.member_id == member_id)
            .where(SessionMember.session_id == session_id)).first()
        
    def get_session_members_for_session(self, session_id: int):
        return self._session.scalars(select(SessionMember)
            .where(SessionMember.session_id == session_id)).all()
    
    def get_session_members_for_member(self, member_id: int):
        return self._session.scalars(select(SessionMember)
            .where(SessionMember.member_id == member_id)).all()
    
    def get_session_member_by_id(self, session_member_id: int) -> Optional[SessionMember]:
        return self._session.scalars(select(SessionMember)
            .where(SessionMember.id == session_member_id)).first()
    
    def add_session_member(self, member_id: int, session_id: int, start: datetime.datetime, end: datetime.datetime):
        session_member = SessionMember(
            member_id = member_id,
            session_id = session_id,
            start = start,
            end = end 
        )
        self._session.add(session_member)
        self._session.commit()
        return session_member

    def add_or_update_session_member(self, session_id: int, member_id: int, start: Optional[datetime.datetime] = None, end: Optional[datetime.datetime] = None):
        if start is None and end is None: raise Exception("Cannot add or update session member if both start and end times are None.")
        session_member = self.get_session_member(member_id=member_id, session_id=session_id)
        if start is None: start = utils.get_current_or_last_session_start_date(end.date())
        if end is None: end = start
        if session_member is None:
            self.add_session_member(member_id, session_id, start=start, end=end)
        else:
            session_member.end = end
            self._session.commit()

# --- Game ---

    def get_games(self) -> list[Game]:
        """Gets all games from the database."""
        return self._session.scalars(select(Game)).all()

    def get_game_by_id(self, id: int) -> Optional[Game]:
        return self._session.scalars(select(Game)
            .where(Game.id == id)).first()
    
    def get_game_by_name(self, name: str) -> Game:
        """Checks the database for a game which matches the name."""
        return self._session.scalars(select(Game)
            .where(Game.name == name)).first()
    
    def get_or_create_game(self, name: str) -> Game:
        """Gets or creates a session for the provided date"""
        game = self.get_game_by_name(name)
        if game is None: game = self.add_game(name)
        return game
    
    def add_game(self, name: str) -> Game:
        """Adds a new game to the database."""
        game = Game(name=name)
        self._session.add(game)
        self._session.commit()
        return game
    
# --- SessionGame ---

    def get_session_game(self, session_id: int, game_id: int) -> Optional[SessionGame]:
        return self._session.scalars(select(SessionGame)
            .where(SessionGame.game_id == game_id)
            .where(SessionGame.session_id == session_id)).first()
        
    def get_session_games_for_session(self, session_id: int):
        return self._session.scalars(select(SessionGame)
            .where(SessionGame.session_id == session_id)).all()
    
    def get_session_games_for_game(self, game_id: int):
        return self._session.scalars(select(SessionGame)
            .where(SessionGame.game_id == game_id)).all()
    
    def get_session_game_by_id(self, session_game_id: int) -> Optional[SessionGame]:
        return self._session.scalars(select(SessionGame)
            .where(SessionGame.id == session_game_id)).first()
    
    def add_session_game(self, session_id: int, game_id: int, start: datetime, end: datetime):
        session_game = SessionGame(
            game_id = game_id,
            session_id = session_id,
            start = start,
            end = end 
        )
        self._session.add(session_game)
        self._session.commit()
        return session_game

    def add_or_update_session_game(self, session_id: int, game_id: int, start: Optional[datetime.datetime] = None, end: Optional[datetime.datetime] = None):
        if start is None and end is None: raise Exception("Cannot add or update session member if both start and end times are None.")
        session_game = self.get_session_game(game_id=game_id, session_id=session_id)
        if start is None: start = utils.get_current_or_last_session_start_date(end.date())
        if end is None: end = start
        if session_game is None:
            self.add_session_game(session_id, game_id, start=start, end=end)
        else:
            session_game.end = end
            self._session.commit()

# -- MemberGame --

    def get_member_game_by_member_and_game(self, member_id: int, game_id: int) -> Optional[MemberGame]:
        return self._session.scalars(select(MemberGame)
            .where(MemberGame.game_id == game_id)
            .where(MemberGame.member_id == member_id)).first()
    
    def get_member_games_for_game(self, game_id: int):
        return self._session.scalars(select(MemberGame)
            .where(MemberGame.game_id == game_id)).all()
    
    def get_member_games_for_member(self, member_id: int):
        return self._session.scalars(select(MemberGame)
            .where(MemberGame.member_id == member_id)).all()
    
    def add_member_game(self, member_id: int, game_id: int):
        member_game = MemberGame(
            member_id = member_id,
            game_id = game_id,
        )
        self._session.add(member_game)
        self._session.commit()
        return member_game
    
    def get_or_add_member_game(self, member_id: int, game_id: int) -> Game:
        member_game = self.get_member_game_by_member_and_game(member_id, game_id)
        if member_game is None: member_game = self.add_member_game(member_id, game_id)
        return member_game
