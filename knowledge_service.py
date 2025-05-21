import json
import os
import re
from typing import Dict, List, Any, Optional, Union

class KnowledgeService:
    """
    Servicio para manejar la base de conocimientos.
    Esta clase encapsula toda la lógica relacionada con la búsqueda y recuperación
    de información de la base de conocimientos.
    """

    def __init__(self, knowledge_file: str = 'knowledge_base.json'):
        """
        Inicializa el servicio de conocimiento.

        Args:
            knowledge_file (str): Ruta al archivo JSON con la base de conocimientos.
        """
        self.knowledge_file = knowledge_file
        self.knowledge_base = self._load_knowledge_base()

    def _load_knowledge_base(self) -> Dict[str, Any]:
        """
        Carga la base de conocimientos desde el archivo JSON.

        Returns:
            Dict[str, Any]: La base de conocimientos como un diccionario.
        """
        try:
            if os.path.exists(self.knowledge_file):
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"Archivo de base de conocimientos no encontrado: {self.knowledge_file}")
                return {}
        except Exception as e:
            print(f"Error al cargar la base de conocimientos: {e}")
            return {}

    def get_company_info(self) -> Dict[str, Any]:
        """
        Obtiene información general sobre la empresa.

        Returns:
            Dict[str, Any]: Información general de la empresa.
        """
        return {
            "title": self.knowledge_base.get("title", ""),
            "description": self.knowledge_base.get("description", ""),
            "about": self.knowledge_base.get("about", ""),
            "site_url": self.knowledge_base.get("site_url", "")
        }

    def get_contact_info(self) -> Dict[str, Any]:
        """
        Obtiene la información de contacto de la empresa.

        Returns:
            Dict[str, Any]: Información de contacto.
        """
        return self.knowledge_base.get("contact_info", {})

    def get_products(self) -> List[Dict[str, str]]:
        """
        Obtiene la lista de productos/servicios ofrecidos.

        Returns:
            List[Dict[str, str]]: Lista de productos/servicios.
        """
        return self.knowledge_base.get("products", [])

    def get_sections(self) -> Dict[str, str]:
        """
        Obtiene las secciones de información de la empresa.

        Returns:
            Dict[str, str]: Secciones de información.
        """
        return self.knowledge_base.get("sections", {})

    def get_faqs(self) -> List[Dict[str, str]]:
        """
        Obtiene las preguntas frecuentes.

        Returns:
            List[Dict[str, str]]: Lista de preguntas frecuentes.
        """
        return self.knowledge_base.get("faqs", [])

    def search(self, query: str) -> Dict[str, Any]:
        """
        Busca información relevante en la base de conocimientos basada en la consulta.

        Args:
            query (str): La consulta del usuario.

        Returns:
            Dict[str, Any]: Información relevante encontrada.
        """
        query = query.lower()
        results = {
            "company_info": {},
            "contact": {},
            "products": [],
            "sections": {},
            "faqs": []
        }

        # Buscar en información de la empresa
        company_info = self.get_company_info()
        if any(keyword in query for keyword in ["empresa", "compañía", "about", "acerca", "quiénes", "quienes"]):
            results["company_info"] = company_info

        # Palabras clave para información de contacto
        # Limitamos a las más específicas para evitar falsos positivos

        # Incluir información de contacto en más casos para asegurar que esté disponible cuando se necesite
        contact_keywords = ["contacto", "email", "correo", "teléfono", "telefono", "dirección", "direccion", "ubicación", "ubicacion"]

        # Palabras clave que sugieren que el usuario podría necesitar contactar a la empresa
        contact_suggestion_keywords = ["consultar", "contactar", "preguntar", "información", "informacion", "detalle", "detalles", "específico", "especifico", "personalizado", "personalizada", "cotización", "cotizacion", "precio", "costo"]

        # Incluir información de contacto si el usuario la solicita explícitamente o si podría necesitarla
        if any(keyword in query for keyword in contact_keywords) or any(keyword in query for keyword in contact_suggestion_keywords):
            results["contact"] = self.get_contact_info()

        # Buscar en productos/servicios
        products = self.get_products()
        if any(keyword in query for keyword in ["producto", "servicio", "ofrecen", "venden", "precio"]):
            results["products"] = products
        else:
            # Buscar productos específicos
            for product in products:
                if product["name"].lower() in query:
                    results["products"].append(product)

        # Buscar en secciones
        sections = self.get_sections()
        for section_name, section_content in sections.items():
            if section_name.lower() in query:
                results["sections"][section_name] = section_content

        # Buscar en FAQs
        faqs = self.get_faqs()

        # Palabras clave específicas para mejorar la búsqueda
        horario_keywords = ["horario", "hora", "abierto", "atienden", "atención", "disponible", "disponibilidad", "cuando"]
        soporte_keywords = ["soporte", "técnico", "domicilio", "visita", "presencial", "remoto"]
        desarrollo_keywords = ["desarrollo", "aplicación", "app", "software", "tiempo", "duración", "tarda"]
        exterior_keywords = ["exterior", "extranjero", "internacional", "fuera", "otro país"]
        # Palabras clave para chatbots - ahora dirigirán a la FAQ específica que indica que no es un servicio específico
        chatbot_keywords = ["chatbot", "chat", "bot", "asistente virtual", "asistente", "virtual", "corporativo", "automatizado", "automatización", "conversacional"]

        # Verificar si la consulta está relacionada con horarios
        is_horario_query = any(keyword in query for keyword in horario_keywords)
        is_soporte_query = any(keyword in query for keyword in soporte_keywords)
        is_desarrollo_query = any(keyword in query for keyword in desarrollo_keywords)
        is_exterior_query = any(keyword in query for keyword in exterior_keywords)
        is_chatbot_query = any(keyword in query for keyword in chatbot_keywords)

        for faq in faqs:
            question = faq["question"].lower()

            # Verificar coincidencias específicas por tema
            if is_horario_query and "horario" in question:
                results["faqs"].append(faq)
                continue

            if is_soporte_query and "soporte técnico" in question:
                results["faqs"].append(faq)
                continue

            if is_desarrollo_query and "desarrollar" in question:
                results["faqs"].append(faq)
                continue

            if is_exterior_query and "exterior" in question:
                results["faqs"].append(faq)
                continue

            if is_chatbot_query and ("chatbot" in question or "bot" in question):
                results["faqs"].append(faq)
                continue

            # Método general: verificar palabras en común
            question_words = set(re.findall(r'\w+', question))
            query_words = set(re.findall(r'\w+', query))
            if len(question_words.intersection(query_words)) >= 2:  # Al menos 2 palabras en común
                results["faqs"].append(faq)

        return results

    def format_knowledge_for_context(self, query: str) -> str:
        """
        Formatea la información relevante de la base de conocimientos para incluirla en el contexto.

        Args:
            query (str): La consulta del usuario.

        Returns:
            str: Información formateada para el contexto.
        """
        search_results = self.search(query)
        context_parts = []

        # Añadir información de la empresa si es relevante
        if search_results["company_info"]:
            company_info = search_results["company_info"]
            context_parts.append(f"Información de la empresa:\n{company_info['title']}: {company_info['description']}\n{company_info['about']}")

        # Añadir información de contacto si es relevante
        if search_results["contact"]:
            contact_info = search_results["contact"]
            contact_str = "Información de contacto:\n"

            # Obtener emails del JSON
            if "email" in contact_info and contact_info["email"]:
                contact_str += f"Email: {', '.join(contact_info['email'])}\n"

            # Obtener teléfonos del JSON
            if "phone" in contact_info and contact_info["phone"]:
                contact_str += f"Teléfono: {', '.join(contact_info['phone'])}\n"

            # Obtener direcciones del JSON
            if "address" in contact_info and contact_info["address"]:
                contact_str += f"Dirección: {', '.join(contact_info['address'])}"

            context_parts.append(contact_str)

        # Añadir productos/servicios si son relevantes
        if search_results["products"]:
            products_str = "Productos/Servicios:\n"
            for product in search_results["products"]:
                products_str += f"- {product['name']}: {product['description']} (Precio: {product['price']})\n"
            context_parts.append(products_str)

        # Añadir secciones relevantes
        if search_results["sections"]:
            sections_str = "Información adicional:\n"
            for section_name, section_content in search_results["sections"].items():
                sections_str += f"{section_name}: {section_content}\n"
            context_parts.append(sections_str)

        # Añadir FAQs relevantes
        if search_results["faqs"]:
            faqs_str = "Preguntas frecuentes:\n"
            for faq in search_results["faqs"]:
                faqs_str += f"P: {faq['question']}\nR: {faq['answer']}\n"
            context_parts.append(faqs_str)

        # Unir todas las partes del contexto
        if context_parts:
            return "\n\n".join(context_parts)
        else:
            return ""

# Crear una instancia del servicio para uso general
knowledge_service = KnowledgeService()

# Funciones de conveniencia para uso directo
def search(query: str) -> Dict[str, Any]:
    """Busca información en la base de conocimientos."""
    return knowledge_service.search(query)

def format_knowledge_for_context(query: str) -> str:
    """Formatea la información relevante para el contexto."""
    return knowledge_service.format_knowledge_for_context(query)
