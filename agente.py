import os
from dotenv import load_dotenv
import pandas as pd
import re

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



#  PRUEBAS
if __name__ == "__main__":
    ruta = "datos/inventario_tienda.csv" 

    #  PRUEBA DE INVENTARIO
    if os.path.exists(ruta):
        print("--- Extrayendo datos del Inventario ---")
        productos_limpios = extraer_inventario(ruta)

        for prod in productos_limpios[:1]:
            print(prod)

    # 2. PRUEBA DE POLITICAS
    ruta_txt = "datos/politicas_tienda.txt"  # Asegúrate de tener este archivo en tu carpeta datos/
    if os.path.exists(ruta_txt):
        print("\n--- Extrayendo y fragmentando Políticas ---")
        fragmentos_politicas = extraer_y_fragmentar_politicas(ruta_txt)
        
        for i, chunk in enumerate(fragmentos_politicas[:2]):
            print(f"Fragmento {i+1}: {chunk}\n")