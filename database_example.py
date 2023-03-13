from src.backend.database.orm import (
    User,
    UserMetadata,
    Goal,
    Story
)

from sqlmodel import Session, SQLModel
from src.backend.database import engine

SQLModel.metadata.create_all(engine)

if __name__ == '__main__':
    with Session(engine) as session:
        user_2 = User.get_by_id(session, _id=7)

        goals_1 = Goal(
            user_id=user_2.id,
            title="My test goal",
            description="My very very nice goal with bitches and jack daniels"
        )

        session.add(goals_1)
        session.commit()

        goals = Goal.get_by_user_id(session, user_id=user_2.id)
        print(goals)
