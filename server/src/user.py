import dataclasses

from database import Database

db = Database()

@dataclasses.dataclass
class User:
    id: str
