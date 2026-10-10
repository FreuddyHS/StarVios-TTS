import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from gtts import gTTS

app = Flask(__name__)
CORS(app)

# Credenciales permitidas (Usuario: Contraseña)
# Puedes cambiar las contraseñas aquí o añadir más usuarios
USUARIOS_PERMITIDOS = {
    "navidekennedy": "leonesmiesposo2026",
    "atajashe": "atajasheforever123"
}

AUDIO_DIR = os.path.join(os.getcwd(), "audios")
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

@app.route("/")
def index():
    return "Servidor TTS para Starvios (Español México) 🚀"

@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    user = data.get("usuario")
    password = data.get("password")

    if user in USUARIOS_PERMITIDOS and USUARIOS_PERMITIDOS[user] == password:
        return jsonify({"success": True, "message": "Acceso concedido"})
    else:
        return jsonify({"success": False, "message": "Usuario o contraseña incorrectos"}), 401

@app.route("/tts", methods=["POST"])
def generar_tts():
    data = request.json or {}
    canal = data.get("canal", "general")
    usuario = data.get("usuario", "Espectador")
    mensaje = data.get("mensaje", "")

    if not mensaje:
        return jsonify({"error": "Mensaje vacío"}), 400

    texto_a_decir = f"{usuario} dice: {mensaje}"

    try:
        # Idioma español con acento de México (tld='com.mx')
        tts = gTTS(text=texto_a_decir, lang='es', tld='com.mx', slow=False)
        filename = f"audio_{os.urandom(4).hex()}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)
        tts.save(filepath)

        return jsonify({"success": True, "audio_url": f"/audios/{filename}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/audios/<filename>")
def get_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
