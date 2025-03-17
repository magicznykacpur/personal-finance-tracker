from pydantic import BaseModel


class UserRQ(BaseModel):
    email: str
    password: str


class TransactionRQ(BaseModel):
    amount: float
    category: str
    description: str

class CategoriesLimitRQ(BaseModel):
    food: float | None = None
    rent: float | None = None
    luxury: float | None = None
    other: float | None = None