import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
import logging

# CONFIGURACIÓN DE RUTA ABSOLUTA PARA LOGS
RUTA_ABSOLUTA_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ejecucion.log")

# Limpiar handlers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# LOGS
logging.basicConfig(
    filename=RUTA_ABSOLUTA_LOG,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

class AgenteTienda:

    def __init__(self, ruta_base_vectores="base_vectores"):

        # Ruta de la base de vectores
        self.ruta_base = "base_vectors" if os.path.exists("base_vectors") else "base_vectores"
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

        logging.info("Iniciando la carga de la base de datos vectorial.")
        if os.path.exists(self.ruta_base):
            self.db_vectorial = FAISS.load_local(
                self.ruta_base,
                self.embeddings,
                allow_dangerous_deserialization = True
            )
            logging.info("Base de datos vectorial cargada exitosamente.")
        else:
            logging.error(f"Error crítico: No se encontró la carpeta {self.ruta_base}")
            raise FileNotFoundError(f"No se encontró la base de vectores en {self.ruta_base}.")
        
        # MODELOS Y FALLBACKS

        modelo_principal = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.0)

        respaldo_2_0 = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.0)
        respaldo_1_5 = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.0)

        self.llm = modelo_principal.with_fallbacks([respaldo_2_0, respaldo_1_5])
        

    def responder_consulta(self, pregunta_usuario):
        try:

            logging.info(f"Consulta usuario: '{pregunta_usuario}'")
            documentos_relevantes = self.db_vectorial.similarity_search(pregunta_usuario, k=3)
            contexto = "\n\n".join([doc.page_content for doc in documentos_relevantes])

            # ESTRUCTURACIÓN DE FUENTES CON SU ORIGEN
            fuentes = []
            for doc in documentos_relevantes:
                origen = doc.metadata.get("source", "politicas_tienda.txt")
                nombre_archivo = os.path.basename(origen)
                
                fuentes.append({
                    "texto": doc.page_content,
                    "origen": nombre_archivo
                })
            
            for idx, f in enumerate(fuentes, 1):
                logging.info(f"FUENTE UTILIZADA [{idx}] en [{f['origen']}]: {f['texto'][:100]}...")
            prompt_sistema = f"""
            Eres un asistente virtual de atención al cliente altamente profesional para nuestra Tienda Online.
            Tu objetivo es responder de forma amable, clara y precisa a las consultas de los usuarios utilizando ÚNICAMENTE el contexto provisto a continuación.

            === CONTEXTO DE CONOCIMIENTO (INVENTARIO Y POLÍTICAS) ===
            {contexto}
            =========================================================

            === REGLAS CRÍTICAS DE VALIDACIÓN ===
            1. Solo responde utilizando la información que se encuentra explícitamente en el CONTEXTO.
            2. Si la información solicitada no está en el contexto (por ejemplo, si te preguntan por un producto que no está en el inventario o una política que no existe), debes responder exactamente: "Lo siento, actualmente no tengo esa información disponible en nuestro sistema. ¿Puedo ayudarte con alguna otra consulta sobre nuestro catálogo o políticas actuales?"
            3. No inventes precios, características ni inventarios bajo ninguna circunstancia.
            4. Responde siempre en español, manteniendo un tono servicial y profesional.

            Pregunta del Cliente: {pregunta_usuario}
            Respuesta:


            """

            respuesta_modelo = self.llm.invoke(prompt_sistema)
            
            # PARSER
            
            contenido = respuesta_modelo.content

            respuesta_final= str(contenido)

            if isinstance(contenido, list) and len(contenido) > 0:
                if isinstance(contenido[0], dict) and 'text' in contenido[0]:
                    respuesta_final = contenido[0]['text']
            
            logging.info(f"Respuesta agente: '{respuesta_final[:100]}'")

            # PREGUNTAS FUERA DE CONTEXTO
            mensaje_resguardo = "Lo siento, actualmente no tengo esa información disponible"
            if mensaje_resguardo in respuesta_final:
                fuentes = []

            return {
                "respuesta": respuesta_final,
                "fuentes": fuentes
            }
            #return str(contenido)    
            #return respuesta_modelo.content
        
        except Exception as e:
            logging.error(f"Error durante el procesamiento de la consulta: {e}")
            return {
                "respuesta": f"Error en la consulta: {e}",
                "fuentes": []
            }
    
    def registrar_feedback_externo(self, pregunta, respuesta, evaluacion):
        logging.info(f"FEEDBACK RECIBIDO - Evaluación: {evaluacion} | Pregunta: '{pregunta}' | Respuesta dada: '{respuesta[:100]}...'")
        for handler in logging.root.handlers:
            handler.flush()