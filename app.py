
import os
import json
import threading
from flask import Flask, jsonify, request
from tuya_connector import (
    TuyaOpenAPI,
    TuyaOpenPulsar,
    TuyaCloudPulsarTopic,
)

app = Flask(__name__)

ACCESS_ID = os.environ.get("TUYA_ACCESS_ID")
ACCESS_SECRET = os.environ.get("TUYA_ACCESS_SECRET")
DEVICE_ID = os.environ.get("TUYA_DEVICE_ID")

API_ENDPOINT = "https://openapi.tuyaus.com"
MQ_ENDPOINT = "wss://mqe.tuyaus.com:8285/"

@app.route("/")
def inicio():
    return "JC Portoes - Servidor funcionando!"

@app.route("/teste-tuya")
def teste_tuya():
    if not all([ACCESS_ID, ACCESS_SECRET, DEVICE_ID]):
        return jsonify({"erro": "Faltam credenciais"}), 500

    try:
        api = TuyaOpenAPI(
            API_ENDPOINT, ACCESS_ID, ACCESS_SECRET
        )
        api.connect()
        resultado = api.get(
            f"/v1.0/devices/{DEVICE_ID}/status"
        )
        return jsonify(resultado)
    except Exception:
        app.logger.exception("Erro ao consultar Tuya")
        return jsonify({"erro": "Falha na consulta"}), 502

def receber_evento(msg):
    try:
        dados = msg if isinstance(msg, dict) else json.loads(msg)
        evento = dados.get("data", {})
        if not isinstance(evento, dict):
            return

        if evento.get("devId") != DEVICE_ID:
            return

        for item in evento.get("status", []):
            codigo = item.get("code")
            valor = item.get("value")

            if codigo in ("doorcontact_state", "door_state_1"):
                app.logger.info(
                    "JC PORTOES EVENTO: %s = %s",
                    codigo, valor
                )
    except Exception:
        app.logger.exception("Erro ao processar evento")

def iniciar_monitoramento():
    if not all([ACCESS_ID, ACCESS_SECRET, DEVICE_ID]):
        app.logger.warning("Credenciais incompletas")
        return

    try:
        consumidor = TuyaOpenPulsar(
            ACCESS_ID,
            ACCESS_SECRET,
            MQ_ENDPOINT,
            TuyaCloudPulsarTopic.PROD
        )
        consumidor.add_message_listener(receber_evento)
        app.extensions["tuya_pulsar"] = consumidor
        print("JC PORTOES: Iniciando conexao Pulsar", flush=True)
consumidor.start()
print("JC PORTOES: Metodo start retornou", flush=True)
        app.logger.info("Monitoramento Tuya iniciado")
    except Exception:
        app.logger.exception("Erro no monitoramento Tuya")

@app.route("/webhook", methods=["POST"])
def webhook():
    dados = request.get_json(silent=True) or {}
    app.logger.info("Webhook recebido")
    return jsonify({"status": "recebido"}), 200

if __name__ == "__main__":
    threading.Thread(
        target=iniciar_monitoramento,
        daemon=True
    ).start()

    porta = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=porta)
    
