from sqlmodel import SQLModel, Field, Relationship, select, Session
from typing import Optional, List
from datetime import datetime

__all__ = [
    "User",
    "UserMetadata",
    "Goal",
    "Story",
    "UserStoryLikes",
]


class UserStoryLikes(SQLModel, table=True):
    """UserStoryLikes model

    :param user_id: user id
    :param story_id: story id
    """
    user_id: Optional[int] = Field(foreign_key="user.id", primary_key=True)
    story_id: Optional[int] = Field(foreign_key="story.id", primary_key=True)


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
    liked_stories: List["Story"] = Relationship(back_populates="liked_users", link_model=UserStoryLikes)
    user_metadata: "UserMetadata" = Relationship(back_populates="user")

    @classmethod
    def get_by_nickname(cls, session: Session, nickname: str) -> Optional["User"]:
        """Get user by nickname

        :param session: session
        :param nickname: user nickname
        :return: user
        """
        return session.exec(select(cls).where(cls.nickname == nickname)).first()

    @classmethod
    def get_by_id(cls, session: Session, _id: int) -> Optional["User"]:
        """Get user by id

        :param session: session
        :param _id: user id
        :return: user
        """
        return session.get(cls, _id)

    @classmethod
    def get_all(cls, session: Session, limit: int = 100, offset: int = 0) -> List["User"]:
        """Get all users

        :param session: session
        :param limit: limit
        :param offset: offset
        :return: users
        """
        return session.exec(select(cls).offset(offset).limit(limit)).all()

    def create(self, session: Session) -> "User":
        """Create user

        :param session: session
        :return: user
        """
        session.add(self)
        session.commit()
        session.refresh(self)
        return self

    def update(self, session: Session) -> "User":
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
    def get_by_user_id(cls, session: Session, user_id: int) -> Optional["UserMetadata"]:
        """Get user metadata by user id

        :param session: session
        :param user_id: user id
        :return: user metadata
        """
        return session.exec(select(cls).where(cls.user_id == user_id)).first()

    @classmethod
    def create(cls, session: Session, user_id: int, description: str, photo: str) -> "UserMetadata":
        """Create user metadata

        :param session: session
        :param user_id: user id
        :param description: user description
        :param photo: user photo
        :return: user metadata
        """
        user_metadata = cls(user_id=user_id, description=description, photo=photo)
        session.add(user_metadata)
        session.commit()
        session.refresh(user_metadata)
        return user_metadata

    def update(self, session: Session) -> "UserMetadata":
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
    price: Optional[float] = Field(default=0.)
    deadline: Optional[datetime] = Field(default=None)
    date_create: datetime = Field(default_factory=datetime.now)
    user_id: int = Field(foreign_key="user.id")
    user: 'User' = Relationship(back_populates="goals")
    stories: List["Story"] = Relationship(back_populates="goal")

    @classmethod
    def get_by_id(cls, session: Session, _id: int) -> Optional["Goal"]:
        """Get goal by id

        :param session: session
        :param _id: goal id
        :return: goal
        """
        return session.get(cls, _id)

    @classmethod
    def get_all(cls, session: Session, limit: int = 100, offset: int = 0) -> List["Goal"]:
        """Get all goals

        :param session: session
        :param limit: limit
        :param offset: offset
        :return: goals
        """
        return session.exec(select(cls).offset(offset).limit(limit)).all()

    @classmethod
    def get_by_user_id(cls, session: Session, user_id: int, limit: int = 100, offset: int = 0) -> List["Goal"]:
        """Get goals by user id

        :param session: session
        :param user_id: user id
        :param limit: limit
        :param offset: offset
        :return: goals
        """
        return session.exec(select(cls).where(cls.user_id == user_id).offset(offset).limit(limit)).all()

    def create(self, session: Session) -> "Goal":
        """Create goal

        :param session: session
        :return: goal
        """
        session.add(self)
        session.commit()
        session.refresh(self)
        return self

    def update(self, session: Session) -> "Goal":
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
    def get_by_id(cls, session: Session, _id: int) -> Optional["Story"]:
        """Get story by id

        :param session: session
        :param _id: story id
        :return: story
        """
        return session.get(cls, _id)

    @classmethod
    def get_all(cls, session: Session, limit: int = 100, offset: int = 0) -> List["Story"]:
        """Get all stories

        :param session: session
        :param limit: limit
        :param offset: offset
        :return: stories
        """
        return session.exec(select(cls).offset(offset).limit(limit)).all()

    @classmethod
    def get_by_user_id(cls, session: Session, user_id: int, limit: int = 100, offset: int = 0) -> List["Story"]:
        """Get stories by user id

        :param session: session
        :param user_id: user id
        :param limit: limit
        :param offset: offset
        :return: stories
        """
        return session.exec(select(cls).where(cls.user_id == user_id).offset(offset).limit(limit)).all()

    @classmethod
    def get_by_goal_id(cls, session: Session, goal_id: int, limit: int = 100, offset: int = 0) -> List["Story"]:
        """Get stories by goal id

        :param session: session
        :param goal_id: goal id
        :param limit: limit
        :param offset: offset
        :return: stories
        """
        return session.exec(select(cls).where(cls.goal_id == goal_id).offset(offset).limit(limit)).all()

    def create(self, session: Session) -> "Story":
        """Create story

        :param session: session
        :return: story
        """
        session.add(self)
        session.commit()
        session.refresh(self)
        return self

    def update(self, session: Session) -> "Story":
        """Update story

        :param session: session
        :return: story
        """
        session.add(self)
        session.commit()
        session.refresh(self)
        return self

    def delete(self, session: Session) -> "Story":
        """Delete story

        :param session: session
        :return: story
        """
        self.deleted = True
        session.add(self)
        session.commit()
        session.refresh(self)
        return self
