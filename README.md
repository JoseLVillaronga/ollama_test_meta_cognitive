# Ollama Chat Web

Una aplicación web simple para interactuar con modelos de lenguaje de Ollama.

## Requisitos

- Python 3.8 o superior
- Ollama instalado y ejecutándose localmente
- El modelo especificado en el archivo `.env` debe estar disponible en Ollama

## Configuración

1. Clona este repositorio
2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

3. Configura las variables de entorno en el archivo `.env`:

```
MODEL=phi4-mini:latest  # El modelo de Ollama que deseas usar
WEB_PORT=8140           # El puerto en el que se ejecutará la aplicación web
```

## Ejecución

1. Asegúrate de que Ollama esté ejecutándose en tu máquina local
2. Si aún no has descargado el modelo especificado, puedes hacerlo con:

```bash
ollama pull phi4-mini:latest
```

3. Inicia la aplicación web:

```bash
python app.py
```

4. Abre tu navegador y visita `http://localhost:8140`

## Uso

- Escribe un mensaje en el campo de texto y presiona "Enviar" o la tecla Enter
- La respuesta del modelo se mostrará en el chat
- Puedes continuar la conversación enviando más mensajes

## Notas

- Esta es una aplicación de prueba y no está diseñada para uso en producción
- La aplicación asume que Ollama está ejecutándose en `http://localhost:11434`
