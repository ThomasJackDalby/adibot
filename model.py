from datetime import datetime, date
from sqlalchemy import Column, Boolean, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    discord_name: Mapped[str] = mapped_column(String(32))
    name: Mapped[int] = mapped_column(String(32))
    in_rotation: Mapped[bool] = mapped_column(Boolean, default=True)

    session_members: Mapped[list["SessionMember"]] = relationship(back_populates="member")

class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date)

    session_games: Mapped[list["SessionGame"]] = relationship(back_populates="session")
    session_members: Mapped[list["SessionMember"]] = relationship(back_populates="session")

class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_games: Mapped[list["SessionGame"]] = relationship(back_populates="game")

class SessionMember(Base):
    __tablename__ = "session_members"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"))
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    start: Mapped[datetime] = mapped_column(DateTime)
    end: Mapped[datetime] = mapped_column(DateTime)

    member: Mapped["Member"] = relationship(back_populates="session_members")
    session: Mapped["Session"] = relationship(back_populates="session_members")

class SessionGame(Base):
    __tablename__ = "session_games"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    start: Mapped[datetime] = mapped_column(DateTime)
    end: Mapped[datetime] = mapped_column(DateTime)

    game: Mapped["Game"] = relationship(back_populates="session_games")
    session: Mapped["Session"] = relationship(back_populates="session_games")