# Chatbot con Ollama y RAG

Este proyecto implementa un chatbot basado en modelos de lenguaje locales de Ollama, mejorado con técnicas de Retrieval Augmented Generation (RAG) para proporcionar respuestas precisas basadas en una base de conocimientos personalizada.

## Características principales

- **Modelos locales**: Utiliza modelos de Ollama que se ejecutan localmente, sin dependencia de APIs externas.
- **Base de conocimientos personalizada**: Información estructurada en formato JSON que el chatbot puede consultar.
- **Prompting metacognitivo**: Técnica avanzada para mejorar la calidad de las respuestas.
- **Interfaz web simple**: Interfaz de usuario para interactuar con el chatbot.
- **Gestión de sesiones**: Mantiene el contexto de las conversaciones.

## Arquitectura del sistema

El sistema está compuesto por los siguientes componentes principales:

### 1. Servicio de Ollama (`ollama_service.py`)

Este componente se encarga de la comunicación con la API local de Ollama. Sus responsabilidades incluyen:

- Generar y enviar prompts estructurados al modelo
- Gestionar sesiones y mantener el historial de conversaciones
- Aplicar técnicas de prompting metacognitivo
- Integrar la información de la base de conocimientos en los prompts

### 2. Servicio de Conocimiento (`knowledge_service.py`)

Este componente gestiona la base de conocimientos y proporciona información relevante para las consultas. Sus responsabilidades incluyen:

- Cargar y procesar la base de conocimientos desde el archivo JSON
- Buscar información relevante basada en palabras clave
- Formatear la información para incluirla en el contexto del modelo
- Determinar qué información es relevante para cada consulta

### 3. Base de Conocimientos (`knowledge_base.json`)

Archivo JSON estructurado que contiene toda la información que el chatbot puede proporcionar, incluyendo:

- Información de la empresa
- Información de contacto
- Productos y servicios
- Secciones informativas
- Preguntas frecuentes (FAQs)

### 4. Aplicación Web (`app.py`)

Implementa una interfaz web simple utilizando Flask para interactuar con el chatbot. Sus responsabilidades incluyen:

- Proporcionar endpoints para la comunicación con el frontend
- Gestionar las sesiones de usuario
- Coordinar la comunicación entre el frontend y los servicios de backend

## Flujo de procesamiento de consultas

El sistema procesa las consultas de los usuarios siguiendo estos pasos:

1. **Recepción de la consulta**: La aplicación web recibe la consulta del usuario.
2. **Búsqueda de información relevante**: El servicio de conocimiento busca información relacionada con la consulta en la base de conocimientos.
3. **Construcción del prompt**: El servicio de Ollama construye un prompt que incluye:
   - Instrucciones metacognitivas
   - Instrucciones específicas del sistema
   - Información relevante de la base de conocimientos
   - Historial de la conversación
   - Consulta actual del usuario
4. **Generación de respuesta**: El modelo de Ollama procesa el prompt y genera una respuesta.
5. **Envío de respuesta**: La respuesta se envía de vuelta al usuario a través de la interfaz web.

## Técnicas de prompting

### Prompting Metacognitivo

El sistema utiliza un enfoque de prompting metacognitivo que guía al modelo a través de un proceso de pensamiento estructurado:

```
Eres un asistente virtual para [nombre de la empresa]. Utiliza el siguiente proceso de pensamiento INTERNO para generar respuestas precisas, pero NO MUESTRES este proceso al usuario:

1. Interpreta exactamente qué está pidiendo el usuario.
2. Verifica si tienes toda la información necesaria para responder adecuadamente.
3. Identifica posibles ambigüedades o riesgos de proporcionar información incorrecta.
4. Planifica una respuesta concisa, precisa y útil.
5. Revisa mentalmente tu respuesta antes de proporcionarla.

IMPORTANTE: Este proceso es SOLO PARA TU USO INTERNO. NO muestres estos pasos ni tu razonamiento en la respuesta final. La respuesta debe ser directa, profesional y amable, sin mencionar este proceso metacognitivo.
```

Este enfoque mejora significativamente la calidad de las respuestas al proporcionar una estructura de pensamiento que el modelo puede seguir, incluso cuando sus capacidades son limitadas.

### Instrucciones específicas del sistema

Además del prompting metacognitivo, el sistema proporciona instrucciones específicas sobre cómo debe comportarse el modelo:

- Mantener el rol de asistente
- Ser honesto cuando no tiene información
- No inventar servicios o productos
- Proporcionar información de contacto cuando sea apropiado
- Mantener una conversación natural y fluida

## Lecciones aprendidas y mejores prácticas

### 1. Importancia de las instrucciones precisas

Más que el tamaño del modelo, lo que realmente marca la diferencia es la claridad y precisión de las instrucciones. Un prompt bien diseñado puede compensar las limitaciones de modelos más pequeños.

### 2. Consistencia en todo el flujo

Es crucial mantener la consistencia entre:
- Cómo se almacena la información
- Cómo se recupera
- Cómo se presenta al modelo
- Cómo se instruye al modelo para usarla

### 3. Enfoque en casos de uso específicos

En lugar de intentar que el modelo sea bueno en todo, es más efectivo enfocarse en mejorar aspectos específicos, como la presentación de información de contacto.

### 4. Aprovechamiento de la base de conocimientos

Una base de conocimientos bien estructurada reduce la necesidad de que el modelo "invente" respuestas, lo que es especialmente importante con modelos más pequeños.

### 5. Iteración y prueba

El desarrollo de un chatbot efectivo requiere múltiples iteraciones y pruebas para identificar y corregir problemas específicos.

## Ventajas de usar modelos locales pequeños

- **Eficiencia de recursos**: Requieren menos recursos computacionales.
- **Privacidad**: Toda la información se procesa localmente.
- **Control**: Control total sobre el comportamiento del modelo.
- **Personalización**: Fácil adaptación a dominios específicos.
- **Costo**: Sin costos de API por consulta.

## Requisitos y configuración

- Python 3.8 o superior
- Ollama instalado y ejecutándose localmente
- El modelo especificado en el archivo `.env` debe estar disponible en Ollama

### Instalación

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

### Ejecución

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

## Próximos pasos

- Mejorar las capacidades de RAG con técnicas más avanzadas
- Implementar embeddings para búsqueda semántica
- Añadir soporte para múltiples bases de conocimientos
- Mejorar la interfaz de usuario
- Implementar tests automatizados
