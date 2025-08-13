from tortoise import fields
from tortoise.models import Model


class Activity(Model):
    id = fields.BigIntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="activities", on_delete=fields.CASCADE)
    date = fields.DateField(null=False)
    # status: 1 = done, -1 = not done. Absence of record means not marked
    status = fields.SmallIntField(null=False, default=1)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "activities"
        unique_together = ("user", "date")
        indexes = (("user", "date"),)

    def __str__(self):
        return f"Activity(user={self.user_id}, date={self.date}, status={self.status})" 