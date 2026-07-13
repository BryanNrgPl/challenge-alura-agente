import os
from dotenv import load_dotenv
import pandas as pd
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY no está configurada en el archivo .env")

def extraer_inventario(ruta_csv):
    try:
        if not os.path.exists(ruta_csv):
            return []
            
        df = pd.read_csv(ruta_csv)
        documentos_inventario = []

        for _, fila in df.iterrows():
            texto_producto = (
                f"Producto: {fila['producto']} | "
                f"Categoría: {fila['categoria']} | "
                f"Precio: S/. {fila['precio_soles']} | "
                f"Stock disponible: {fila['stock']} unidades."
            )
            doc = Document(page_content=texto_producto, metadata={"source": ruta_csv})
            documentos_inventario.append(doc)

        return documentos_inventario
    
    except Exception as e:
        print(f"Error al procesar el inventario en CSV: {e}")
        return []

def extraer_y_fragmentar_politicas(ruta_txt):
    if not os.path.exists(ruta_txt):
        return []
        
    with open(ruta_txt, "r", encoding="utf-8") as f:
        contenido = f.read()
        
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    fragmentos_texto = text_splitter.split_text(contenido)
    
    documentos = [
        Document(page_content=texto, metadata={"source": ruta_txt}) 
        for texto in fragmentos_texto
    ]
    return documentos

def crear_base_conocimiento(documentos_inventario, documentos_politicas, ruta_guardado="base_vectors"):
    try:
        todos_los_documentos = documentos_inventario + documentos_politicas

        if not todos_los_documentos:
            print("Sin documentos disponibles para generar la base de conocimiento")
            return None
        
        print(f"Generando embeddings para {len(todos_los_documentos)} fragmentos totales con metadatos.")

        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

        db_vectorial = FAISS.from_documents(todos_los_documentos, embeddings)

        db_vectorial.save_local(ruta_guardado)
        print(f"Base de conocimiento vectorial guardada localmente en: {ruta_guardado}")

        return db_vectorial
    
    except Exception as e:
        print(f"Error al crear base de conocimiento: {e}")
        return None
    

#  PRUEBAS
# if __name__ == "__main__":

#     # Rutas de archivos
#     ruta_csv = "datos/inventario_tienda.csv" 
#     ruta_txt = "datos/politicas_tienda.txt"

#     # 1. PRUEBA DE INVENTARIO
#     if os.path.exists(ruta_csv):
#         print("--- Extrayendo datos del Inventario ---")
#         productos_limpios = extraer_inventario(ruta_csv)

#         for prod in productos_limpios[:1]:
#             print(prod)

#     # 2. PRUEBA DE POLITICAS
#     if os.path.exists(ruta_txt):
#         print("\n--- Extrayendo y fragmentando Políticas ---")
#         fragmentos_politicas = extraer_y_fragmentar_politicas(ruta_txt)
        
#         for i, chunk in enumerate(fragmentos_politicas[:1]):
#             print(f"Fragmento {i+1}: {chunk}\n")

#     # 3. PRUEBA DE EMBEDDINGS / BASE VECTORIAL
#     print("\n--- Creando Base de Conocimiento Vectorial ---")
#     db = crear_base_conocimiento(productos_limpios, fragmentos_politicas)

#     if db:
#         print("\n--- Probando búsqueda interna en la base vectorial ---")
#         consulta = "¿Cuál es la política de reembolsos?"
#         resultados = db.similarity_search(consulta, k=1)
#         print(f"Pregunta: {consulta}")
#         print(f"Fragmento más relevante recuperado:\n{resultados[0].page_content}")


#     print("\n--- Iniciando Agente Virtual de Atención al Cliente ---")
    
#     from modelo_agente import AgenteTienda
    
#     agente = AgenteTienda()
    
#     pregunta_1 = "¿Cuántos días tengo para devolver un producto?"
#     print(f"\n Cliente: {pregunta_1}")
#     print(f" Agente: {agente.responder_consulta(pregunta_1)}")
    
#     pregunta_2 = "que hora es?"
#     print(f"\n Cliente: {pregunta_2}")
#     print(f" Agente: {agente.responder_consulta(pregunta_2)}")
    
#     # pregunta_3 = "¿Tienen stock de iPhone 15 Pro Max?"
#     # print(f"\n Cliente: {pregunta_3}")
#     # print(f" Agente: {agente.responder_consulta(pregunta_3)}")