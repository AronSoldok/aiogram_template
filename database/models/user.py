from .base import Base
from tortoise import fields


class User(Base):
    tg_id = fields.BigIntField(unique=True)
    username = fields.CharField(max_length=100, null=True)
    nickname = fields.CharField(max_length=100, null=True)

    class Meta:
        table = "users"

    def __str__(self):
        return f"Пользователь {self.tg_id} ({self.full_user_name})"