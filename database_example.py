from src.backend.database.orm import (
    User,
    UserMetadata,
    Goal,
    Story,
)

from sqlmodel import Session, SQLModel
from src.backend.database import engine

SQLModel.metadata.create_all(engine)


def register_fake_user() -> User:
    user = User(
        nickname="user1",
        password="password1",
    )

    with Session(engine) as session:
        user.create(session)

    return user


def create_fake_metadata(user_id: int) -> UserMetadata:
    user_metadata = UserMetadata(
        user_id=user_id,
        photo="https://example.com/photo.jpg",
        description="This is a fake user",
    )

    with Session(engine) as session:
        user_metadata.create(session)

    return user_metadata


def create_fake_goal(user_id: int) -> Goal:
    goal = Goal(
        user_id=user_id,
        title="My goal",
        description="This is a fake goal",
    )

    with Session(engine) as session:
        goal.create(session)

    return goal


def create_fake_story(user_id: int, goal_id: int) -> Story:
    story = Story(
        user_id=user_id,
        goal_id=goal_id,
        photo="https://example.com/photo.jpg",
        summary="This is a fake story",
    )

    with Session(engine) as session:
        story.create(session)

    return story


if __name__ == "__main__":
    fake_user = register_fake_user()
    # create_fake_metadata(fake_user.id)

    fake_goal = create_fake_goal(fake_user.id)
    create_fake_story(fake_user.id, fake_goal.id)

    # get list of all user stories: 2 ways
    # 1. using SQLMODEL ORM,
    # but we need to get it with a transaction
    with Session(engine) as _session:
        searched_user = User.get_by_id(_session, fake_user.id)
        print(searched_user.stories)

    # 2. using ORM that declared in src/backend/database/orm.py
    with Session(engine) as _session:
        # limit is the maximum number of stories to return
        # offset is the number of stories to skip in the database read
        stories = Story.get_by_user_id(_session, fake_user.id, limit=100, offset=0)

    print(stories)

    # I've barely recommended to use the second way, because it's more flexible with SQL queries,
    # and it's more efficient, because it doesn't need to read all the stories from the database

    # but as fact, you can still use the first way, because it's more readable and easier to use
