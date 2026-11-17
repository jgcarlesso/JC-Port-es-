
import os
from flask import Flask, request, jsonify
from tuya_connector import TuyaOpenAPI

app = Flask(__name__)

TUYA_ENDPOINT = "https://openapi.tuyaus.com"
ACCESS_ID = os.environ.get("TUYA_ACCESS_ID")
ACCESS_SECRET = os.environ.get("TUYA_ACCESS_SECRET")
DEVICE_ID = os.environ.get("TUYA_DEVICE_ID")

@app.route("/")
def inicio():
    return "JC Portoes - Servidor funcionando!"

@app.route("/teste-tuya")
def teste_tuya():
    if not ACCESS_ID or not ACCESS_SECRET or not DEVICE_ID:
        return jsonify({
            "erro": "Faltam credenciais ou ID do dispositivo"
        }), 500

    try:
        api = TuyaOpenAPI(
            TUYA_ENDPOINT, ACCESS_ID, ACCESS_SECRET
        )
        api.connect()
        resultado = api.get(
            f"/v1.0/devices/{DEVICE_ID}/status"
        )
        return jsonify(resultado)
    except Exception:
        app.logger.exception("Erro ao consultar Tuya")
        return jsonify({
            "erro": "Falha ao consultar Tuya"
        }), 502

@app.route("/webhook", methods=["POST"])
def webhook():
    dados = request.get_json(silent=True) or {}
    print("Evento recebido:", dados, flush=True)
    return jsonify({"status": "recebido"}), 200

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=porta)
    
