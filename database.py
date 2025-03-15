import datetime
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

    def get_user_where_email(self, email):
        return User.select().where(email)

    def insert_user(self, email, password):
        User.insert(
            email=email, password=password, created_at=datetime.datetime.now()
        ).execute()

    def __repr__(self):
        return f"email: {self.email}, created_at: {self.created_at}"


def create_tables():
    with sqlite_database:
        sqlite_database.create_tables([User])
