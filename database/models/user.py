from .base import Base
from tortoise import fields


class User(Base):
    tg_id = fields.BigIntField(unique=True)
    username = fields.CharField(max_length=100, null=True)
    nickname = fields.CharField(max_length=100, null=True)
    timezone = fields.CharField(max_length=64, null=False, default="UTC")

    class Meta:
        table = "users"

    def __str__(self):
        display_name = self.nickname or self.username or "anonymous"
        return f"User {self.tg_id} ({display_name})"