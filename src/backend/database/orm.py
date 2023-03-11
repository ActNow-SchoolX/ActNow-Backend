from sqlmodel import SQLModel, Field, Relationship, select, create_engine, Session
from typing import Optional, List, Dict, Any
from datetime import datetime


# class user with id, nickname, password and relationship for UserMetadata
class User(SQLModel, table=True):
    """User model

    :param id: user id
    :param nickname: user nickname
    :param password: user password
    :param goals: user goals
    :param stories: user stories
    :param user_metadata: user metadata
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    nickname: str
    password: str
    goals: List["Goal"] = Relationship(back_populates="user")
    stories: List["Story"] = Relationship(back_populates="user")
    user_metadata: "UserMetadata" = Relationship(back_populates="user")


# class UserMetadata with id, description, photo, date_create and date_modify
class UserMetadata(SQLModel, table=True):
    """UserMetadata model

    :param id: user metadata id
    :param description: user description
    :param photo: user photo
    :param date_create: user metadata date create
    :param date_modify: user metadata date modify
    :param user_id: user id
    :param user: user
    """
    id: int = Field(default=None, primary_key=True)
    description: str = Field(default=None)
    photo: str = Field(default=None)
    date_create: datetime = Field(default_factory=datetime.now)
    date_modify: datetime = Field(default_factory=datetime.now)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: "User" = Relationship(back_populates="user_metadata")


# class Goal with id, user_id, title, description, price, deadline, date_create
class Goal(SQLModel, table=True):
    """Goal model

    :param id: goal id
    :param title: goal title
    :param description: goal description
    :param price: goal price
    :param deadline: goal deadline
    :param date_create: goal date create
    :param user_id: user id
    :param user: user
    :param stories: goal stories
    """
    id: int = Field(default=None, primary_key=True)
    title: str
    description: str
    price: int
    deadline: Optional[datetime] = Field(default=None)
    date_create: datetime = Field(default_factory=datetime.now)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: "User" = Relationship(back_populates="goals")
    stories: List["Story"] = Relationship(back_populates="goal")


# class Story with id, user, goal, photo, summary, dste_create and deleted
class Story(SQLModel, table=True):
    """Story model

    :param id: story id
    :param user_id: user id
    :param user: user
    :param goal_id: goal id
    :param goal: goal
    :param photo: story photo
    :param summary: story summary
    :param date_create: story date create
    :param deleted: story deleted
    """
    id: int = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: "User" = Relationship(back_populates="stories")
    goal_id: Optional[int] = Field(default=None, foreign_key="goal.id")
    goal: "Goal" = Relationship(back_populates="stories")
    photo: str
    summary: str
    date_create: datetime = Field(default_factory=datetime.now)
    deleted: bool = Field(default=False)
