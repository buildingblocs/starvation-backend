from sandbox import sandbox
from flask import Flask, request, jsonify

from flask_cors import CORS

print(sandbox.sandbox("print('hello world')"))

app = Flask(__name__)
app.secret_key = "super_secret_key"
CORS(app)

@app.route("/sendCode", methods=["POST"])
def sendCode():
    code = request.get_json()['code']
    imports = "from troop import enemiesWithinRange, getFriendlyTroops, distanceToEntity\n"
    return jsonify({"output": sandbox.sandbox(imports + code)})

if __name__ == "__main__":
    app.run(port=8080)
