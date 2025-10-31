import os
import datetime
import constants
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy import select
from typing import Optional
from model import Base, Member, Session, SessionMember

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

    def get_sessions(self) -> list[Session]:
        """Gets all sessions from the database."""
        return self._session.scalars(select(Session)).all()

    def get_members(self) -> list[Member]:
        """Gets all members from the database."""
        return self._session.scalars(select(Member)).all()

    def get_session_by_id(self, id: int) -> Optional[Session]:
        return self._session.scalars(select(Session)
            .where(Session.id == id)).first()
    
    def get_session_by_date(self, date: datetime.date) -> Session:
        """Checks the database for a session which matches the datetime."""
        return self._session.scalars(select(Session)
            .where(Session.date == date)).first()
    
    def get_member_by_id(self, id: int) -> Optional[Member]:
        return self._session.scalars(select(Member)
            .where(Member.id == id)).first()
    
    def get_member_by_name(self, name: str) -> Optional[Member]:
        return self._session.scalars(select(Member)
            .where(Member.name == name)).first()
    
    def get_member_by_discord_name(self, discord_name: str) -> Optional[Member]:
        return self._session.execute(select(Member)
            .where(Member.discord_name == discord_name)).first()

    def get_session_member(self, session_id: int, member_id: int) -> Optional[SessionMember]:
        return self._session.execute(select(Member)
            .where(SessionMember.member_id == member_id)
            .where(SessionMember.session_id == session_id)).first()
        
    def get_session_members_for_session(self, session_id: int):
        return self._session.scalars(select(SessionMember)
            .where(SessionMember.session_id == session_id)).all()
    
    def get_session_member_by_id(self, session_member_id: int) -> Optional[SessionMember]:
        return self._session.scalars(select(Member)
            .where(SessionMember.id == session_member_id)).first()
    
    def add_session(self, date: datetime.date):
        """Adds a new session to the database."""
        session = Session(date=date)
        self._session.add(session)
        self._session.commit()
        return session

    def add_member(self, name: str, discord_name: str):
        member = Member(name=name,
                        discord_name=discord_name)
        self._session.add(member)
        self._session.commit()
        return member
        
    def add_session_member(self, member_id: int, session_id: int, start: datetime, end: datetime):
        session_member = SessionMember(
            member_id = member_id,
            session_id = session_id,
            start = start,
            end = end 
        )
        self._session.add(session_member)
        self._session.commit()
        return session_member

    def remove_member_by_id(self, id: int):
            member = self.get_member_by_id(id)
            if member is None: return False 

            self._session.remove(member)
            self._session.commit()
            return True

    def update_session_member(self, session_member: SessionMember) -> None:    
        with sqlalchemy.orm.Session(engine) as session:
            session.update(session_member)
            session.commit()