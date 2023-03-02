from sandbox import sandbox
from flask import Flask, request, jsonify

from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "super_secret_key"
CORS(app)

@app.route("/<name>")
def home(name):
    return f"<h1>Hello World, {name}</h1>"

@app.route("/sendCodeHTML/<code>")
def sendCodeHTML(code):
    imports = "from troop import enemiesWithinRange, getFriendlyTroops, distanceToEntity\n\n"
    return sandbox.sandbox(imports + code)[1]

@app.route("/sendCode", methods=["POST"])
def sendCode():
    code = request.get_json()['code']
    imports = "from troop import enemiesWithinRange, getFriendlyTroops, distanceToEntity\n\n"
    return jsonify(dict(zip(("status", "output"), sandbox.sandbox(imports + code))))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
