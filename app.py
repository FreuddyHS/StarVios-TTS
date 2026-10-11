from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from gtts import gTTS
import os
import uuid

app = Flask(__name__)
CORS(app)

AUDIO_DIR = "audios"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Usuarios permitidos y sus contraseñas
USUARIOS_PERMITIDOS = {
    "atajashe": "atajasheforever123",
    "navidekennedy": "esposadeleon",
    "carlitaxcc": "elamordealiyatajashexd"
}

@app.route('/')
def home():
    return "Servidor TTS Multiusuario para Starvios activo (Español México)"

@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    usuario = data.get('usuario', '').strip().lower()
    password = data.get('password', '').strip()

    if usuario in USUARIOS_PERMITIDOS and USUARIOS_PERMITIDOS[usuario] == password:
        return jsonify({"success": True, "usuario": usuario})
    
    return jsonify({"success": False, "error": "Credenciales inválidas"}), 401

@app.route('/tts', methods=['POST'])
def generar_tts():
    data = request.json or {}
    canal = data.get('canal', 'general').strip().lower()
    usuario = data.get('usuario', 'Espectador').strip()
    mensaje = data.get('mensaje', '').strip()

    if not mensaje:
        return jsonify({"success": False, "error": "Mensaje vacío"}), 400

    texto_voz = f"{usuario} dice: {mensaje}"

    try:
        tts = gTTS(text=texto_voz, lang='es', tld='com.mx', slow=False)
        filename = f"audio_{uuid.uuid4().hex[:8]}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)
        tts.save(filepath)

        return jsonify({
            "success": True,
            "audio_url": f"/audios/{filename}",
            "canal": canal
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/audios/<filename>')
def servir_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
