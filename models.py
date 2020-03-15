from datetime import datetime

import peewee
from peewee import DoesNotExist
from playhouse.sqliteq import SqliteQueueDatabase

from config import config
from utils import get_message_content

db = SqliteQueueDatabase(database=config["db"]["messages"].get(str), thread_safe=True)


class BaseModel(peewee.Model):
    class Meta:
        database = db


class User(BaseModel):
    uid = peewee.IntegerField()
    username = peewee.CharField(null=True)
    first_name = peewee.CharField(null=True)
    last_name = peewee.CharField(null=True)

    @classmethod
    def from_message(cls, message):
        return cls.create(
            uid=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )

    @classmethod
    def from_chatmember(cls, chat_member):
        return cls.create(
            uid=chat_member.user.id,
            username=chat_member.user.username,
            first_name=chat_member.user.first_name,
            last_name=chat_member.user.last_name,
        )


class Message(BaseModel):
    msg_id = peewee.IntegerField()
    user = peewee.ForeignKeyField(User, backref="messages")
    chat_id = peewee.IntegerField()
    date = peewee.DateTimeField(default=datetime.now)
    content_type = peewee.CharField()
    content_data = peewee.CharField()

    @classmethod
    def from_message(cls, message):
        try:
            user = User.select().where(User.uid == message.from_user.id).get()
        except DoesNotExist:
            user = User.from_message(message)

        return cls.create(
            msg_id=message.message_id,
            user=user,
            chat_id=message.chat.id,
            content_type=message.content_type,
            content_data=get_message_content(message),
        )
