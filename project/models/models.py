from sqlalchemy import INTEGER, Column, ForeignKey, String, Boolean, Integer, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    id = Column(INTEGER(), primary_key=True)


class Product(BaseModel):
    __tablename__ = "products"
    title = Column(String(45), nullable=False)
    description = Column(String(250), nullable=False)
    price = Column(Integer, nullable=False)

    def to_dict(self):
        return {'id': self.id,
                "title": self.title,
                "description": self.description,
                'price': self.price}


products = Product.__table__


class User(BaseModel):
    __tablename__ = "users"

    username = Column(String(15), unique=True, nullable=False)
    is_active = Column(Boolean(), default=False)
    is_admin = Column(Boolean(), default=False)
    password_hash = Column(Text(), nullable=False)
    token = Column(String, nullable=False)


    def to_dict(self):
        return {'id': self.id,
                "username": self.username,
                "is_active": self.is_active,
                'is_admin': self.is_admin}


users = User.__table__


class Account(BaseModel):
    __tablename__ = "accounts"

    bill_id = Column(String, nullable=False, unique=True)
    balance = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id"))

    def to_dict(self):
        return {'id': self.id,
                "bill_id": self.bill_id,
                "balance": self.balance,
                'user_id': self.user_id}


accounts = Account.__table__


class Transaction(BaseModel):
    __tablename__ = "transactions"

    amount = Column(Integer, nullable=False)
    bill_id_account = Column(String, nullable=False)

    def to_dict(self):
        return {'id': self.id,
                "amount": self.amount,
                "bill_id_account": self.bill_id_account}
