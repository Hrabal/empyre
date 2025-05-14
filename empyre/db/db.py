from sqlalchemy import URL
from sqlalchemy.orm import joinedload
from sqlmodel import Session, SQLModel, create_engine

from .sqlmodels import DbRule


class EmpyreDb:
    def __init__(self, db_uri: str):
        db_uri = URL.create(
            "postgresql",
            username="user",
            password="pwd",
            host="localhost",
            database="empyre",
        )
        self.engine = create_engine(db_uri, echo=True)

    def load_rules(self):
        with Session(self.engine) as session:
            query = session.query(DbRule)
            query = query.options(joinedload(DbRule.matchers))
            query = query.options(joinedload(DbRule.outcomes))
            return query.all()

    def create_db(self):
        SQLModel.metadata.create_all(self.engine)
