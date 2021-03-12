from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model
from tortoise import fields


class Users(Model):
    username = fields.CharField(max_length=255)
    password_hash = fields.CharField(max_length=255)

    def __repr__(self):
        return f"User(username={self.username}, password_hash={self.password_hash})"


UserPydantic = pydantic_model_creator(Users, name="Users")