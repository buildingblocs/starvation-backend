from datetime import timedelta
from quart import Quart, redirect, request, jsonify
from quart.json.provider import JSONProvider
from quart_cors import cors
from oauthlib.oauth2 import WebApplicationClient
from quart_jwt_extended import JWTManager, create_access_token, jwt_refresh_token_required, create_refresh_token, get_jwt_identity, jwt_required, jwt_optional
import requests
from database import Database
from sandbox.sandbox_ai import runner
import orjson
import base64
import os
from io import BytesIO
import arrow

app = Quart(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
db = Database()
cors(app)

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
GOOGLE_PROVIDER_CONFIG = requests.get(GOOGLE_DISCOVERY_URL).json()

app.config["JWT_SECRET_KEY"] = app.secret_key
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

jwt = JWTManager(app)

client = WebApplicationClient(GOOGLE_CLIENT_ID)

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

@app.before_serving
async def init_db():
    await db.init_connection()

@app.route("/")
async def home():
    return f"<h1>Starvation Backend :)</h1>"

@app.route("/sendCode", methods=["POST"])
@jwt_required
async def sendCode():
    data = await request.get_json()
    code = data["code"]
    pid = data["id"]
    if pid != get_jwt_identity():
        return "Unauthorized", 401
    code = code
    await db.submit_code(pid, code)
    return "OK", 200

@app.route("/sendCodeAI", methods=["POST"])
@jwt_required
async def sendCodeAI():
    data = await request.get_json()
    code = data["code"]
    level = data["level"]
    pid = data["id"]
    if pid != get_jwt_identity():
        return "Unauthorized", 401
    code = code
    return jsonify(dict(zip(("status", "output"), await runner(code, level))))

@app.route("/getPlayers", methods=["GET"])
async def getPlayers():
    res = await db.retrieve_all_players()
    return jsonify(res)

@app.route("/getPlayer/<string:id>", methods=["GET"])
async def getPlayer(id: str):
    res = await db.retrieve_player(id)
    if res is None:
        return "", 404
    return jsonify(res)

@app.route("/getGames", methods=["GET"])
async def getGames():
    res = await db.retrieve_all_games()
    return jsonify(res)

@app.route("/getGame/<int:id>", methods=["GET"])
async def getGameDetails(id):
    res = await db.retrieve_game(id)
    if res is None:
        return "", 404
    return jsonify(res)

@app.route("/updateChallenge", methods=["POST"])
@jwt_required
async def updateChallenge():
    data = await request.get_json()
    id = data["id"]
    if id != get_jwt_identity():
        return "Unauthorized", 401
    level = data["level"]
    code = data["code"]
    winner = data['winner']
    await db.submit_challenge(id, level, code, winner)
    return "OK", 200

@app.route("/getChallenges/<string:id>", methods=["GET"])
async def challengesById(id):
    return jsonify(await db.retrieve_challenges(id))
    
@app.route("/getChallengeCode", methods=["GET"]) # type: ignore
async def getChallenge():
    level = int(request.args.get("level", "0"))
    id = request.args.get("id", "")
    return jsonify(dict(code=await db.get_challenge_code(id, level)))

@app.route("/testLogin")
@jwt_optional
async def testLogin():
    identity = get_jwt_identity()
    if identity:
        result = await db.retrieve_player(identity)
        if result is None:
            response = jsonify({"status": False})
            return response
        response = {"user": result, "status": True}
        return jsonify(response)
    return jsonify({"status": False})

@app.route("/login")
async def login():
    _next = request.args.get("next", "") # redirect url at the end
    create = request.args.get("create", "false")

    # Find out what URL to hit for Google login
    authorization_endpoint = GOOGLE_PROVIDER_CONFIG["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url.replace("http://", "https://", 1) + "/callback",
        scope=["openid", "email"],
    )
    response = redirect(request_uri)
    response.set_cookie("next", _next)
    response.set_cookie("create", create)
    return response

@app.route("/login/callback")
async def callback():
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

    next_ = request.cookies.get("next", "/")
    response = redirect(next_)
    response.set_cookie("next", "", expires=0)
    response.set_cookie("create", "", expires=0)

    if not await db.does_user_exist(id):
        print(request.cookies.get("create"), flush=True)
        if request.cookies.get("create") != "true":
            return response
        with open("default.png", "rb") as f:
            pfp = f.read()
        await db.add_user(id, "", "", "", "", pfp)

    code = await db.add_resolver_id(id)
    if not code:
        return response
    
    response = redirect(next_ + "?code=" + code.hex)
    response.set_cookie("next", "", expires=0)
    response.set_cookie("create", "", expires=0)

    # vulnerable to open redirect but welp
    return response

@app.route("/login/resolver")
async def resolver():
    code = request.args.get("code")
    if code is None:
        return jsonify(status=False)
    id = await db.resolve_code(code)
    if id:
        user = id
        access_token = create_access_token(identity=user)
        refresh_token = create_refresh_token(identity=user)
        time_till_renew = app.config["JWT_ACCESS_TOKEN_EXPIRES"] / 2
        renew = arrow.utcnow() + time_till_renew
        response = jsonify({"status": True, "access_token": access_token, "refresh_token": refresh_token, "renew": renew.isoformat()})
        return response
    return jsonify({"status": False})

@app.route("/refresh", methods=["POST"])
@jwt_refresh_token_required
async def refresh_expiring_jwts():
    access_token = create_access_token(identity=get_jwt_identity())
    time_till_renew = app.config["JWT_ACCESS_TOKEN_EXPIRES"] / 2
    renew = arrow.utcnow() + time_till_renew
    return jsonify(access_token=access_token, renew=renew.isoformat())

@app.route("/updateDetails", methods=["POST"])
@jwt_required
async def updateDetails():
    try:
        data = await request.get_json()
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
            with open("default.png", "rb") as f:
                pfp = f.read()
        await db.updateUser(id, fullname, username, school, about, pfp)
        return "OK", 200
    except Exception as e:
        return str(e), 200

@app.route("/existsUsername", methods=["GET"])
async def existsUsername():
    username = request.args.get("username")
    if username is None: return jsonify({"result": False})
    return jsonify({"result": await db.does_username_exist(username)})

@app.route("/deleteUser", methods=["POST"])
@jwt_required
async def deleteUser():
    data = await request.get_json()
    id = data["id"]
    await db.delete_user(id)
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
#         with open("default.png", "rb") as f:
#             photo = f.read()
#     await db.add_user(id, fullname, username, school, about, photo)
#     return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
