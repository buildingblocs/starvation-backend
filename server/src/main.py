from flask import Flask, redirect, request, jsonify, session
from flask.json.provider import JSONProvider
from flask_cors import CORS
from flask_login import LoginManager, login_required, login_user, logout_user
from oauthlib.oauth2 import WebApplicationClient
import requests
from database import Database
from sandbox.sandbox_ai import runner
from user import User
import orjson
import base64
import os
from io import BytesIO

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
db = Database()
CORS(app)

BASE_URL = "https://starvation-api.buildingblocs.sg"

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
GOOGLE_PROVIDER_CONFIG = requests.get(GOOGLE_DISCOVERY_URL).json()

login_manager = LoginManager()
login_manager.init_app(app)

client = WebApplicationClient(GOOGLE_CLIENT_ID)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

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
@login_required
def sendCode():
    data = request.get_json()
    code = data["code"]
    pid = data["id"]
    code = code
    db.submit_code(pid, code)
    return "OK", 200

@app.route("/sendCodeAI", methods=["POST"])
@login_required
def sendCodeAI():
    data = request.get_json()
    code = data["code"]
    level = data["level"]
    code = code
    return jsonify(dict(zip(("status", "output"), runner(code, level))))

@app.route("/getPlayers", methods=["GET"])
def getPlayers():
    res = db.retrieve_all_players()
    return jsonify(res)

@app.route("/getPlayer/<string:id>", methods=["GET"])
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

@app.route("/updateChallenge", methods=["POST"]) # type: ignore
def updateChallenge():
    data = request.get_json()
    id = data["id"]
    level = data["level"]
    code = data["code"]
    db.submit_challenge(id, level, code)
    
@app.route("/getChallengeCode", methods=["GET"]) # type: ignore
def getChallenge():
    level = int(request.args.get("level", "0"))
    id = request.args.get("id", "")
    return jsonify(dict(code=db.get_challenge_code(id, level)))

@app.route("/login")
def login():
    _next = request.args.get("next") # redirect url at the end
    session["next"] = _next

    # Find out what URL to hit for Google login
    authorization_endpoint = GOOGLE_PROVIDER_CONFIG["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=BASE_URL + "/login/callback",
        scope=["openid", "email"],
    )
    return redirect(request_uri)

@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    token_endpoint = GOOGLE_PROVIDER_CONFIG["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=BASE_URL + "/login/callback",
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    client.parse_request_body_response(token_response.text)

    userinfo_endpoint = GOOGLE_PROVIDER_CONFIG["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        id = userinfo_response.json()["email"]
    else:
        return "User email not available or not verified by Google.", 400
    
    user = User(id)

    if not User.get(id):
        with open("src/default.png", "rb") as f:
            pfp = f.read()
        User.create(id, "", "", "", "", pfp)

    login_user(user)

    # vulnerable to open redirect but welp
    return redirect(session["next"])

@app.route("/updateDetails", methods=["POST"])
@login_required
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
@login_required
def deleteUser():
    data = request.get_json()
    id = data["id"]
    db.delete_user(id)
    return "OK", 200

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return "OK", 200

# @app.route("/addUser", methods=["POST"])
# def addUser():
#     data = request.get_json()
#     id = data["id"]
#     fullname = data["fullname"]
#     username = data["username"]
#     school = data["school"]
#     about = data["about"]
#     if "photo" in data:
#         photo = data["photo"].encode("utf-8")
#     else:
#         with open("src/default.png", "rb") as f:
#             photo = f.read()
#     db.add_user(id, fullname, username, school, about, photo)
#     return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
