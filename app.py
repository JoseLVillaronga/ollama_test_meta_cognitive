import os
import threading
import time
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv

# Importar nuestro servicio de Ollama
from ollama_service import (
    get_model_name, generate_response, create_session,
    get_session_history, clear_session, delete_session, cleanup_expired_sessions
)

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Clave secreta para las sesiones de Flask

# Configuración desde variables de entorno
WEB_PORT = int(os.getenv('WEB_PORT', 8140))

# Configurar un temporizador para limpiar sesiones expiradas periódicamente
def cleanup_sessions_periodically():
    while True:
        time.sleep(3600)  # Ejecutar cada hora
        num_deleted = cleanup_expired_sessions()
        if num_deleted > 0:
            print(f"Se eliminaron {num_deleted} sesiones expiradas")

@app.route('/')
def index():
    """Ruta principal que renderiza la interfaz de chat"""
    # Verificar si el usuario ya tiene una sesión
    if 'session_id' not in session:
        # Crear una nueva sesión
        session['session_id'] = create_session()
        print(f"Nueva sesión creada: {session['session_id']}")

    return render_template('index.html', model=get_model_name())

@app.route('/api/chat', methods=['POST'])
def chat():
    """API para enviar mensajes al modelo y recibir respuestas"""
    data = request.json
    user_message = data.get('message', '')
    use_knowledge_base = data.get('use_knowledge_base', True)

    if not user_message:
        return jsonify({"error": "Mensaje vacío"}), 400

    # Obtener el ID de sesión del usuario
    session_id = session.get('session_id')
    if not session_id:
        # Si no hay sesión, crear una nueva
        session_id = create_session()
        session['session_id'] = session_id

    # Usar nuestro servicio para generar la respuesta con la sesión
    result = generate_response(user_message, session_id, use_knowledge_base=use_knowledge_base)

    if "error" in result:
        return jsonify(result), 500

    return jsonify(result)

@app.route('/api/history', methods=['GET'])
def history():
    """API para obtener el historial de conversación"""
    session_id = session.get('session_id')
    if not session_id:
        return jsonify({"error": "No hay sesión activa"}), 400

    # Obtener el historial de la sesión
    conversation_history = get_session_history(session_id)

    return jsonify({"history": conversation_history})

@app.route('/api/clear', methods=['POST'])
def clear():
    """API para limpiar el historial de conversación"""
    session_id = session.get('session_id')
    if not session_id:
        return jsonify({"error": "No hay sesión activa"}), 400

    # Limpiar el historial de la sesión
    success = clear_session(session_id)

    if success:
        return jsonify({"message": "Historial limpiado correctamente"})
    else:
        return jsonify({"error": "No se pudo limpiar el historial"}), 500

if __name__ == '__main__':
    # Iniciar el hilo de limpieza de sesiones
    cleanup_thread = threading.Thread(target=cleanup_sessions_periodically, daemon=True)
    cleanup_thread.start()

    print(f"Iniciando servidor en http://localhost:{WEB_PORT}")
    print(f"Usando modelo: {get_model_name()}")
    print(f"Limpieza de sesiones configurada para ejecutarse cada hora")

    app.run(host='0.0.0.0', port=WEB_PORT, debug=True)
