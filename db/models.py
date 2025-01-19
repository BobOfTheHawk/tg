import enum
from typing import Optional

from sqlalchemy import BigInteger, ForeignKey, Time, create_engine, Boolean, Column, Integer, Float
from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base
from db.utils import CreatedModel


class LanguageEnum(str, enum.Enum):
    EN = 'EN'
    RU = 'RU'
    UZ = 'UZ'


class User(CreatedModel):
    __tablename__ = 'users'
    fullname: Mapped[str] = mapped_column(String(55), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(13))
    language: Mapped[LanguageEnum] = mapped_column(
        Enum(LanguageEnum, name="language_enum"),
        default=LanguageEnum.EN,
        nullable=False
    )
    premium: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    routines = relationship("Routine", back_populates="user")
    notifications = Column(Boolean, default=False)
    moneys = relationship("Money", back_populates="user")


class Routine(CreatedModel):
    __tablename__ = 'routines'
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id', ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    end_time: Mapped[Optional[Time]] = mapped_column(Time)
    days = Column(String, nullable=False)
    user = relationship("User", back_populates="routines")


class Money(CreatedModel):
    __tablename__ = 'moneys'

    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(20), nullable=False)
    days = Column(Integer, nullable=False)

    user = relationship("User", back_populates="moneys")

    def __repr__(self):
        return f"<Money(id={self.id}, amount={self.amount}, currency='{self.currency}', days={self.days})>"


class Moneyplan(CreatedModel):
    __tablename__ = 'Moneyplans'
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    plan_name = Column(String(50), nullable=False)
    plan_price = Column(Integer, nullable=False)
    plan_status = Column(Boolean, nullable=True, default=True)
    days = Column(String, nullable=False)


class Code(CreatedModel):
    __tablename__ = 'Codes'
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(1555), nullable=True)


class Category(CreatedModel):
    __tablename__ = 'categories'

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    photo: Mapped[str] = mapped_column(String(555), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    parent_id = Column(BigInteger, ForeignKey("categories.id"), nullable=True)
    parent = relationship(
        "Category",
        remote_side="Category.id",
        backref="subcategories"
    )


engine = create_engine("postgresql+psycopg2://postgres:1@localhost:5432/mybotmain")
# engine = create_engine("postgresql+psycopg2://postgres:1@pg:5432/mybotmain")

metadata = Base.metadata.create_all(engine)
