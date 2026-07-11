import os
from dotenv import load_dotenv
import pandas as pd
import re
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY no está configurada en el archivo .env")

def extraer_inventario(ruta_csv):
    try:
        df = pd.read_csv(ruta_csv)
        fragmentos_inventario = []

        for _, fila in df.iterrows():
            texto_productto = (
                f"Producto: {fila['producto']} | "
                f"Categoría: {fila['categoria']} | "
                f"Precio: S/. {fila['precio_soles']} | "
                f"Stock disponible: {fila['stock']} unidades."
            )
            fragmentos_inventario.append(texto_productto)

        return fragmentos_inventario
    
    except Exception as e:
        print(f"Error al procesar el inventario en CSV: {e}")
        return []


def extraer_y_fragmentar_politicas(ruta_txt, tamaño_fragmento=500, solapamiento=100):
    try:
        with open(ruta_txt, "r", encoding="utf-8") as f:
            texto_completo = f.read()

        
        texto_limpio = re.sub(r'\s+', ' ', texto_completo.strip())

        fragmentos = []
        inicio = 0
        total_caracteres = len(texto_limpio)

        # Algoritmo chunking
        while inicio < total_caracteres:
            fin = inicio + tamaño_fragmento
            fragmento = texto_limpio[inicio:fin]
            fragmentos.append(fragmento)
            inicio += (tamaño_fragmento - solapamiento)

        return fragmentos
    except Exception as e:
        print(f"Error en el procesamiento del archivo de politicas TXT: {e}")
        return []


def crear_base_conocimiento(fragmentos_inventario, fragmentos_politicas, ruta_guardado="base_vectores"):

    try:
        todos_los_textos = fragmentos_inventario + fragmentos_politicas

        if not todos_los_textos:
            print("Sin texto disponible para generar la base de conocimiento")
            return None
        
        print(f"Generando embeddings para {len(todos_los_textos)} fragmentos totales.")

        # Inicializacion del modelo de embeddings de google
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

        db_vectorial = FAISS.from_texts(todos_los_textos, embeddings)

        # Guardado de base de datos localmente
        db_vectorial.save_local(ruta_guardado)
        print(f"Base de conocimiento vectorial guardada localmente en: {ruta_guardado}")

        return db_vectorial
    
    except Exception as e:
        print(f"Error al crear base de conocimiento: {e}")
        return None






#  PRUEBAS
if __name__ == "__main__":

    # Rutas de archivos
    ruta_csv = "datos/inventario_tienda.csv" 
    ruta_txt = "datos/politicas_tienda.txt"

    # 1. PRUEBA DE INVENTARIO
    if os.path.exists(ruta_csv):
        print("--- Extrayendo datos del Inventario ---")
        productos_limpios = extraer_inventario(ruta_csv)

        for prod in productos_limpios[:1]:
            print(prod)

    # 2. PRUEBA DE POLITICAS
    if os.path.exists(ruta_txt):
        print("\n--- Extrayendo y fragmentando Políticas ---")
        fragmentos_politicas = extraer_y_fragmentar_politicas(ruta_txt)
        
        for i, chunk in enumerate(fragmentos_politicas[:1]):
            print(f"Fragmento {i+1}: {chunk}\n")

    # 3. PRUEBA DE EMBEDDINGS / BASE VECTORIAL
    print("\n--- Creando Base de Conocimiento Vectorial ---")
    db = crear_base_conocimiento(productos_limpios, fragmentos_politicas)

    if db:
        print("\n--- Probando búsqueda interna en la base vectorial ---")
        consulta = "¿Cuál es la política de reembolsos?"
        resultados = db.similarity_search(consulta, k=1)
        print(f"Pregunta: {consulta}")
        print(f"Fragmento más relevante recuperado:\n{resultados[0].page_content}")