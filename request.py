from pydantic import BaseModel


class UserRQ(BaseModel):
    email: str
    password: str


class TransactionRQ(BaseModel):
    amount: float
    category: str
    description: str
