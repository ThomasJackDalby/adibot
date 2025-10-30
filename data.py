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

def get_sessions() -> list[Session]:
    with sqlalchemy.orm.Session(engine) as session:
        return [row[0] for row in session.execute(select(Session)).all()]

def get_session_by_date(date: datetime.date) -> Session:
    """Checks the database for a session which matches the datetime"""
    with sqlalchemy.orm.Session(engine) as session:
        return session.execute(select(Session).where(Session.date == date)).scalar()
    
def add_session(date: datetime.date):
    with sqlalchemy.orm.Session(engine) as session:
        sess = Session(date=date)
        session.add(sess)
        session.commit()
        return sess

def get_members() -> list[Member]:
    with sqlalchemy.orm.Session(engine) as session:
        return [row[0] for row in session.execute(select(Member)).all()]

def get_member_by_id(id: int) -> Optional[Member]:
    with sqlalchemy.orm.Session(engine) as session:
        return session.execute(select(Member)
                               .where(Member.id == id)).scalar()

def get_member_by_name(name: str) -> Optional[Member]:
    with sqlalchemy.orm.Session(engine) as session:
        return session.execute(select(Member)
                               .where(Member.name == name)).scalar()

def get_member_by_discord_name(discord_name: str) -> Optional[Member]:
    with sqlalchemy.orm.Session(engine) as session:
        return session.execute(select(Member)
            .where(Member.discord_name == discord_name)).scalar()

def add_member(name: str, discord_name: str):
    with sqlalchemy.orm.Session(engine) as session:
        member = Member(name=name,
                        discord_name = discord_name)
        session.add(member)
        session.commit()
        return member

def remove_member_by_id(id: int):
    with sqlalchemy.orm.Session(engine) as session:
        member = session.execute(select(Member)
                                .where(Member.id == id)).scalar()
        if member is None: return False 
        session.remove(member)
        session.commit()
        return True

def add_session_member(member_id: int, session_id: int, start: datetime, end: datetime):
    with sqlalchemy.orm.Session(engine) as session:
        session_member = SessionMember(
            member_id = member_id,
            session_id = session_id,
            start = start,
            end = end 
        )
        session.add(session_member)
        session.commit()
        return session_member

def get_session_member_by_id(session_member_id: int) -> Optional[SessionMember]:
    with sqlalchemy.orm.Session(engine) as session:
        return session.execute(select(Member)
            .where(SessionMember.id == session_member_id)).scalar()
    
def get_session_member(session_id: int, member_id: int) -> Optional[SessionMember]:
    with sqlalchemy.orm.Session(engine) as session:
        return session.execute(select(Member)
            .where(SessionMember.member_id == member_id)
            .where(SessionMember.session_id == session_id)).scalar()
    
def update_session_member(session_member: SessionMember) -> None:    
    with sqlalchemy.orm.Session(engine) as session:
        session.update(session_member)
        session.commit()