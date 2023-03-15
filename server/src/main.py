from flask import Flask, request, jsonify
from flask.json.provider import JSONProvider
from flask_cors import CORS
from database import Database
from sandbox.sandbox_ai import runner
import orjson

app = Flask(__name__)
app.secret_key = "super_secret_key"
db = Database()
CORS(app)

class ORJSONProvider(JSONProvider):
    def __init__(self, *args, **kwargs):
        self.options = kwargs
        super().__init__(*args, **kwargs)
    
    def loads(self, s, **_):
        return orjson.loads(s)
    
    def dumps(self, obj, **_):
        # decode back to str, as orjson returns bytes
        return orjson.dumps(obj, option=orjson.OPT_NON_STR_KEYS).decode('utf-8')

app.json = ORJSONProvider(app)

@app.route("/")
def home():
    return f"<h1>Starvation Backend :)</h1>"

@app.route("/sendCode", methods=["POST"])
def sendCode():
    data = request.get_json()
    code = data["code"]
    pid = data["id"]
    code = "from gameAPI import enemiesWithinRange, getFriendlyTroops, distanceToEntity\n\n" + code
    db.submit_code(pid, code)
    return "OK", 200

@app.route("/sendCodeAI", methods=["POST"])
def sendCodeAI():
    data = request.get_json()
    code = data["code"]
    level = data["level"]
    code = "from gameAPI import enemiesWithinRange, getFriendlyTroops, distanceToEntity\n\n" + code
    return jsonify(dict(zip(("status", "output"), runner(code, level))))

@app.route("/getPlayers", methods=["GET"])
def getPlayers():
    res = db.retrieve_all_players()
    return jsonify(res)

@app.route("/getGames", methods=["GET"])
def getGames():
    res = db.retrieve_all_games()
    return jsonify(res)

@app.route("/getGame/<int:id>", methods=["GET"])
def getGameDetails(id):
    res = db.retrieve_game(id)
    return jsonify(res)

@app.route("/addUser", methods=["POST"])
def addUser():
    data = request.get_json()
    id = data["id"]
    fullname = data["fullname"]
    db.add_user(id, fullname)
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
