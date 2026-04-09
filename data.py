import os
import datetime
import constants
import sqlalchemy
import dotenv
import utils
import logging
import sqlalchemy.orm
from sqlalchemy import select
from typing import Optional
from model import Base, Session, Member, Game, SessionMember, SessionMemberGame

logger = logging.getLogger("adibot")

if os.path.exists(".env"): logger.info("Loading env variables from .env file.")
dotenv.load_dotenv()

CONNECTION_STRING = os.environ["CONNECTION_STRING"]
_engine = None

def create_engine():
    global _engine
    logger.debug("Creating SQL engine.")
    _engine = sqlalchemy.create_engine(CONNECTION_STRING)
    Base.metadata.create_all(_engine)

class DataBaseSession:

    def __init__(self):
        global _engine
        if _engine is None: create_engine()
        self._session = sqlalchemy.orm.Session(_engine)

    def __enter__(self):
        self._session.__enter__()
        return self
    
    def __exit__(self, exception_type, exception_value, exception_traceback):
        self._session.__exit__(exception_type, exception_value, exception_traceback)

# --- Session ---

    def get_sessions(self) -> list[Session]:
        """Gets all sessions from the database."""
        return list(self._session.scalars(select(Session)).all())

    def get_session_with_id(self, id: int) -> Optional[Session]:
        """Gets a session with the id, otherwise returns None."""
        return self._session.scalars(select(Session)
            .where(Session.id == id)).first()
    
    def get_session_with_date(self, date: datetime.date) -> Session | None:
        """Gets a session for the provided date, otherwise returns None."""
        return self._session.scalars(select(Session)
            .where(Session.date == date)).first() 
    
    def get_or_create_session_with_date(self, current_date: datetime.date) -> Session:
        """Gets or creates a session for the provided date."""
        session = self.get_session_with_date(current_date)
        if session is None: session = self.add_session_with_date(current_date)    
        return session

    def add_session_with_date(self, date: datetime.date):
        """Adds a new session to the database."""
        session = Session(date=date)
        self._session.add(session)
        self._session.commit()
        return session
    
# --- Member ---

    def get_members(self) -> list[Member]:
        """Gets all members from the database."""
        return list(self._session.scalars(select(Member)).all())
    
    def get_members_for_session(self, session_id: int) -> list[Member]:
        return list(self._session.scalars(select(Member)
            .join(SessionMember)
            .where(SessionMember.session_id == session_id))
            .all())

    def get_member_with_id(self, id: int) -> Member | None:
        """Gets a member with the id, otherwise returns None."""
        return self._session.scalars(select(Member)
            .where(Member.id == id)).first()
    
    def get_member_by_name(self, name: str) -> Member | None:
        """Gets a member with the name, otherwise returns None."""
        return self._session.scalars(select(Member)
            .where(Member.name == name)).first()
    
    def get_member_by_discord_name(self, discord_name: str) -> Member | None:
        """Gets a member with the discord name, otherwise returns None."""
        return self._session.scalars(select(Member)
            .where(Member.discord_name == discord_name)).first()

    def add_member(self, name: str, discord_name: str, is_admin: bool=False):
        member = Member(
            name=name,
            discord_name=discord_name,
            is_admin=is_admin
            )
        self._session.add(member)
        self._session.commit()
        return member
    
    def remove_member_by_id(self, id: int):
        member = self.get_member_with_id(id)
        if member is None:
            logger.debug(f"Cannot remove member with id [{id}] as does not currently exist.")
            return False 
        self._session.delete(member)
        self._session.commit()
        return True
    
    # --- Game ---

    def get_games(self) -> list[Game]:
        return list(self._session.scalars(select(Game)).all())

    def get_games_for_session(self, session_id: int) -> list[Game]:
        return list(self._session.scalars(select(Game)
            .join(SessionMemberGame)
            .join(SessionMember)
            .where(SessionMember.session_id == session_id))
            .all())

    def get_game_by_id(self, id: int) -> Optional[Game]:
        return self._session.scalars(select(Game)
            .where(Game.id == id)).first()
    
    def get_game_by_name(self, name: str) -> Game | None:
        return self._session.scalars(select(Game)
            .where(Game.name == name)).first()
    
    def get_or_create_game(self, name: str) -> Game:
        game = self.get_game_by_name(name)
        if game is None: game = self.add_game(name)
        return game
    
    def add_game(self, name: str) -> Game:
        game = Game(name=name)
        self._session.add(game)
        self._session.commit()
        return game
        
