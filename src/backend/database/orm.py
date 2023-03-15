from sqlmodel import SQLModel, Field, Relationship, select, Session
from typing import List, TypeVar
from datetime import datetime

__all__ = [
    "User",
    "UserMetadata",
    "Goal",
    "Story",
    "UserStoryLikes",
]

U = TypeVar("U", bound="User")
UM = TypeVar("UM", bound="UserMetadata")
G = TypeVar("G", bound="Goal")
S = TypeVar("S", bound="Story")


class UserStoryLikes(SQLModel, table=True):
    """UserStoryLikes model

    :param user_id: user id
    :param story_id: story id
    """
    user_id: int | None = Field(foreign_key="user.id", primary_key=True)
    story_id: int | None = Field(foreign_key="story.id", primary_key=True)


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
    id: int | None = Field(default=None, primary_key=True)
    nickname: str
    password: str
    goals: List["Goal"] = Relationship(back_populates="user")
    stories: List["Story"] = Relationship(back_populates="user")
    liked_stories: List["Story"] = Relationship(back_populates="liked_users", link_model=UserStoryLikes)
    user_metadata: "UserMetadata" = Relationship(back_populates="user")

    @classmethod
    def get_by_nickname(cls: type[U], session: Session, nickname: str) -> U | None:
        """Get user by nickname

        :param session: session
        :param nickname: user nickname
        :return: user
        """
        return session.exec(select(cls).where(cls.nickname == nickname)).first()

    @classmethod
    def get_by_id(cls: type[U], session: Session, _id: int) -> U | None:
        """Get user by id

        :param session: session
        :param _id: user id
        :return: user
        """
        return session.get(cls, _id)

    @classmethod
    def get_all(cls: type[U], session: Session, limit: int = 100, offset: int = 0) -> List[U]:
        """Get all users

        :param session: session
        :param limit: limit
        :param offset: offset
        :return: users
        """
        return session.exec(select(cls).offset(offset).limit(limit)).all()

    @classmethod
    def like_story(cls: type[U], session: Session, user_id: int, story_id: int) -> None:
        """Like story

        :param session: session
        :param user_id: user id
        :param story_id: story id
        """
        session.add(UserStoryLikes(user_id=user_id, story_id=story_id))
        session.commit()

    def create(self, session: Session) -> U:
        """Create user

        :param session: session
        :return: user
        """
        session.add(self)
        session.commit()
        session.refresh(self)
        return self

    def update(self, session: Session) -> U:
        """Update user

        :param session: session
        :return: user
        """
        session.add(self)
        session.commit()
        session.refresh(self)
        return self


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
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="user_metadata")

    @classmethod
    def get_by_user_id(cls: type[UM], session: Session, user_id: int) -> UM | None:
        """Get user metadata by user id

        :param session: session
        :param user_id: user id
        :return: user metadata
        """
        return session.exec(select(cls).where(cls.user_id == user_id)).first()

    def create(self, session: Session) -> UM:
        """Create user metadata

        :param session: session
        :return: user metadata
        """
        session.add(self)
        session.commit()
        session.refresh(self)
        return self

    def update(self, session: Session) -> UM:
        """Update user metadata

        :param session: session
        :return: user metadata
        """
        self.date_modify = datetime.now()
        session.add(self)
        session.commit()
        session.refresh(self)
        return self


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
    price: float | None = Field(default=0.)
    deadline: datetime | None = Field(default=None)
    date_create: datetime = Field(default_factory=datetime.now)
    user_id: int = Field(foreign_key="user.id")
    user: 'User' = Relationship(back_populates="goals")
    stories: List["Story"] = Relationship(back_populates="goal")

    @classmethod
    def get_by_id(cls: type[G], session: Session, _id: int) -> G | None:
        """Get goal by id

        :param session: session
        :param _id: goal id
        :return: goal
        """
        return session.get(cls, _id)

    @classmethod
    def get_all(cls: type[G], session: Session, limit: int = 100, offset: int = 0) -> List[G]:
        """Get all goals

        :param session: session
        :param limit: limit
        :param offset: offset
        :return: goals
        """
        return session.exec(select(cls).offset(offset).limit(limit)).all()

    @classmethod
    def get_by_user_id(cls: type[G], session: Session, user_id: int, limit: int = 100, offset: int = 0) -> List[G]:
        """Get goals by user id

        :param session: session
        :param user_id: user id
        :param limit: limit
        :param offset: offset
        :return: goals
        """
        return session.exec(select(cls).where(cls.user_id == user_id).offset(offset).limit(limit)).all()

    def create(self, session: Session) -> G:
        """Create goal

        :param session: session
        :return: goal
        """
        session.add(self)
        session.commit()
        session.refresh(self)
        return self

    def update(self, session: Session) -> G:
        """Update goal

        :param session: session
        :return: goal
        """
        session.add(self)
        session.commit()
        session.refresh(self)
        return self


# class Story with id, user, goal, photo, summary, date_create and deleted
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
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="stories")
    goal_id: int = Field(foreign_key="goal.id")
    goal: "Goal" = Relationship(back_populates="stories")
    liked_users: List["User"] = Relationship(back_populates="liked_stories", link_model=UserStoryLikes)
    photo: str
    summary: str
    date_create: datetime = Field(default_factory=datetime.now)
    deleted: bool = Field(default=False)

    @classmethod
    def get_by_id(cls: type[S], session: Session, _id: int) -> S | None:
        """Get story by id

        :param session: session
        :param _id: story id
        :return: story
        """
        return session.get(cls, _id)

    @classmethod
    def get_all(cls: type[S], session: Session, limit: int = 100, offset: int = 0) -> List[S]:
        """Get all stories

        :param session: session
        :param limit: limit
        :param offset: offset
        :return: stories
        """
        return session.exec(select(cls).offset(offset).limit(limit)).all()

    @classmethod
    def get_by_user_id(cls: type[S], session: Session, user_id: int, limit: int = 100, offset: int = 0) -> List[S]:
        """Get stories by user id

        :param session: session
        :param user_id: user id
        :param limit: limit
        :param offset: offset
        :return: stories
        """
        return session.exec(select(cls).where(cls.user_id == user_id).offset(offset).limit(limit)).all()

    @classmethod
    def get_by_goal_id(cls: type[S], session: Session, goal_id: int, limit: int = 100, offset: int = 0) -> List[S]:
        """Get stories by goal id

        :param session: session
        :param goal_id: goal id
        :param limit: limit
        :param offset: offset
        :return: stories
        """
        return session.exec(select(cls).where(cls.goal_id == goal_id).offset(offset).limit(limit)).all()

    @classmethod
    def add_user_like(cls: type[S], session: Session, story_id: int, user_id: int) -> S | None:
        """Add user like

        :param session: session
        :param story_id: story id
        :param user_id: user id
        :return: story
        """
        story = cls.get_by_id(session, story_id)
        if story:
            story.liked_users.append(User.get_by_id(session, user_id))
            session.add(story)
            session.commit()
            session.refresh(story)
            return story
        return None

    def create(self, session: Session) -> S:
        """Create story

        :param session: session
        :return: story
        """
        session.add(self)
        session.commit()
        session.refresh(self)
        return self

    def update(self, session: Session) -> S:
        """Update story

        :param session: session
        :return: story
        """
        session.add(self)
        session.commit()
        session.refresh(self)
        return self

    def delete(self, session: Session) -> S:
        """Delete story

        :param session: session
        :return: story
        """
        self.deleted = True
        session.add(self)
        session.commit()
        session.refresh(self)
        return self
