import datetime
from bcrypt import gensalt, hashpw
from peewee import *

sqlite_database = SqliteDatabase(":memory:")


class BaseModel(Model):
    class Meta:
        database = sqlite_database


class User(BaseModel):
    email = CharField(unique=True)
    password = CharField()
    created_at = DateTimeField()

    def get_all_users(self):
        users = User.select()
        return list(map(lambda user: user, users))

    def get_user_where_email(self, email: str):
        return User.select().where(User.email == email).get()

    def insert_user(self, email: str, password: str):
        hashed_pwd = hashpw(password.encode(), gensalt())
        User.insert(
            email=email, password=hashed_pwd, created_at=datetime.datetime.now()
        ).execute()

    def __repr__(self):
        return f"email: {self.email}, password: {self.password}, created_at: {self.created_at}"


def create_tables():
    User.create_table()
