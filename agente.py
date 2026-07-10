import os
from dotenv import load_dotenv
import pandas as pd

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

#  PRUEBA
if __name__ == "__main__":
    ruta = "datos/inventario_tienda.csv" 
    if os.path.exists(ruta):
        print("--- Extrayendo datos del Inventario ---")
        productos_limpios = extraer_inventario(ruta)

        for prod in productos_limpios[:3]:
            print(prod)