from typing import Tuple, Union
import psycopg
import warnings
from psycopg.rows import dict_row
import dataclasses

@dataclasses.dataclass
class SimulationPlayer:
    id: str
    code: str
    score: int

class Database:
    __slots__ = ["conn"]

    def __init__(self):
        self.conn = psycopg.connect("", row_factory=dict_row)
        
        # create table with ID (email address), full name, score
        with self.conn.transaction():
            with self.conn.cursor() as cur:
                cur.execute("""CREATE TABLE IF NOT EXISTS players (
                                id varchar(255) not null PRIMARY KEY,
                                fullname varchar(255),
                                username varchar(255) not null unique,
                                school varchar(100),
                                about varchar(255),
                                pfp bytea,
                                score int not null default 1000,
                                code text,
                                error_count int not null default 0,
                                last_update timestamp with time zone not null default now(),
                                num_games int not null default 0,
                                games_since_update int not null default 0)""")
                cur.execute("""CREATE TABLE IF NOT EXISTS games (
                                id SERIAL PRIMARY KEY,
                                time timestamp with time zone not null default now(),
                                player_1 varchar(255) not null references players(id) on delete cascade,
                                player_2 varchar(255) not null references players(id) on delete cascade,
                                finished boolean NOT NULL default false,
                                result varchar(255),
                                d1 INT,
                                d2 INT,
                                replay jsonb,
                                CONSTRAINT details_if_finished CHECK ( NOT (finished AND (result IS NULL OR d1 IS NULL OR d2 IS NULL OR replay IS NULL ))) 
                            )""")
                cur.execute("""CREATE TABLE IF NOT EXISTS levels (
                                id varchar(255) not null references players(id) on delete cascade,
                                level INT,
                                code text,
                                PRIMARY KEY(id, level)
                            )""")
                cur.execute("""IF COL_LENGTH(levels, winner) IS NULL
                            BEGIN
                                ALTER TABLE levels
                                ADD winner BOOLEAN default false
                            END""")


    def _does_user_exist(self, id: str):
        with self.conn.transaction():
            with self.conn.cursor() as cur:
                cur.execute("SELECT id FROM players WHERE id=%s", (id,))
                return len(cur.fetchall()) == 1

    # updates user's score
    def update_score(self, id: str, delta: int):
        if not self._does_user_exist(id):
            warnings.warn("ID does not exist in database. No players affected.")
        elif not isinstance(delta, int):
            warnings.warn("Score must be an integer. No players affected.")
        else:
            with self.conn.transaction():
                with self.conn.cursor() as cur:
                    cur.execute("UPDATE players SET score=score+%s WHERE id=%s", (delta, id))
    
    def record_error(self, pid: str):
        with self.conn.transaction():
            with self.conn.cursor() as cur:
                cur.execute("UPDATE players SET error_count=error_count+1 WHERE id=%s", (pid,))
    
    def record_game(self, game_id: int, d1: int, d2: int, details: str, result: str) -> None:
        with self.conn.transaction():
            with self.conn.cursor() as cur:
                data = cur.execute("UPDATE games SET finished=true, result=%s, d1=%s, d2=%s, replay=%s WHERE id=%s RETURNING player_1, player_2", (result, d1, d2, details, game_id)).fetchall()
                if len(data) == 0:
                    raise ValueError("Game ID not found")
                player_1 = data[0]["player_1"]
                player_2 = data[0]["player_2"]

        self.update_score(player_1, d1)
        self.update_score(player_2, d2)

    def choose_game(self) -> Union[None, Tuple[int, SimulationPlayer, SimulationPlayer]]:
        # Greedy algorithm to choose a pair of players to play
        with self.conn.transaction():
            with self.conn.cursor() as cur:
                # acquire lock
                cur.execute("LOCK TABLE players IN ACCESS EXCLUSIVE MODE")
                cur.execute("LOCK TABLE games IN ACCESS EXCLUSIVE MODE")
                # check for any orphaned games
                data = cur.execute("SELECT id, player_1, player_2 FROM games WHERE NOT finished AND NOW() - time > INTERVAL '3 minutes'").fetchone()
                if data:
                    player_info = cur.execute("SELECT id, code, score FROM players WHERE id=%s OR id=%s", (data["player_1"], data["player_2"])).fetchall()
                    player_1 = SimulationPlayer(player_info[0]["id"], player_info[0]["code"], player_info[0]["score"])
                    player_2 = SimulationPlayer(player_info[1]["id"], player_info[1]["code"], player_info[1]["score"])
                    return data["id"], player_1, player_2
                # get the player with the least games played since last update, and with non-null code and < 3 errors
                data = cur.execute("SELECT id, code, score, last_update FROM players WHERE error_count < 3 AND code IS NOT NULL ORDER BY games_since_update ASC LIMIT 1").fetchall()
                if len(data) == 0:
                    return None  # no players available
                player_1 = SimulationPlayer(data[0]["id"], data[0]["code"], data[0]["score"])
                last_update = data[0]["last_update"]
                # get all players who have already played with player 1 since the last update
                data = cur.execute("SELECT player_1, player_2 FROM games WHERE (player_1=%s OR player_2=%s) AND time > %s", (player_1.id, player_1.id, last_update)).fetchall()
                have_played = {row["player_1"] for row in data} | {row["player_2"] for row in data} | {player_1.id}
                # get a valid player 2 that has closest score to player 1
                data = cur.execute("SELECT id, code, score FROM players WHERE NOT id = ANY(%s) AND error_count < 3 AND code IS NOT NULL ORDER BY ABS(%s - score) ASC LIMIT 1", (list(have_played), player_1.score)).fetchall()
                if len(data) == 0:
                    return None  # no players available
                player_2 = SimulationPlayer(data[0]["id"], data[0]["code"], data[0]["score"])
                # insert in progress game, add game count to both players
                data = cur.execute("INSERT INTO games (player_1, player_2) VALUES (%s, %s) RETURNING id", (player_1.id, player_2.id)).fetchone()
                if not data:
                    raise RuntimeError("insert failed???")
                game_id = data["id"]
                cur.execute("UPDATE players SET num_games=num_games+1, games_since_update=games_since_update+1 WHERE id=%s OR id=%s", (player_1.id, player_2.id))
        
        return game_id, player_1, player_2

    
    def close_connection(self):
        self.conn.close() # note: all commands ran after closing will not work
