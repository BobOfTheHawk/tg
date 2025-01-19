import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, BigInteger, String
from sqlalchemy import delete as sqlalchemy_delete
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.future import select

from db import db, Base

db.init()


# ----------------------------- ABSTRACTS ----------------------------------
class AbstractClass:
    @staticmethod
    async def commit():
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise

    @classmethod
    async def create(cls, **kwargs):
        object_ = cls(**kwargs)
        db.add(object_)
        await cls.commit()
        return object_

    @classmethod
    async def update(cls, id_, **kwargs):
        query = (
            sqlalchemy_update(cls)
            .where(cls.id == id_)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        await db.execute(query)
        await cls.commit()

    @classmethod
    async def get(cls, id_):
        query = select(cls).where(cls.id == id_)
        objects = await db.execute(query)
        object_ = objects.first()
        if object_:
            return object_[0]
        else:
            return []

    @classmethod
    async def get_user_id(cls, id_):
        query = select(cls).where(cls.user_id == id_)
        objects = await db.execute(query)
        object_ = objects.first()
        if object_:
            return object_[0]
        else:
            return []

    @classmethod
    async def delete(cls, id_):
        query = sqlalchemy_delete(cls).where(cls.id == id_)
        await db.execute(query)
        await cls.commit()
        return True

    @classmethod
    async def get_all(cls, order_fields: list[str] = None):
        query = select(cls)
        if order_fields:
            query = query.order_by(*order_fields)
        objects = await db.execute(query)
        result = []
        for i in objects.all():
            result.append(i[0])
        return result

    @classmethod
    async def get_all_copy(cls, user_id: int = None, order_fields: list[str] = None):
        query = select(cls)
        if user_id is not None:
            query = query.where(cls.user_id == user_id)
        if order_fields:
            query = query.order_by(*order_fields)
        objects = await db.execute(query)
        return [obj[0] for obj in objects.all()]


class CreatedModel(Base, AbstractClass):
    __abstract__ = True
    id = Column(BigInteger, primary_key=True, autoincrement=True, unique=True)
    created_at = Column(DateTime(), default=datetime.datetime.utcnow)
    updated_at = Column(DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
