
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def inicio():
    return "JC Portoes - Servidor funcionando!"

@app.route("/webhook", methods=["POST"])
def webhook():
    dados = request.get_json(silent=True) or {}
    print("Evento recebido:", dados, flush=True)
    return jsonify({"status": "recebido"}), 200

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=porta)
