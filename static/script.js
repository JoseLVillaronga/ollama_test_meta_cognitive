document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // Variables para almacenar el estado de la aplicación
    let sessionId = null;
    let useKnowledgeBase = true; // Por defecto, usar la base de conocimientos

    // Función para agregar un mensaje al chat
    function addMessage(content, role) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = content;

        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);

        // Desplazar hacia abajo para mostrar el mensaje más reciente
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Función para cargar el historial de conversación
    async function loadConversationHistory() {
        try {
            const response = await fetch('/api/history');

            if (response.ok) {
                const data = await response.json();

                // Limpiar el chat actual
                chatMessages.innerHTML = '';

                // Si hay historial, mostrarlo
                if (data.history && data.history.length > 0) {
                    data.history.forEach(message => {
                        const role = message.role === 'user' ? 'user' : 'assistant';
                        addMessage(message.content, role);
                    });
                } else {
                    // Si no hay historial, mostrar mensaje de bienvenida
                    addMessage('¡Hola! Soy un asistente basado en el modelo phi4-mini. ¿En qué puedo ayudarte hoy?', 'system');
                }
            } else {
                console.error('Error al cargar el historial:', response.statusText);
                // Mostrar mensaje de bienvenida por defecto
                addMessage('¡Hola! Soy un asistente basado en el modelo phi4-mini. ¿En qué puedo ayudarte hoy?', 'system');
            }
        } catch (error) {
            console.error('Error al cargar el historial:', error);
            // Mostrar mensaje de bienvenida por defecto
            addMessage('¡Hola! Soy un asistente basado en el modelo phi4-mini. ¿En qué puedo ayudarte hoy?', 'system');
        }
    }

    // Función para mostrar el indicador de "escribiendo..."
    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'message assistant';
        indicator.id = 'typing-indicator';

        const indicatorContent = document.createElement('div');
        indicatorContent.className = 'typing-indicator';

        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            indicatorContent.appendChild(dot);
        }

        indicator.appendChild(indicatorContent);
        chatMessages.appendChild(indicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Función para ocultar el indicador de "escribiendo..."
    function hideTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    // Función para enviar el mensaje al servidor
    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        // Agregar el mensaje del usuario al chat
        addMessage(message, 'user');

        // Limpiar el campo de entrada
        userInput.value = '';

        // Mostrar indicador de escritura
        showTypingIndicator();

        try {
            // Enviar solicitud al servidor
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message,
                    use_knowledge_base: useKnowledgeBase
                })
            });

            const data = await response.json();

            // Ocultar indicador de escritura
            hideTypingIndicator();

            if (response.ok) {
                // Guardar el ID de sesión si está presente
                if (data.session_id) {
                    sessionId = data.session_id;
                }

                // Agregar la respuesta del asistente al chat
                addMessage(data.response, 'assistant');
            } else {
                // Mostrar mensaje de error
                addMessage(`Error: ${data.error || 'Ocurrió un error al procesar tu solicitud.'}`, 'system');
            }
        } catch (error) {
            // Ocultar indicador de escritura
            hideTypingIndicator();

            // Mostrar mensaje de error
            addMessage('Error: No se pudo conectar con el servidor.', 'system');
            console.error('Error:', error);
        }
    }

    // Función para limpiar la conversación
    async function clearConversation() {
        try {
            const response = await fetch('/api/clear', {
                method: 'POST'
            });

            if (response.ok) {
                // Limpiar el chat en la interfaz
                chatMessages.innerHTML = '';
                // Mostrar mensaje de sistema
                addMessage('La conversación ha sido limpiada.', 'system');
            } else {
                const data = await response.json();
                addMessage(`Error: ${data.error || 'No se pudo limpiar la conversación.'}`, 'system');
            }
        } catch (error) {
            console.error('Error al limpiar la conversación:', error);
            addMessage('Error: No se pudo conectar con el servidor para limpiar la conversación.', 'system');
        }
    }

    // Crear botón de limpiar conversación
    function createClearButton() {
        const headerElement = document.querySelector('header');

        if (headerElement) {
            const clearButton = document.createElement('button');
            clearButton.id = 'clear-button';
            clearButton.textContent = 'Limpiar Conversación';
            clearButton.className = 'clear-button';

            // Añadir estilos al botón
            clearButton.style.marginTop = '10px';
            clearButton.style.padding = '8px 16px';
            clearButton.style.backgroundColor = '#e74c3c';
            clearButton.style.color = 'white';
            clearButton.style.border = 'none';
            clearButton.style.borderRadius = '4px';
            clearButton.style.cursor = 'pointer';

            clearButton.addEventListener('click', clearConversation);

            headerElement.appendChild(clearButton);
        }
    }

    // Event listeners
    sendButton.addEventListener('click', sendMessage);

    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Event listener para el interruptor de la base de conocimientos
    const knowledgeBaseToggle = document.getElementById('knowledge-base-toggle');
    if (knowledgeBaseToggle) {
        knowledgeBaseToggle.addEventListener('change', function() {
            useKnowledgeBase = this.checked;
            console.log(`Base de conocimientos ${useKnowledgeBase ? 'activada' : 'desactivada'}`);

            // Mostrar mensaje en el chat
            const status = useKnowledgeBase ? 'activada' : 'desactivada';
            addMessage(`Base de conocimientos ${status}. ${useKnowledgeBase ? 'Ahora responderé usando información específica de Tech Support Argentina.' : 'Ahora responderé sin usar información específica de la empresa.'}`, 'system');
        });
    }

    // Inicialización
    createClearButton();
    loadConversationHistory();

    // Enfocar el campo de entrada al cargar la página
    userInput.focus();
});
