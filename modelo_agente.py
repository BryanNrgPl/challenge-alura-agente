import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS

class AgenteTienda:

    def __init__(self, ruta_base_vectores="base_vectores"):

        # Ruta de la base de vectores
        self.ruta_base = "base_vectors" if os.path.exists("base_vectors") else "base_vectores"
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

        if os.path.exists(self.ruta_base):
            self.db_vectorial = FAISS.load_local(
                self.ruta_base,
                self.embeddings,
                allow_dangerous_deserialization = True
            )
        else:
            raise FileNotFoundError(f"No se encontró la base de vectores en {self.ruta_base}.")
        
        # MODELOS Y FALLBACKS

        modelo_principal = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.0)

        respaldo_2_0 = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.0)
        respaldo_1_5 = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.0)

        self.llm = modelo_principal.with_fallbacks([respaldo_2_0, respaldo_1_5])
        

    def responder_consulta(self, pregunta_usuario):
        try:
            documentos_relevantes = self.db_vectorial.similarity_search(pregunta_usuario, k=3)
            contexto = "\n\n".join([doc.page_content for doc in documentos_relevantes])

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

            if isinstance(contenido, list) and len(contenido) > 0:
                if isinstance(contenido[0], dict) and 'text' in contenido[0]:
                    return contenido[0]['text']

            return str(contenido)    
            
            
            #return respuesta_modelo.content
        
        except Exception as e:
            return f"Error en la consulta: {e}"