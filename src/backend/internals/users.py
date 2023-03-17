from pydantic import BaseModel, validator
from passlib.hash import sha256_crypt
from fastapi import UploadFile
import re, string

NICKNAME_PATTERN = re.compile(r"^[a-zA-Z0-9]+$")
PASSWORD_PATTERN = re.compile(r"[0-9]")
FILE_FORMAT = ["png", "jpeg"]


def get_password_hash(password):
    return sha256_crypt.hash(password)


def validate_photo(content_type):
    if content_type not in FILE_FORMAT:
        raise


class User(BaseModel):

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
    def validate_password(cls, value):   # Пройдет валидацию только при наличии цифр, двух букв в разном регистре и по длинам.

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

    


