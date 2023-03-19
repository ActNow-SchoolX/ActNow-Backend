from os import environ
from sqlmodel import create_engine

if environ.get('DATABASE_URL').startswith('mysql'):
    engine = create_engine(
        environ.get("DATABASE_URL"),
        echo=False,
    )
elif environ.get('DATABASE_URL').startswith('postgresql'):
    engine = create_engine(
        environ.get("DATABASE_URL"),
        echo=False,
    )
elif environ.get('DATABASE_URL').startswith('sqlite'):
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        environ.get("DATABASE_URL"),
        echo=False,
        connect_args=connect_args,
    )
