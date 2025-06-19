from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return "Climatizzatore - API attiva"

@app.route('/clima', methods=['POST'])
def clima_control():
    data = request.json
    action = data.get("action")

    if action == "start":
        subprocess.run(["python3", "start_clima.py"])
        return "Climatizzatore acceso", 200
    elif action == "stop":
        subprocess.run(["python3", "stop_clima.py"])
        return "Climatizzatore spento", 200
    else:
        return "Azione non valida. Usa 'start' o 'stop'.", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
