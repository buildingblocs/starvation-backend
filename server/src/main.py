from flask import Flask, request, jsonify
from flask.json.provider import JSONProvider
from flask_cors import CORS
from database import Database
from sandbox.sandbox_ai import runner
import orjson
import base64
from io import BytesIO

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

@app.route("/getPlayer/<str:id>", methods=["GET"])
def getPlayer(id: str):
    res = db.retrieve_player(id)
    return jsonify(res)

@app.route("/getGames", methods=["GET"])
def getGames():
    res = db.retrieve_all_games()
    return jsonify(res)

@app.route("/getGame/<int:id>", methods=["GET"])
def getGameDetails(id):
    res = db.retrieve_game(id)
    return jsonify(res)

@app.route("/updateDetails", methods=["POST"])
def updateDetails():
    try:
        data = request.get_json()
        id = data["id"]
        fullname = data["fullname"]
        username = data["username"]
        school = data["school"]
        about = data["about"]
        if(data["pfp"]):
            f = BytesIO()
            f.write(base64.b64decode(data["pfp"]))
            f.seek(0)
            pfp = f.read()
            f.close()
        else:
            with open("src/default.png", "rb") as f:
                    pfp = f.read()
        db.updateUser(id, fullname, username, school, about, pfp)
        return "OK", 200
    except Exception as e:
        return str(e), 200

@app.route("/existsUsername", methods=["GET"])
def existsUsername():
    username = request.args.get("username")
    if username is None: return jsonify({"result": False})
    return jsonify({"result": db.does_username_exist(username)})

@app.route("/deleteUser", methods=["POST"])
def deleteUser():
    data = request.get_json()
    id = data["id"]
    db.delete_user(id)
    return "OK", 200

@app.route("/addUser", methods=["POST"])
def addUser():
    data = request.get_json()
    id = data["id"]
    fullname = data["fullname"]
    username = data["username"]
    school = data["school"]
    about = data["about"]
    if "photo" in data:
        photo = data["photo"].encode("utf-8")
    else:
        with open("src/default.png", "rb") as f:
            photo = f.read()
    db.add_user(id, fullname, username, school, about, photo)
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
