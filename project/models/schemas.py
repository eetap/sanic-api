from pydantic import BaseModel, Field, validator, constr, UUID4
from typing import Optional


class ProductBase(BaseModel):
    title: str
    description: str
    price: int = Field(gt=1)


class ProductPatch(BaseModel):
    title: Optional[str]
    description: Optional[str]
    price: Optional[int]


class UserLoginBase(BaseModel):
    username: str
    password: str


class UserIn(BaseModel):
    username: str
    password1: constr(min_length=8)
    password2: str

    @validator("password2")
    def password_match(cls, v2, values, **kwargs):
        if 'password1' in values and v2 != values['password1']:
            raise ValueError("Passwords do not match")
        return v2


class PaymentBase(BaseModel):
    signature: str
    transaction_id: int
    user_id: int
    bill_id: UUID4
    amount: int
