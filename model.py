from datetime import datetime, date, timedelta
from sqlalchemy import Column, Boolean, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    discord_name: Mapped[str] = mapped_column(String(32))
    name: Mapped[str] = mapped_column(String(32))
    in_rotation: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    
    games_master_sessions: Mapped["Session"] = relationship(back_populates="games_master")
    session_members: Mapped[list["SessionMember"]] = relationship(back_populates="member")

class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date)
    games_master_id: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=True)

    games_master: Mapped["Member"] = relationship(back_populates="games_master_sessions")
    session_members: Mapped[list["SessionMember"]] = relationship(back_populates="session")

class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(32))
    ignore: Mapped[bool] = mapped_column(Boolean, default=False)

    session_member_games: Mapped[list["SessionMemberGame"]] = relationship(back_populates="game")

class SessionMember(Base):
    __tablename__ = "session_members"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"))
    start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    session: Mapped["Session"] = relationship(back_populates="session_members")
    member: Mapped["Member"] = relationship(back_populates="session_members")
    session_member_games: Mapped[list["SessionMemberGame"]] = relationship(back_populates="session_member")

    def get_duration(self) -> timedelta | None:
        if self.start is None or self.end is None: return None
        return self.end - self.start

class SessionMemberGame(Base):
    __tablename__ = "session_member_games"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_member_id: Mapped[int] = mapped_column(ForeignKey("session_members.id"))
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    start: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    end: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    session_member: Mapped["SessionMember"] = relationship(back_populates="session_member_games")
    game: Mapped["Game"] = relationship(back_populates="session_member_games")

    def get_duration(self) -> timedelta | None:
        if self.start is None or self.end is None: return None
        return self.end - self.start
    
# class MemberGame(Base):
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
#     member_id: Mapped[int] = mapped_column(ForeignKey("members.id"))

#     member: Mapped["Game"] = relationship(back_populates="session_member_games")
#     game: Mapped["Game"] = relationship(back_populates="session_member_games")
