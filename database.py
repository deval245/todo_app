from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Change `localhost:5433` to `db:5432`
sqlalchemy_database_url = 'postgresql://myuser:mypassword@db:5432/TodoAppDatabase'

engine = create_engine(sqlalchemy_database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# branch to commit