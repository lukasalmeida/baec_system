from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

URL_BANCO_DADOS = (
    "postgresql://"
    "baec_user:"
    "baec_password@"
    "postgres:5432/"
    "baec_db"
)

motor = create_engine(URL_BANCO_DADOS)

SessaoLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=motor
)


