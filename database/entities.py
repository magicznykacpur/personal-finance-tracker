from datetime import datetime
import os
from bcrypt import gensalt, hashpw
from peewee import *

from utils import get_dates_around_month

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
    budget = FloatField(default=0)

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

    def set_user_budget(user_id: int, budget: float):
        User.update(budget=budget).where(User.id == user_id).execute()

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
            & (Transaction.created_at >= datetime.fromisoformat(from_date))
            & (Transaction.created_at <= datetime.fromisoformat(to_date))
        )
        return list(map(lambda transaction: transaction, transactions))

    def get_transaction_where_user_and_id(user: User, transaction_id: int):
        return Transaction.get(
            (Transaction.user == user) & (Transaction.id == transaction_id)
        )

    def get_transactions_where_user_and_month_and_category(
        user: User, month: int, category: str
    ):
        current_month, next_month = get_dates_around_month(month)

        transactions = Transaction.select().where(
            (Transaction.user == user)
            & (Transaction.created_at >= current_month)
            & (Transaction.created_at <= next_month)
            & (Transaction.category == category)
        )
        return list(map(lambda transaction: transaction, transactions))