# --- SessionMember ---

    def get_session_member(self, session_id: int, member_id: int) -> SessionMember | None:
        return self._session.scalars(select(SessionMember)
            .where(SessionMember.member_id == member_id)
            .where(SessionMember.session_id == session_id)).first()
        
    def get_session_members_for_session(self, session_id: int) -> list[SessionMember]:
        return list(self._session.scalars(select(SessionMember)
            .where(SessionMember.session_id == session_id)).all())
    
    def get_session_members_for_member(self, member_id: int) -> list[SessionMember]:
        return list(self._session.scalars(select(SessionMember)
            .where(SessionMember.member_id == member_id)).all())
    
    def get_session_members_for_session_and_member(self, session_id: int, member_id: int) -> list[SessionMember]:
        return list(self._session.scalars(select(SessionMember)
            .where(SessionMember.member_id == member_id)
            .where(SessionMember.session_id == session_id)
            .order_by(SessionMember.start)
            ).all())
    
    def get_pending_session_member_for_session_and_member(self, session_id: int, member_id: int) -> SessionMember | None:
        return self._session.scalars(select(SessionMember)
            .where(SessionMember.member_id == member_id)
            .where(SessionMember.session_id == session_id)
            .where(SessionMember.start != None)
            .where(SessionMember.end == None)
            .order_by(SessionMember.start)
            ).first()
    
    def get_session_member_by_id(self, session_member_id: int) -> SessionMember | None:
        return self._session.scalars(select(SessionMember)
            .where(SessionMember.id == session_member_id)).first()
    
    def add_session_member(
            self,
            session_id: int,
            member_id: int,
            start: datetime.datetime,
            end: datetime.datetime | None = None
            ):
        session_member = SessionMember(
            member_id = member_id,
            session_id = session_id,
            start = start,
            end = end 
        )
        self._session.add(session_member)
        self._session.commit()
        return session_member

    def add_or_update_session_member(self,
            session_id: int,
            member_id: int, 
            datetime: datetime.datetime,
            is_end: bool) -> SessionMember | None:
        
        session_member = self.get_pending_session_member_for_session_and_member(session_id, member_id)

        if not is_end: 
            if session_member is not None:
                logger.warning("Cannot start a session_member as one is already pending.")
                return session_member            
            return self.add_session_member(session_id, member_id, start=datetime)
        if session_member is None:
            logger.warning("Cannot end a session_member as one is not pending.")
            return None
        logger.debug(f"Updated session_member [{session_member.id}] for session [{session_id}] and member [{member_id}] end to {datetime}.")
        session_member.end = datetime
        self._session.commit()
        return session_member

# -- SessionMemberGame --

    def get_session_member_game_by_session_member_and_game(self, session_member_id: int, game_id: int) -> Optional[SessionMemberGame]:
        return self._session.scalars(select(SessionMemberGame)
            .where(SessionMemberGame.game_id == game_id)
            .where(SessionMemberGame.session_member_id == session_member_id)).first()
    
    def get_session_member_games_for_game(self, game_id: int):
        return self._session.scalars(select(SessionMemberGame)
            .where(SessionMemberGame.game_id == game_id)).all()
    
    def get_session_member_games_for_session_member(self, session_member_id: int):
        return self._session.scalars(select(SessionMemberGame)
            .where(SessionMemberGame.session_member_id == session_member_id)).all()
    
    def get_pending_session_member_game_for_session_member_and_game(self, session_member_id: int, game_id: int) -> SessionMemberGame | None:
        return self._session.scalars(select(SessionMemberGame)
            .where(SessionMemberGame.session_member_id == session_member_id)
            .where(SessionMemberGame.game_id == game_id)
            .where(SessionMemberGame.start != None)
            .where(SessionMemberGame.end == None)
            .order_by(SessionMemberGame.start)
            ).first()
    
    def add_session_member_game(
            self,
            session_member_id: int,
            game_id: int,
            start: datetime.datetime | None = None,
            end: datetime.datetime | None = None,
            ):
        if start is None and end is None: raise Exception("Cannot add session_member_game if both start and end times are None.")
        session_member_game = SessionMemberGame(
            session_member_id = session_member_id,
            game_id = game_id,
            start = start,
            end = end
        )
        logger.debug(f"Adding session_member_game [{session_member_game.id}] for session_member [{session_member_id}] and game [{game_id}] start to {start}.")
        self._session.add(session_member_game)
        self._session.commit()
        return session_member_game
    
    def add_or_update_session_member_game(
            self,
            session_member_id: int,
            game_id: int,
            datetime: datetime.datetime,
            is_end: bool
            ) -> SessionMemberGame | None:
        
        session_member_game = self.get_pending_session_member_game_for_session_member_and_game(session_member_id, game_id)
        if not is_end: 
            if session_member_game is not None:
                logger.warning("Cannot start a session_member_game as one is pending.")
                return session_member_game   
            return self.add_session_member_game(session_member_id, game_id, start=datetime)
        
        if session_member_game is None:
                logger.warning("Cannot end a session_member_game as one is not pending.")
                return None
        
        logger.debug(f"Updated session_member [{session_member_game.id}] for session_member [{session_member_id}] and game [{game_id}] end to {datetime}.")
        session_member_game.end = datetime
        self._session.commit()
        return session_member_game

## -- stats

    def get_total_attendance_for_member_by_id(self, member_id):
        session_members = self._session.query(SessionMember).where(SessionMember.member_id == member_id).all()
        return len(set(session_member.session_id for session_member in session_members))

    def get_games_master_count_for_member_by_id(self, member_id):
        return self._session.query(Session).where(Session.games_master_id == member_id).count()
    
    def get_last_games_master_session_for_member_by_id(self, member_id):
        return self._session.scalars(select(Session).where(Session.games_master_id == member_id)).first()

## -- RAW --

    def get_table_names(self):
        return Base.metadata.tables.keys()
    
    def get_table_from_name(self, table_name):
        return Base.metadata.tables.get(table_name, None)
    
    def get_rows(self, table):
        return self._session.execute(select(table)).all()