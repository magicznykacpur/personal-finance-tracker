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
