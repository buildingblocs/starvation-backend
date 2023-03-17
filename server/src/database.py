from psycopg import AsyncConnection
import warnings
from psycopg.rows import dict_row
import base64

class Database:
    __slots__ = ["conn"]

    def __init__(self):
        pass

    async def init_connection(self):
        self.conn = await AsyncConnection.connect("", row_factory=dict_row)
        async with self.conn.transaction():
            async with self.conn.cursor() as cur:
                await cur.execute("""CREATE TABLE IF NOT EXISTS resolver (code uuid PRIMARY KEY default gen_random_uuid(), id varchar(255) not null)""")

    async def add_resolver_id(self, id: str):
        async with self.conn.transaction():
            async with self.conn.cursor() as cur:
                data = await (await cur.execute("INSERT INTO resolver(id) values(%s) RETURNING code", (id,))).fetchone()
        return data["code"] if data else None
    
    async def resolve_code(self, code: str):
        async with self.conn.transaction():
            async with self.conn.cursor() as cur:
                data = await (await cur.execute("SELECT id FROM resolver WHERE code=%s", (code,))).fetchone()
                if data is None:
                    return None
                await cur.execute("DELETE FROM resolver WHERE code=%s", (code,))
                return data["id"]
    
    async def does_user_exist(self, id: str):
        async with self.conn.transaction():
            async with self.conn.cursor() as cur:
                await cur.execute("SELECT id FROM players WHERE id=%s", (id,))
                return len(await cur.fetchall()) == 1
            
    async def does_username_exist(self, username: str):
        async with self.conn.transaction():
            async with self.conn.cursor() as cur:
                await cur.execute("SELECT username FROM players WHERE username=%s", (username, ))
                return len(await cur.fetchall()) == 1
            
    async def updateUser(self, id: str, fullname: str, username: str, school: str, about: str, pfp: bytes):
        if not await self.does_user_exist(id):
            warnings.warn("This user doesn't exist.")
        else:
            async with self.conn.transaction():
                async with self.conn.cursor() as cur:
                    await cur.execute("UPDATE players SET fullname=%s, username=%s, school=%s, about=%s, pfp=%s WHERE id=%s", (fullname, username, school, about, pfp, id))

    # adds user to the database
    async def add_user(self, id: str, fullname: str, username: str, school: str, about: str, photo: bytes):
        if id is None or fullname is None:
            warnings.warn("ID and full name cannot be None or empty. No users added.")
        elif await self.does_user_exist(id):
            warnings.warn("Another user async with the same ID already exists in the database. No users added.")
        else:
            async with self.conn.transaction():
                async with self.conn.cursor() as cur:
                    await cur.execute("INSERT INTO players(id, fullname, username, school, about, pfp) values(%s, %s, %s, %s, %s, %s)", (id, fullname, username, school, about, photo))

    # retrieve full list of users and players and returns in descending order of score
    async def retrieve_all_players(self):
        async with self.conn.transaction():
            async with self.conn.cursor(row_factory=dict_row) as cur:
                data = await (await cur.execute("SELECT id, fullname, username, school, about, pfp, score, num_games FROM players")).fetchall()
        data = sorted(data, key=lambda x: x["score"], reverse=True)
        for row in data:
            row["pfp"] = base64.b64encode(row["pfp"]).decode("utf-8")
        return data
    
    async def retrieve_all_games(self):
        async with self.conn.transaction():
            async with self.conn.cursor() as cur:
                data = await (await cur.execute("SELECT id, time, player_1, player_2, finished, result, d1, d2 FROM games")).fetchall()
        return data
    
    async def retrieve_player(self, id: str):
        async with self.conn.transaction():
            async with self.conn.cursor() as cur:
                data = await (await cur.execute("SELECT id, fullname, username, school, about, pfp, score, num_games FROM players WHERE id=%s", (id,))).fetchone()
        if data is None:
            return data
        data["pfp"] = base64.b64encode(data["pfp"]).decode("utf-8")
        return data
    
    async def retrieve_game(self, gid: int):
        async with self.conn.transaction():
            async with self.conn.cursor() as cur:
                data = await (await cur.execute("SELECT * FROM games WHERE id=%s", (gid,))).fetchone()
        return data
    
    async def submit_code(self, pid: str, code: str) -> None:
        async with self.conn.transaction():
            async with self.conn.cursor() as cur:
                await cur.execute("UPDATE players SET code=%s, error_count=0, last_update=NOW(), games_since_update=0 WHERE id=%s", (code, pid))

    async def delete_user(self, id: str):
        async with self.conn.transaction():
            async with self.conn.cursor() as cur:
                await cur.execute("DELETE FROM players WHERE id=%s", (id,))
                
    async def submit_challenge(self, id: str, level: int, code: str, winner: bool = False):
        async with self.conn.transaction():
            async with self.conn.cursor() as cur:
                # Step 1: Check if {id} has submitted to {level} before
                await cur.execute("SELECT code FROM levels WHERE id=%s and level=%s", (id, level))
                if len(await cur.fetchall()): # has been uploaded before
                    # Update the existing record
                    await cur.execute("UPDATE levels SET code=%s, winner=%s, lastUpdated=CURRENT_TIMESTAMP WHERE id=%s and level=%s", (code, winner, id, level))
                else: # no records
                    # Create a new record
                    await cur.execute("INSERT INTO levels (id, level, code, winner) VALUES (%s, %s, %s, %s)", (id, level, code, winner))

    async def get_challenge_code(self, id: str, level: int) -> str:
        async with self.conn.transaction():
            async with self.conn.cursor() as cur:
                await cur.execute("SELECT code FROM levels WHERE id=%s and level=%s", (id, level))
                result = await cur.fetchall()
        
        if len(result): return result[0]["code"]
        else: return ""
    
    async def retrieve_challenges(self, id: str):
        async with self.conn.transaction():
            async with self.conn.cursor() as cur:
                await cur.execute("SELECT id, lastUpdated, winner FROM levels WHERE id=%s", (id,))
                result = await cur.fetchall()
        return result
    
    async def close_connection(self):
        await self.conn.close() # note: all commands ran after closing will not work
        
