import os
from typing import Annotated
from database.entities import Transaction, User
from request import TransactionRQ, UserRQ
from fastapi import FastAPI, Header
from bcrypt import checkpw
import jwt

app = FastAPI()

env = open(".env").read().split("=")
os.environ[env[0]] = env[1]


@app.get("/user")
def get_users():
    return User.get_all_users()


@app.post("/register")
def register(user_rq: UserRQ):
    try:
        User.insert_user(email=user_rq.email, password=user_rq.password)
        return {"code": 201, "message": "user created"}
    except Exception as e:
        if str(e) == "UNIQUE constraint failed: user.email":
            return {"code": 400, "message": f"user {user_rq.email} already exists"}
        else:
            return e


@app.post("/login")
def login(user_rq: UserRQ):
    user = User.get_user_where_email(email=user_rq.email)
    if checkpw(user_rq.password.encode(), user.password.encode()):
        return jwt.encode(
            {"email": user.email, "password": user.password[5:10]},
            os.environ.get("JWT_SECRET"),
            algorithm="HS256",
        )
    else:
        return {"code": 401, "message": "unauthorized"}


@app.get("/transaction")
def get_all_transactions_by_user(authorization: Annotated[str | None, Header()] = None):
    token = authorization.split("Bearer ")[1]
    email = jwt.decode(token, os.environ.get("JWT_SECRET"), algorithms=["HS256"])[
        "email"
    ]

    if email:
        user = User.get_user_where_email(email)
        transactions = Transaction.get_all_transactions_by_user(user)
        return transactions
    else:
        return {"code": 401, "message": "unauthorized"}


@app.post("/transaction")
def create_transactions(
    transaction_rq: TransactionRQ, authorization: Annotated[str | None, Header()] = None
):
    token = authorization.split("Bearer ")[1]
    email = jwt.decode(token, os.environ.get("JWT_SECRET"), algorithms=["HS256"])[
        "email"
    ]

    if email:
        user = User.get_user_where_email(email)
        Transaction.insert_transaction(
            user=user,
            amount=transaction_rq.amount,
            category=transaction_rq.category,
            description=transaction_rq.description,
        )
        return {"code": 201, "message": f"transaction created for user {user.email}"}
    else:
        return {"code": 401, "message": "unauthorized"}
