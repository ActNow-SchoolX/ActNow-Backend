import re

from passlib.hash import sha256_crypt
from pydantic import BaseModel, validator
from sqlmodel import Session

from src.backend.database import engine
from src.backend.database.orm import User, UserMetadata

NICKNAME_PATTERN = re.compile(r"^[a-zA-Z0-9]+$")
PASSWORD_PATTERN = re.compile(r"[0-9]")
FILE_FORMAT = ["image/jpg", "image/png", "image/jpeg"]


def get_password_hash(password):
    return sha256_crypt.hash(password)


def validate_photo(content_type, size):

    state = True

    if (content_type not in FILE_FORMAT) or (int(size) > 4194304):
        state = False
        
    return state


def user_registrate(user_data) -> User:

    new_user = User(
        nickname=user_data.nickname,
        password=user_data.password,
    )

    with Session(engine) as session:
        User.create(new_user, session)

    return new_user


def user_metadata_create(user_data, user_id) -> UserMetadata:

    new_user_metadata = UserMetadata(
        user_id=user_id,
        description=user_data.profile_description,
        photo=user_data.profile_photo,
    )

    with Session(engine) as session:
        UserMetadata.create(new_user_metadata, session)

    return new_user_metadata


class UserRequest(BaseModel):

    nickname: str
    password: str 
    profile_photo: str | None = None
    profile_description: str | None = None

    @validator("nickname")
    def validate_name(cls, value):   # Пройдет валидацию при наличии только лишь букв и цифр в нике, а также по длинам.

        if ((not NICKNAME_PATTERN.search(value))    # Сопоставляю с регулярным выражением
            or (len(value) > 20) 
            or (len(value) == 0)
        ):

            raise ValueError(
                'Никнейм не соответствует условиям'
            )
        
        return value
    
    @validator("password")
    def validate_password(cls, value):   # Пройдет валидацию только при наличии цифр, двух букв в разном регистре и
        # по длинам.

        if ((not PASSWORD_PATTERN.search(value))    # Сопоставляю с регулярным выражением
            or (len(value) > 20)
            or (len(value) < 8)
            or (re.sub(PASSWORD_PATTERN, '', value) == '')  # Проверяю наличие букв в пароле
            or (re.sub(PASSWORD_PATTERN, '', value).islower())  # Проверяю наличие заглавных букв
            or (re.sub(PASSWORD_PATTERN, '', value).isupper())  # Проверяю наличие строчных букв
        ):

            raise ValueError(
                'Пароль не соответствует условиям'
            )
        
        return value
    
    @validator("profile_description")
    def validate_desc(cls, value):   # Пройдет валидацию только по длине.

        if len(value) > 127:

            raise ValueError(
                'Описание профиля не соответствует условиям'
            )
        
        return value


class UserResponse(BaseModel):

    id: int
    nickname: str
    profile_photo: str | None = None
    profile_description: str | None = None
