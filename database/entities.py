import datetime
import os
from bcrypt import gensalt, hashpw
from peewee import *

pytest_running = os.environ.get("PYTEST_RUNNING") == "True"
database_location = ":memory:" if pytest_running else "local.db"


sqlite_database = SqliteDatabase(database_location)


class BaseModel(Model):
    class Meta:
        database = sqlite_database


class User(BaseModel):
    email = CharField(unique=True)
    password = CharField()
    created_at = DateTimeField()

    def get_all_users():
        users = User.select()
        return list(map(lambda user: user, users))

    def get_user_where_email(email: str):
        return User.get(User.email == email)

    def insert_user(email: str, password: str):
        hashed_pwd = hashpw(password.encode(), gensalt())
        User.insert(
            email=email, password=hashed_pwd, created_at=datetime.datetime.now()
        ).execute()

    def __repr__(self):
        return f"email: {self.email}, password: {self.password}, created_at: {self.created_at}"


class Transaction(BaseModel):
    user = ForeignKeyField(User)
    amount = FloatField()
    category = CharField()
    created_at = DateTimeField()
    description = CharField()

    def insert_transaction(user: User, amount: float, category: str, description: str):
        Transaction.insert(
            user=user,
            amount=amount,
            category=category,
            created_at=datetime.datetime.now(),
            description=description,
        ).execute()

    def get_all_transactions_by_user(user: User):
        transactions = Transaction.select().where(Transaction.user == user)
        return list(map(lambda transaction: transaction, transactions))

    def get_transactions_between(user: User, from_date: str, to_date: str):

        transactions = Transaction.select().where(
            (Transaction.user == user)
            & (Transaction.created_at >= datetime.datetime.fromisoformat(from_date))
            & (Transaction.created_at <= datetime.datetime.fromisoformat(to_date))
        )
        return list(map(lambda transaction: transaction, transactions))
