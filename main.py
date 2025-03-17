from datetime import datetime
from functools import reduce
import os
from typing import Annotated
from database.entities import Transaction, User
from request import CategoriesLimitRQ, TransactionRQ, UserRQ
from fastapi import FastAPI, HTTPException, Header
from bcrypt import checkpw
import jwt

from utils import extract_email, print_fail, print_warning

app = FastAPI()

env = open(".env.local").read().split("=")
os.environ[env[0]] = env[1]


@app.get("/user")
def get_users():
    return User.get_all_users()


@app.get("/me")
def get_my_data(authorization: Annotated[str | None, Header()] = None):
    email = extract_email(authorization)

    if email:
        user = User.get_user_where_email(email)
        transactions = list(
            map(
                lambda transaction: {
                    "amount": transaction.amount,
                    "category": transaction.category,
                    "description": transaction.description,
                    "created_at": transaction.created_at,
                },
                Transaction.get_all_transactions_by_user(user),
            )
        )
        return {
            "email": user.email,
            "created_at": user.created_at,
            "budget": user.budget,
            "categories_limit": user.categories_limit,
            "transactions": transactions,
        }
    else:
        raise HTTPException(status_code=401, detail="unauthorized")


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


@app.patch("/user")
def set_budget(budget: float, authorization: Annotated[str | None, Header()] = None):
    email = extract_email(authorization)

    if budget < 0:
        raise HTTPException(status_code=400, detail="cannot set negative budget")

    if email:
        user = User.get_user_where_email(email)
        User.set_user_budget(user.id, budget)
        return f"budget of {budget} for {email} was set successfully"
    else:
        raise HTTPException(status_code=401, detail="unauthorized")


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


@app.get("/transaction/{id}")
def get_transaction_by_id(
    id: int, authorization: Annotated[str | None, Header()] = None
):
    email = extract_email(authorization)

    if email:
        user = User.get_user_where_email(email)
        try:
            transaction = Transaction.get_transaction_where_user_and_id(
                user=user, transaction_id=id
            )

            return transaction
        except Exception as e:
            raise HTTPException(status_code=404, detail="transaction not found")
    else:
        raise HTTPException(status_code=401, detail="unauthorized")


@app.delete("/transaction/{id}")
def delete_transaction_by_id(
    id: int, authorization: Annotated[str | None, Header()] = None
):
    email = extract_email(authorization)

    if email:
        user = User.get_user_where_email(email)
        try:
            transaction = Transaction.get_transaction_where_user_and_id(
                user=user, transaction_id=id
            )
            transaction.delete_instance()
            return f"transaction -> {id} <- deleted"
        except Exception as e:
            raise HTTPException(status_code=404, detail="transaction not found")
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
        if user.budget < transaction_rq.amount:
            raise HTTPException(status_code=400, detail="insufficient budget")

        budget_for_category = user.categories_limit[transaction_rq.category]
        if (
            budget_for_category - transaction_rq.amount <= 10
            and budget_for_category - transaction_rq.amount > 0
        ):
            print_warning(
                f"You're about to exceed limit for {transaction_rq.category} category..."
            )
        elif budget_for_category - transaction_rq.amount < 0:
            print_fail(f"Budget for {transaction_rq.category} category exceeded!")

        Transaction.insert_transaction(
            user=user,
            amount=transaction_rq.amount,
            category=transaction_rq.category,
            description=transaction_rq.description,
        )
        User.set_user_budget(
            user_id=user.id, budget=user.budget - transaction_rq.amount
        )
        users_limits = user.categories_limit
        users_limits[transaction_rq.category] -= transaction_rq.amount
        User.set_users_categories_limit(user_id=user.id, categories_limit=users_limits)

        return f"transaction created for user {user.email}"
    else:
        raise HTTPException(status_code=401, detail="unauthorized")


@app.get("/report/month-and-category")
def get_month_report_for_category(
    month: str, category: str, authorization: Annotated[str | None, Header()] = None
):
    email = extract_email(authorization)

    if email:
        user = User.get_user_where_email(email)
        transactions = Transaction.get_transactions_where_user_and_month_and_category(
            user=user, month=month, category=category
        )

        total = round(reduce(lambda x, y: x + y.amount, transactions, 0), 2)
        current_year = datetime.now().year

        if total == 0:
            return {
                "total": total,
                "message": f"you've spent 0 on `{category}` in {current_year}-{month}. bloody legend.",
            }
        else:
            return {
                "total": total,
                "message": f"in {current_year}-{month} you've spent a total of {total} on `{category}`. damn...",
            }
    else:
        raise HTTPException(status_code=401, detail="unauthorized")


@app.get("/report/month")
def get_month_total(month: str, authorization: Annotated[str | None, Header()] = None):
    email = extract_email(authorization)

    if email:
        user = User.get_user_where_email(email)
        transactions = Transaction.transactions_where_user_and_month(
            user=user, month=month
        )

        total = round(reduce(lambda x, y: x + y.amount, transactions, 0), 2)
        current_year = datetime.now().year

        if total == 0:
            return {
                "total": total,
                "message": f"you've spent `0` in {current_year}-{month}. bloody legend.",
            }
        else:
            return {
                "total": total,
                "message": f"you've spent `{total}` in {current_year}-{month}. damn...",
            }
    else:
        raise HTTPException(status_code=401, detail="unauthorized")


@app.patch("/categories-limit")
def set_users_categories_limit(
    categories_limit: CategoriesLimitRQ,
    authorization: Annotated[str | None, Header()] = None,
):
    email = extract_email(authorization)

    if email:
        user = User.get_user_where_email(email)
        users_limits = user.categories_limit
        new_limits = {}

        if categories_limit.food:
            new_limits["food"] = categories_limit.food
        if categories_limit.rent:
            new_limits["rent"] = categories_limit.rent
        if categories_limit.luxury:
            new_limits["luxury"] = categories_limit.luxury
        if categories_limit.other:
            new_limits["other"] = categories_limit.other

        users_limits.update(new_limits)
        user.categories_limit = users_limits
        user.save()

        return {"new_users_limits": users_limits, "message": "limits updated"}
    else:
        raise HTTPException(status_code=401, detail="unauthorized")
