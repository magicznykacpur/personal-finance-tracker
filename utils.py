from datetime import datetime
import os
import jwt
from typing import Annotated
from fastapi import Header


def extract_email(authorization: Annotated[str | None, Header()] = None):
    if authorization:
        token = authorization.split("Bearer ")[1]
        email = jwt.decode(token, os.environ.get("JWT_SECRET"), algorithms=["HS256"])[
            "email"
        ]
        return email

def get_dates_around_month(month: str):
    current_year = datetime.now().year
    first_of_month = datetime.fromisoformat(f"{current_year}-{month}-01")
    
    is_not_december = first_of_month.month < 12
    next_month = first_of_month.month + 1 if is_not_december else 1

    iso_next_month = f"{current_year}-0{next_month}-01" if next_month < 10 else f"{current_year}-{next_month}-01"

    return first_of_month, datetime.fromisoformat(iso_next_month)