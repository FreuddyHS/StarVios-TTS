from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from gtts import gTTS
import os
import uuid
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

AUDIO_DIR = "audios"
os.makedirs(AUDIO_DIR, exist_ok=True)

USUARIOS_PERMITIDOS = {
    "atajashe": "80101632",
    "navidekennedy": "leonesmio",
    "carlitaxcc": "carlamaracuchagod"
}

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "active", "message": "Servidor TTS Starvios activo"})

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
        
    data = request.json or {}
    usuario = str(data.get('usuario', '')).strip().lower()
    password = str(data.get('password', '')).strip()

    if usuario in USUARIOS_PERMITIDOS and USUARIOS_PERMITIDOS[usuario] == password:
        return jsonify({"success": True, "usuario": usuario})
    
    return jsonify({"success": False, "error": "Credenciales incorrectas"}), 401

@app.route('/scrape-overlay', methods=['POST', 'OPTIONS'])
def scrape_overlay():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    data = request.json or {}
    overlay_url = data.get('overlay', '').strip()

    if not overlay_url or not overlay_url.startswith("http"):
        return jsonify({"success": False, "error": "URL de overlay inválida"}), 400

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        res = requests.get(overlay_url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')

        # Buscar elementos de chat dentro de la respuesta HTML
        mensajes = []
        for el in soup.find_all(['div', 'p', 'span']):
            texto = el.get_text(strip=True)
            if "@" in texto and len(texto) < 200:
                mensajes.append(texto)

        return jsonify({"success": True, "raw_messages": mensajes})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/tts', methods=['POST', 'OPTIONS'])
def generar_tts():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    data = request.json or {}
    canal = str(data.get('canal', 'general')).strip().lower()
    usuario = str(data.get('usuario', 'Espectador')).strip()
    mensaje = str(data.get('mensaje', '')).strip()

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

@app.route('/audios/<filename>', methods=['GET'])
def servir_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
