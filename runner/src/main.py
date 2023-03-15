import time
from database import Database
from sandbox.sandbox import runner
from elo import calc_elo
import orjson

db = Database()

while True:
    # check for games to run
    print("Finding game...", flush=True)
    game = db.choose_game()
    if game is None:
        time.sleep(5)
        continue

    print("Game found", flush=True)

    game_id, player_1, player_2 = game

    print("Simulation finished", flush=True)
    # simulate game
    result, details = runner(player_1.code, player_2.code)
    if not result:
        # which caused the error?
        result1, _ = runner(player_1.code)
        result2, _ = runner(player_2.code)
        d1 = 0
        d2 = 0
        if not result1:
            db.record_error(player_1.id)
            d1 = -20
        if not result2:
            db.record_error(player_2.id)
            d2 = -20
        db.record_game(game_id, d1, d2, orjson.dumps(details).decode('utf-8'), "error")
    else:
        # update scores
        d1, d2 = calc_elo(player_1.score, player_2.score, details["result"])
        db.record_game(game_id, d1, d2, orjson.dumps(details).decode('utf-8'), "success")
