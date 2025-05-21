import os
import requests
import uuid
import time
from dotenv import load_dotenv
from collections import defaultdict

# Importar el servicio de conocimiento
from knowledge_service import format_knowledge_for_context

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración desde variables de entorno
MODEL = os.getenv('MODEL', 'phi4-mini:latest')

# URL base de la API de Ollama (asumiendo que se ejecuta localmente)
OLLAMA_API_BASE = "http://localhost:11434/api"

# Diccionario para almacenar las conversaciones por sesión
# La estructura es: {session_id: [{"role": "user/assistant", "content": "mensaje"}, ...]}
conversations = defaultdict(list)

# Tiempo de expiración de sesiones inactivas (en segundos)
SESSION_EXPIRY = 3600  # 1 hora

# Diccionario para almacenar la última actividad de cada sesión
session_activity = {}

class OllamaService:
    """
    Servicio para interactuar con la API de Ollama.
    Esta clase encapsula toda la lógica relacionada con la comunicación con Ollama.
    """

    def __init__(self, model=None, api_base=None):
        """
        Inicializa el servicio de Ollama.

        Args:
            model (str, optional): El modelo a utilizar. Si no se proporciona, se usa el valor de la variable de entorno.
            api_base (str, optional): La URL base de la API de Ollama. Si no se proporciona, se usa el valor predeterminado.
        """
        self.model = model or MODEL
        self.api_base = api_base or OLLAMA_API_BASE

    def get_model_name(self):
        """
        Obtiene el nombre del modelo que se está utilizando.

        Returns:
            str: El nombre del modelo.
        """
        return self.model

    def create_session(self):
        """
        Crea una nueva sesión para un usuario.

        Returns:
            str: El ID de la sesión creada.
        """
        session_id = str(uuid.uuid4())
        conversations[session_id] = []
        session_activity[session_id] = time.time()
        return session_id

    def get_session_history(self, session_id):
        """
        Obtiene el historial de conversación de una sesión.

        Args:
            session_id (str): El ID de la sesión.

        Returns:
            list: Una lista de mensajes en la conversación.
        """
        # Actualizar la última actividad de la sesión
        if session_id in session_activity:
            session_activity[session_id] = time.time()

        return conversations.get(session_id, [])

    def clear_session(self, session_id):
        """
        Limpia el historial de una sesión.

        Args:
            session_id (str): El ID de la sesión a limpiar.

        Returns:
            bool: True si se limpió correctamente, False si la sesión no existe.
        """
        if session_id in conversations:
            conversations[session_id] = []
            session_activity[session_id] = time.time()
            return True
        return False

    def delete_session(self, session_id):
        """
        Elimina una sesión.

        Args:
            session_id (str): El ID de la sesión a eliminar.

        Returns:
            bool: True si se eliminó correctamente, False si la sesión no existe.
        """
        if session_id in conversations:
            del conversations[session_id]
            if session_id in session_activity:
                del session_activity[session_id]
            return True
        return False

    def cleanup_expired_sessions(self):
        """
        Limpia las sesiones que han expirado por inactividad.

        Returns:
            int: El número de sesiones eliminadas.
        """
        current_time = time.time()
        expired_sessions = [
            session_id for session_id, last_activity in session_activity.items()
            if current_time - last_activity > SESSION_EXPIRY
        ]

        for session_id in expired_sessions:
            self.delete_session(session_id)

        return len(expired_sessions)

    def generate_response(self, prompt, session_id=None, stream=False, use_knowledge_base=True):
        """
        Genera una respuesta a partir de un prompt utilizando el modelo de Ollama.

        Args:
            prompt (str): El mensaje del usuario.
            session_id (str, optional): El ID de la sesión. Si se proporciona, se guarda el historial.
            stream (bool, optional): Si se debe transmitir la respuesta. Por defecto es False.
            use_knowledge_base (bool, optional): Si se debe usar la base de conocimientos. Por defecto es True.

        Returns:
            dict: Un diccionario con la respuesta o un error.
        """
        if not prompt:
            return {"error": "Mensaje vacío"}

        # Si se proporciona un ID de sesión, actualizar la actividad y guardar el mensaje del usuario
        if session_id:
            if session_id not in conversations:
                # Si la sesión no existe, crear una nueva
                session_id = self.create_session()

            # Actualizar la última actividad
            session_activity[session_id] = time.time()

            # Guardar el mensaje del usuario en el historial
            conversations[session_id].append({"role": "user", "content": prompt})

        # Construir el contexto de la conversación si hay un historial
        context = ""
        if session_id and conversations[session_id]:
            # Formatear el historial de la conversación para el modelo
            # Limitamos a los últimos 10 mensajes para evitar tokens excesivos
            history = conversations[session_id][-10:]
            for msg in history:
                if msg["role"] == "user":
                    context += f"Usuario: {msg['content']}\n"
                else:
                    context += f"Asistente: {msg['content']}\n"

        # Buscar información relevante en la base de conocimientos
        knowledge_context = ""
        if use_knowledge_base:
            knowledge_context = format_knowledge_for_context(prompt)
            if knowledge_context:
                knowledge_context = "Información de la base de conocimientos:\n" + knowledge_context + "\n\n"

        # Construir el prompt completo
        if context or knowledge_context:
            # Si hay contexto o información de la base de conocimientos

            # Obtener información de la empresa desde el contexto
            company_name = "la empresa"
            if knowledge_context and "Información de la empresa:" in knowledge_context:
                # Extraer el nombre de la empresa del contexto
                import re
                match = re.search(r"Información de la empresa:\n([^:]+):", knowledge_context)
                if match:
                    company_name = match.group(1).strip()

            # Prompt metacognitivo para mejorar la precisión (versión interna)
            metacognitive_prompt = f"""Eres un asistente virtual para {company_name}. Utiliza el siguiente proceso de pensamiento INTERNO para generar respuestas precisas, pero NO MUESTRES este proceso al usuario:

1. Interpreta exactamente qué está pidiendo el usuario.
2. Verifica si tienes toda la información necesaria en la base de conocimientos proporcionada.
3. Identifica posibles ambigüedades o riesgos de proporcionar información incorrecta.
4. Planifica una respuesta concisa, precisa y útil.
5. Revisa mentalmente tu respuesta antes de proporcionarla.

IMPORTANTE: Este proceso es SOLO PARA TU USO INTERNO. NO muestres estos pasos ni tu razonamiento en la respuesta final. La respuesta debe ser directa, profesional y basada en la información proporcionada, sin mencionar este proceso metacognitivo.
"""

            # System prompt específico para el asistente
            system_prompt = f"Eres un asistente virtual para {company_name}. "
            system_prompt += "Responde de manera amable y profesional. "
            system_prompt += "Usa la información proporcionada para responder preguntas sobre la empresa y sus servicios.\n\n"
            system_prompt += "IMPORTANTE: Mantén SIEMPRE tu rol como asistente. NUNCA generes texto como si fueras el usuario. "
            system_prompt += "NUNCA uses formatos como 'Usuario: [texto]' o similares. "
            system_prompt += "NUNCA simules una conversación entre múltiples participantes. "
            system_prompt += f"Responde ÚNICAMENTE como el asistente de {company_name}.\n\n"
            system_prompt += "Cuando NO tengas información específica sobre un tema en la base de conocimientos: "
            system_prompt += "1. Sé honesto y directo, indicando que no tienes información específica sobre ese tema. "
            system_prompt += "2. NUNCA inventes servicios o productos que no estén explícitamente mencionados en la base de conocimientos. "
            system_prompt += "3. Si el usuario pregunta por un servicio específico que no está en la lista de productos/servicios, indica claramente que no tienes información sobre ese servicio específico. "
            system_prompt += "4. Puedes sugerir contactar a la empresa para consultar sobre servicios específicos que no están en tu base de conocimientos. "
            system_prompt += "5. NUNCA repitas la información de contacto en cada mensaje. "
            system_prompt += "6. Proporciona información de contacto completa (email, teléfono, dirección) en estos casos: (a) cuando el usuario la solicite explícitamente, o (b) cuando sugieras al usuario que contacte a la empresa para más información. "
            system_prompt += "7. Cuando sugieras contactar a la empresa, SIEMPRE incluye al menos un email o teléfono específico de la información de contacto disponible. Por ejemplo: 'Puedes contactarnos directamente al email info@tech-support.com.ar para más información'. "
            system_prompt += "8. Mantén una conversación natural y fluida, como lo haría un asistente humano. "
            system_prompt += "9. Responde de manera concisa y profesional.\n\n"

            # Combinar los prompts
            full_prompt = metacognitive_prompt + "\n\n" + system_prompt

            # Añadir información de la base de conocimientos si existe
            if knowledge_context:
                full_prompt += knowledge_context

            # Añadir el historial de conversación si existe
            if context:
                full_prompt += "Historial de la conversación:\n" + context + "\n"

            # Añadir el prompt actual
            full_prompt += "Usuario: " + prompt + "\nAsistente:"
        else:
            # Si no hay historial ni información de la base de conocimientos
            # Usar un nombre genérico para la empresa
            company_name = "Tech Support Argentina"

            metacognitive_prompt = f"""Eres un asistente virtual para {company_name}. Utiliza el siguiente proceso de pensamiento INTERNO para generar respuestas precisas, pero NO MUESTRES este proceso al usuario:

1. Interpreta exactamente qué está pidiendo el usuario.
2. Verifica si tienes toda la información necesaria para responder adecuadamente.
3. Identifica posibles ambigüedades o riesgos de proporcionar información incorrecta.
4. Planifica una respuesta concisa, precisa y útil.
5. Revisa mentalmente tu respuesta antes de proporcionarla.

IMPORTANTE: Este proceso es SOLO PARA TU USO INTERNO. NO muestres estos pasos ni tu razonamiento en la respuesta final. La respuesta debe ser directa, profesional y amable, sin mencionar este proceso metacognitivo.
"""

            system_prompt = f"Eres un asistente virtual para {company_name}. Responde de manera amable y profesional.\n\n"
            system_prompt += "IMPORTANTE: Mantén SIEMPRE tu rol como asistente. NUNCA generes texto como si fueras el usuario. "
            system_prompt += "NUNCA uses formatos como 'Usuario: [texto]' o similares. "
            system_prompt += "NUNCA simules una conversación entre múltiples participantes. "
            system_prompt += f"Responde ÚNICAMENTE como el asistente de {company_name}.\n\n"
            system_prompt += "Cuando NO tengas información específica sobre un tema en la base de conocimientos: "
            system_prompt += "1. Sé honesto y directo, indicando que no tienes información específica sobre ese tema. "
            system_prompt += "2. NUNCA inventes servicios o productos que no estén explícitamente mencionados en la base de conocimientos. "
            system_prompt += "3. Si el usuario pregunta por un servicio específico que no está en la lista de productos/servicios, indica claramente que no tienes información sobre ese servicio específico. "
            system_prompt += "4. Puedes sugerir contactar a la empresa para consultar sobre servicios específicos que no están en tu base de conocimientos. "
            system_prompt += "5. NUNCA repitas la información de contacto en cada mensaje. "
            system_prompt += "6. Proporciona información de contacto completa (email, teléfono, dirección) en estos casos: (a) cuando el usuario la solicite explícitamente, o (b) cuando sugieras al usuario que contacte a la empresa para más información. "
            system_prompt += "7. Cuando sugieras contactar a la empresa, SIEMPRE incluye al menos un email o teléfono específico de la información de contacto disponible. Por ejemplo: 'Puedes contactarnos directamente al email info@tech-support.com.ar para más información'. "
            system_prompt += "8. Mantén una conversación natural y fluida, como lo haría un asistente humano. "
            system_prompt += "9. Responde de manera concisa y profesional.\n\n"
            full_prompt = metacognitive_prompt + "\n\n" + system_prompt + "Usuario: " + prompt + "\nAsistente:"

        # Preparar la solicitud para Ollama
        ollama_payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": stream
        }

        try:
            # Enviar solicitud a la API de Ollama
            response = requests.post(f"{self.api_base}/generate", json=ollama_payload)
            response.raise_for_status()

            # Procesar la respuesta
            result = response.json()
            ai_response = result.get('response', 'No se pudo obtener una respuesta')

            # Si se proporciona un ID de sesión, guardar la respuesta del asistente
            if session_id:
                conversations[session_id].append({"role": "assistant", "content": ai_response})

            return {"response": ai_response, "session_id": session_id}

        except requests.exceptions.RequestException as e:
            print(f"Error al comunicarse con Ollama: {e}")
            return {"error": f"Error al comunicarse con Ollama: {str(e)}"}

    def list_available_models(self):
        """
        Obtiene una lista de los modelos disponibles en Ollama.

        Returns:
            list: Una lista de diccionarios con información sobre los modelos disponibles.
        """
        try:
            response = requests.get(f"{self.api_base}/tags")
            response.raise_for_status()

            result = response.json()
            models = result.get('models', [])

            return models

        except requests.exceptions.RequestException as e:
            print(f"Error al obtener la lista de modelos: {e}")
            return []

# Crear una instancia del servicio para uso general
ollama_service = OllamaService()

# Funciones de conveniencia para uso directo
def get_model_name():
    """Obtiene el nombre del modelo actual."""
    return ollama_service.get_model_name()

def generate_response(prompt, session_id=None, stream=False, use_knowledge_base=True):
    """Genera una respuesta a partir de un prompt."""
    return ollama_service.generate_response(prompt, session_id, stream, use_knowledge_base)

def list_available_models():
    """Obtiene una lista de los modelos disponibles."""
    return ollama_service.list_available_models()

def create_session():
    """Crea una nueva sesión."""
    return ollama_service.create_session()

def get_session_history(session_id):
    """Obtiene el historial de una sesión."""
    return ollama_service.get_session_history(session_id)

def clear_session(session_id):
    """Limpia el historial de una sesión."""
    return ollama_service.clear_session(session_id)

def delete_session(session_id):
    """Elimina una sesión."""
    return ollama_service.delete_session(session_id)

def cleanup_expired_sessions():
    """Limpia las sesiones expiradas."""
    return ollama_service.cleanup_expired_sessions()
