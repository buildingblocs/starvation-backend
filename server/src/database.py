import psycopg2
import warnings

class Database:
    def __init__(self, table_name: str, db_file: str):
        self.table_name = table_name
        self.conn = psycopg2.connect(db_file)
        # create table with ID (email address), full name, score
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (
                                id varchar(255) not null PRIMARY KEY, 
                                fullname varchar(255), 
                                score int not null)""") 

    def _does_user_exist(self, id: str):
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(f"SELECT * FROM {self.table_name} WHERE id='{id}'")
                return len(cur.fetchall()) == 1

    # adds user to the database
    def add_user(self, id: str, fullname: str, score: int = 0):
        if id is None or fullname is None or id == "" or fullname == "":
            warnings.warn("ID and full name cannot be None or empty. No users added.")
        elif self._does_user_exist(id):
            warnings.warn("Another user with the same ID already exists in the database. No users added.")
        elif not isinstance(score, int):
            warnings.warn("Score must be an integer. No scores affected.")
        else:
            with self.conn:
                with self.conn.cursor() as cur:
                    cur.execute(f"INSERT INTO {self.table_name} values('{id}', '{fullname}', {score})")

    # updates user's score
    def update_score(self, id: str, score: int):
        if not self._does_user_exist(id):
            warnings.warn("ID does not exist in database. No scores affected.")
        elif not isinstance(score, int):
            warnings.warn("Score must be an integer. No scores affected.")
        else:
            with self.conn:
                with self.conn.cursor() as cur:
                    cur.execute(f"UPDATE {self.table_name} SET score={score} WHERE id='{id}'")

    # retrieve full list of users and scores and returns in descending order of score
    def retrieve_all_scores(self):
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(f"SELECT * FROM {self.table_name}")
                data = cur.fetchall()
        data = sorted(data, key=lambda x: x[-1], reverse=True)
        return data
    
    def close_connection(self):
        self.conn.close() # note: all commands ran after closing will not work
        
if __name__ == '__main__':
    db = Database("scores", "") # ! please save the file properly somewhere
    print(db.retrieve_all_scores())
    db.close_connection()
