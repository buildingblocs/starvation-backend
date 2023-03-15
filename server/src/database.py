import psycopg
import warnings
from psycopg.rows import dict_row

class Database:
    __slots__ = ["conn"]

    def __init__(self):
        self.conn = psycopg.connect("", row_factory=dict_row)

    def _does_user_exist(self, id: str):
        with self.conn.transaction():
            with self.conn.cursor() as cur:
                cur.execute("SELECT id FROM players WHERE id=%s", (id,))
                return len(cur.fetchall()) == 1

    # adds user to the database
    def add_user(self, id: str, fullname: str):
        if id is None or fullname is None or id == "" or fullname == "":
            warnings.warn("ID and full name cannot be None or empty. No users added.")
        elif self._does_user_exist(id):
            warnings.warn("Another user with the same ID already exists in the database. No users added.")
        else:
            with self.conn.transaction():
                with self.conn.cursor() as cur:
                    cur.execute("INSERT INTO players(id, fullname) values(%s, %s)", (id, fullname))

    # retrieve full list of users and players and returns in descending order of score
    def retrieve_all_players(self):
        with self.conn.transaction():
            with self.conn.cursor(row_factory=dict_row) as cur:
                data = cur.execute("SELECT id, fullname, username, school, about, pfp, score, num_games FROM players").fetchall()
        data = sorted(data, key=lambda x: x["score"], reverse=True)
        return data
    
    def retrieve_all_games(self):
        with self.conn.transaction():
            with self.conn.cursor() as cur:
                data = cur.execute("SELECT id, time, player_1, player_2, finished, result, d1, d2 FROM games").fetchall()
        return data
    
    def retrieve_game(self, gid: int):
        with self.conn.transaction():
            with self.conn.cursor() as cur:
                data = cur.execute("SELECT * FROM games WHERE id=%s", (gid,)).fetchone()
        return data
    
    def submit_code(self, pid: str, code: str) -> None:
        with self.conn.transaction():
            with self.conn.cursor() as cur:
                cur.execute("UPDATE players SET code=%s, error_count=0, last_update=NOW(), games_since_update=0 WHERE id=%s", (code, pid))

    
    def close_connection(self):
        self.conn.close() # note: all commands ran after closing will not work
        
if __name__ == '__main__':
    db = Database()
    print(db.retrieve_all_players())
    db.close_connection()
