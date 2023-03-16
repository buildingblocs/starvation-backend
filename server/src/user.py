from __future__ import annotations
from typing import Union

from flask_login import UserMixin

from database import Database

db = Database()

class User(UserMixin):
    def __init__(self, id_):
        self.id = id_

    @staticmethod
    def get(user_id) -> Union[User, None]:
        exists = db.does_user_exist(user_id)
        if not exists:
            return None
        else:
            return User(user_id)

    @staticmethod
    def create(id_, fullname, username, school, about, photo):
        db.add_user(id_, fullname, username, school, about, photo)
        return User(id_)
