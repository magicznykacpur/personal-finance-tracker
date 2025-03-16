import os
from typing import Annotated
from database.entities import Transaction, User
from request import TransactionRQ, UserRQ
from fastapi import FastAPI, HTTPException, Header
from bcrypt import checkpw
import jwt

from utils import extract_email

app = FastAPI()

env = open(".env.local").read().split("=")
os.environ[env[0]] = env[1]


@app.get("/user")
def get_users():
    return User.get_all_users()


@app.post("/register", status_code=201)
def register(user_rq: UserRQ):
    try:
        User.insert_user(email=user_rq.email, password=user_rq.password)
        return f"user {user_rq.email} created"
    except Exception as e:
        if str(e) == "UNIQUE constraint failed: user.email":
            raise HTTPException(
                status_code=400, detail=f"user {user_rq.email} already exists"
            )
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
        raise HTTPException(status_code=401, detail="unauthorized")


@app.get("/transaction")
def get_all_transactions_by_user(authorization: Annotated[str | None, Header()] = None):
    email = extract_email(authorization)

    if email:
        user = User.get_user_where_email(email)
        transactions = Transaction.get_all_transactions_by_user(user)
        return transactions
    else:
        raise HTTPException(status_code=401, detail="unauthorized")


@app.get("/transaction/")
def get_transactions_from_to(
    from_date: str,
    to_date: str,
    authorization: Annotated[str | None, Header()] = None,
):
    email = extract_email(authorization)

    if email:
        user = User.get_user_where_email(email)
        transactions = Transaction.get_transactions_between(
            user=user, from_date=from_date, to_date=to_date
        )
        return transactions
    else:
        raise HTTPException(status_code=401, detail="unauthorized")


@app.post("/transaction", status_code=201)
def create_transactions(
    transaction_rq: TransactionRQ, authorization: Annotated[str | None, Header()] = None
):
    email = extract_email(authorization)

    if email:
        if transaction_rq.category not in ["food", "rent", "luxury", "other"]:
            raise HTTPException(
                status_code=400,
                detail=f"wrong transaction category -> {transaction_rq.category}",
            )

        user = User.get_user_where_email(email)
        Transaction.insert_transaction(
            user=user,
            amount=transaction_rq.amount,
            category=transaction_rq.category,
            description=transaction_rq.description,
        )
        return f"transaction created for user {user.email}"
    else:
        raise HTTPException(status_code=401, detail="unauthorized")
