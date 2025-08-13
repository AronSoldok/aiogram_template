from tortoise import fields
from tortoise.models import Model


class UserStats(Model):
    id = fields.BigIntField(pk=True)
    user = fields.OneToOneField("models.User", related_name="user_stats", on_delete=fields.CASCADE)
    total_done = fields.IntField(null=False, default=0)
    total_not_done = fields.IntField(null=False, default=0)
    current_streak = fields.IntField(null=False, default=0)
    max_streak = fields.IntField(null=False, default=0)
    goal_monthly = fields.IntField(null=False, default=0)
    reminder_time = fields.CharField(max_length=5, null=True)  # HH:MM
    is_registered = fields.BooleanField(null=False, default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "user_stats"
        indexes = (("user",),)

    def __str__(self):
        return f"UserStats(user={self.user_id}, streak={self.current_streak}/{self.max_streak}, done={self.total_done})" 