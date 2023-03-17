import psycopg
import warnings
from psycopg.rows import dict_row
import base64

class Database:
    __slots__ = ["conn"]

    def __init__(self):
        self.conn = psycopg.connect("", row_factory=dict_row)

    def does_user_exist(self, id: str):
        with self.conn.transaction():
            with self.conn.cursor() as cur:
                cur.execute("SELECT id FROM players WHERE id=%s", (id,))
                return len(cur.fetchall()) == 1
            
    def does_username_exist(self, username: str):
        with self.conn.transaction():
            with self.conn.cursor() as cur:
                cur.execute("SELECT username FROM players WHERE username=%s", (username, ))
                return len(cur.fetchall()) == 1
            
    def updateUser(self, id: str, fullname: str, username: str, school: str, about: str, pfp: bytes):
        if not self.does_user_exist(id):
            warnings.warn("This user doesn't exist.")
        else:
            with self.conn.transaction():
                with self.conn.cursor() as cur:
                    cur.execute("UPDATE players SET fullname=%s, username=%s, school=%s, about=%s, pfp=%s WHERE id=%s", (fullname, username, school, about, pfp, id))

    # adds user to the database
    def add_user(self, id: str, fullname: str, username: str, school: str, about: str, photo: bytes):
        if id is None or fullname is None:
            warnings.warn("ID and full name cannot be None or empty. No users added.")
        elif self.does_user_exist(id):
            warnings.warn("Another user with the same ID already exists in the database. No users added.")
        else:
            with self.conn.transaction():
                with self.conn.cursor() as cur:
                    cur.execute("INSERT INTO players(id, fullname, username, school, about, pfp) values(%s, %s, %s, %s, %s, %s)", (id, fullname, username, school, about, photo))

    # retrieve full list of users and players and returns in descending order of score
    def retrieve_all_players(self):
        with self.conn.transaction():
            with self.conn.cursor(row_factory=dict_row) as cur:
                data = cur.execute("SELECT id, fullname, username, school, about, pfp, score, num_games FROM players").fetchall()
        data = sorted(data, key=lambda x: x["score"], reverse=True)
        for row in data:
            row["pfp"] = base64.b64encode(row["pfp"]).decode("utf-8")
        return data
    
    def retrieve_all_games(self):
        with self.conn.transaction():
            with self.conn.cursor() as cur:
                data = cur.execute("SELECT id, time, player_1, player_2, finished, result, d1, d2 FROM games").fetchall()
        return data
    
    def retrieve_player(self, id: str):
        with self.conn.transaction():
            with self.conn.cursor() as cur:
                data = cur.execute("SELECT id, fullname, username, school, about, pfp, score, num_games FROM players WHERE id=%s", (id,)).fetchone()
        if data is None:
            return data
        data["pfp"] = base64.b64encode(data["pfp"]).decode("utf-8")
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

    def delete_user(self, id: str):
        with self.conn.transaction():
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM players WHERE id=%s", (id,))
                
    def submit_challenge(self, id: str, level: int, code: str):
        with self.conn.transaction():
            with self.conn.cursor() as cur:
                # Step 1: Check if {id} has submitted to {level} before
                cur.execute("SELECT code FROM levels WHERE id=%s and level=%s", (id, level))
                if len(cur.fetchall()): # has been uploaded before
                    # Update the existing record
                    cur.execute("UPDATE levels SET code=%s WHERE id=%s and level=%s", (code, id, level))
                else: # no records
                    # Create a new record
                    cur.execute("INSERT INTO levels (id, level, code) VALUES (%s, %s, %s)", (id, level, code))

    def get_challenge_code(self, id: str, level: int) -> str:
        with self.conn.transaction():
            with self.conn.cursor() as cur:
                cur.execute("SELECT code FROM levels WHERE id=%s and level=%s", (id, level))
                result = cur.fetchall()
        
        if len(result): return result[0]["code"]
        else: return ""
    
    def retrieve_challenges(self, id: str) -> str:
        with self.conn.transaction():
            with self.conn.cursor() as cur:
                cur.execute("SELECT id FROM levels WHERE id=%s", (id,))
                result = cur.fetchall()
        return result
    
    def close_connection(self):
        self.conn.close() # note: all commands ran after closing will not work
        
if __name__ == '__main__':
    db = Database()
    print(db.retrieve_all_players())
    db.close_connection()
