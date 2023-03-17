from datetime import datetime, timedelta, timezone
import uuid
from flask import Flask, make_response, redirect, request, jsonify, session
from flask.json.provider import JSONProvider
from flask_cors import CORS
from oauthlib.oauth2 import WebApplicationClient
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, current_user, get_jwt, get_jwt_identity, jwt_required
import requests
from database import Database
from sandbox.sandbox_ai import runner
from user import User
import orjson
import base64
import os
from io import BytesIO
import arrow

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
db = Database()
CORS(app)

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
GOOGLE_PROVIDER_CONFIG = requests.get(GOOGLE_DISCOVERY_URL).json()

app.config["JWT_SECRET_KEY"] = app.secret_key
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

resolver_table = {}

jwt = JWTManager(app)

client = WebApplicationClient(GOOGLE_CLIENT_ID)

@jwt.user_identity_loader
def user_identity_lookup(user: User):
    return user.id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    player = db.retrieve_player(identity)
    if not player:
        return None
    return User(player["id"])

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
@jwt_required()
def sendCode():
    data = request.get_json()
    code = data["code"]
    pid = data["id"]
    if pid != current_user.id:
        return "Unauthorized", 401
    code = code
    db.submit_code(pid, code)
    return "OK", 200

@app.route("/sendCodeAI", methods=["POST"])
@jwt_required()
def sendCodeAI():
    data = request.get_json()
    code = data["code"]
    level = data["level"]
    pid = data["id"]
    if pid != current_user.id:
        return "Unauthorized", 401
    code = code
    return jsonify(dict(zip(("status", "output"), runner(code, level))))

@app.route("/getPlayers", methods=["GET"])
def getPlayers():
    res = db.retrieve_all_players()
    return jsonify(res)

@app.route("/getPlayer/<string:id>", methods=["GET"])
def getPlayer(id: str):
    res = db.retrieve_player(id)
    if res is None:
        return "", 404
    return jsonify(res)

@app.route("/getGames", methods=["GET"])
def getGames():
    res = db.retrieve_all_games()
    return jsonify(res)

@app.route("/getGame/<int:id>", methods=["GET"])
def getGameDetails(id):
    res = db.retrieve_game(id)
    if res is None:
        return "", 404
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

@app.route("/testLogin")
@jwt_required(optional=True)
def testLogin():
    if current_user: # type: ignore
        result = db.retrieve_player(current_user.id) # type: ignore
        if result is None:
            response = jsonify({"status": False})
            return response
        response = {"user": result, "status": True}
        return jsonify(response)
    return jsonify({"status": False}) # type: ignore

@app.route("/login")
def login():
    _next = request.args.get("next") # redirect url at the end
    session["next"] = _next

    create = request.args.get("create")
    session["create"] = create

    # Find out what URL to hit for Google login
    authorization_endpoint = GOOGLE_PROVIDER_CONFIG["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url.replace("http://", "https://", 1) + "/callback",
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
        authorization_response=request.url.replace("http://", "https://", 1),
        redirect_url=request.base_url.replace("http://", "https://", 1),
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

    next_ = session.pop("next", "/")

    if not db.does_user_exist(id):
        print(session["create"], flush=True)
        if session.pop("create", None) != "true":
            return redirect(next_)
        with open("src/default.png", "rb") as f:
            pfp = f.read()
        db.add_user(id, "", "", "", "", pfp)

    code = uuid.uuid4().hex
    resolver_table[code] = User(id)

    # vulnerable to open redirect but welp
    return redirect(next_ + "?code=" + code)

@app.route("/login/resolver")
def resolver():
    code = request.args.get("code")
    if code in resolver_table:
        user = resolver_table[code]
        del resolver_table[code]
        access_token = create_access_token(identity=user)
        refresh_token = create_refresh_token(identity=user)
        time_till_renew = app.config["JWT_ACCESS_TOKEN_EXPIRES"] / 2
        renew = arrow.utcnow() + time_till_renew
        response = jsonify({"status": True, "access_token": access_token, "refresh_token": refresh_token, "renew": renew.isoformat()})
        return response
    return jsonify({"status": False})

@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_expiring_jwts():
    access_token = create_access_token(identity=current_user)
    time_till_renew = app.config["JWT_ACCESS_TOKEN_EXPIRES"] / 2
    renew = arrow.utcnow() + time_till_renew
    return jsonify(access_token=access_token, renew=renew.isoformat())

@app.route("/updateDetails", methods=["POST"])
@jwt_required()
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
@jwt_required()
def deleteUser():
    data = request.get_json()
    id = data["id"]
    db.delete_user(id)
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
