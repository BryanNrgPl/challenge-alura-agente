import streamlit as st
from dotenv import load_dotenv
from modelo_agente import AgenteTienda, RUTA_ABSOLUTA_LOG
import os
from agente import extraer_inventario, extraer_y_fragmentar_politicas, crear_base_conocimiento


# EMOJIS
# 🏠 🔍 ⚙️ 💡 🔔 📂 🗑️ ✉️ 📱 🤖 💻 👍 👎 🖥️ 🚀 🔒 🔑 📊 🎨 💖 🛠️ 💼 ⚙️ 🛒 💰 📝 📚 💬 ⚠️ ⭐ 🔥 📍 📢 ➡️ ⬅️ ⬆️

# Pestaña del navegador
st.set_page_config(
    page_title="Asistente Virtual - Tienda Online",
    page_icon="🛒",
    layout="wide"
)

load_dotenv()

if not os.path.exists("base_vectores") and not os.path.exists("base_vectors"):
    ruta_csv = "datos/inventario_tienda.csv"
    ruta_tienda_txt = "datos/politicas_tienda.txt"
    ruta_colaboradores_txt = "datos/politicas_colaboradores.txt"
    with st.spinner("Inicializando base de conocimientos en el servidor."):
        # Cargar inventario
        productos_limpios = extraer_inventario(ruta_csv) if os.path.exists(ruta_csv) else[]
        # Cargar y fragmentar politicas tienda
        fragmentos_tienda = extraer_y_fragmentar_politicas(ruta_tienda_txt) if os.path.exists(ruta_tienda_txt) else[]
        # Cargar y fragmentar politicas colabordores
        fragmentos_colaboradores = extraer_y_fragmentar_politicas(ruta_colaboradores_txt) if os.path.exists(ruta_colaboradores_txt) else []
        # Unir fragmentos
        fragmentos_politicas_totales = fragmentos_tienda + fragmentos_colaboradores
        # Base de conocimiento con todo indexado
        crear_base_conocimiento(productos_limpios, fragmentos_politicas_totales)

# Inicializar el agente en la sesión de Streamlit
if "agente" not in st.session_state:
    try:
        st.session_state.agente = AgenteTienda()
    except Exception as e:
        st.error(f"Error al inicializar el agente: {e}")

# Inicializar historial de chat
if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {
            "role": "assistant", 
            "content": "¡Hola! Soy tu asistente de atención híbrida. ¿En qué puedo ayudarte hoy respecto a nuestro catálogo de productos, políticas de la tienda o dudas de colaboradores?",
            "fuentes": []
        }
    ]

# SIDEBAR
with st.sidebar:
    st.header("⚙️ Consola de Auditoría (Admin)")
    st.write("Herramientas de monitoreo de ejecución exigidas para control interno.")
    
    if st.checkbox("Ver Registro de Logs en Tiempo Real (ejecucion.log)"):
        st.subheader("📋 Últimas líneas del Log:")
        if os.path.exists(RUTA_ABSOLUTA_LOG):
            with open(RUTA_ABSOLUTA_LOG, "r", encoding="utf-8") as f:
                lineas = f.readlines()
                # últimas 15 líneas
                for linea in lineas[-15:]:
                    st.text(linea.strip())
        else:
            st.info("Aún no se ha generado el archivo de logs.")


# Diseño de la interfaz
st.title("Asistente Virtual de Atención al Cliente")
st.caption("Challenge Alura - Sistema RAG con Trazabilidad Completa e Interfaz")

st.divider()

# Mostrar mensajes anteriores
for idx, msg in enumerate(st.session_state.mensajes):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        if msg["role"] == "assistant" and msg.get("fuentes"):
            with st.expander("📚 Ver fuentes y documentos utilizados"):
                for f_idx, fuente in enumerate(msg["fuentes"], 1):
                    st.markdown(f"**Fragmento {f_idx}** *(Archivo Origen: `{fuente['origen']}`)*")
                    st.write(fuente["texto"])
                    st.divider()
        
        if msg["role"] == "assistant" and idx > 0:
            col1, col2, _ = st.columns([1, 1, 8])
            with col1:
                if st.button("👍", key=f"up_{idx}"):
                    st.session_state.agente.registrar_feedback_externo(
                        st.session_state.mensajes[idx-1]["content"], msg["content"], "POSITIVO"
                    )
                    st.toast("¡Gracias por tu feedback positivo!", icon="💖")
            with col2:
                if st.button("👎", key=f"down_{idx}"):
                    st.session_state.agente.registrar_feedback_externo(
                        st.session_state.mensajes[idx-1]["content"], msg["content"], "NEGATIVO"
                    )
                    st.toast("Feedback registrado. Revisaremos esta respuesta.", icon="⚠️")

# Capturar entrada del usuario
if pregunta := st.chat_input("Escribe tu consulta aquí..."):
    # 1. Mostrar la pregunta del usuario en la UI
    with st.chat_message("user"):
        st.markdown(pregunta)
    # Guardar en el historial
    st.session_state.mensajes.append({"role": "user", "content": pregunta, "fuentes": []})

    # 2. Generar la respuesta

    if "agente" in st.session_state:
        with st.chat_message("assistant"):
            with st.spinner("Buscando en la base de conocimientos..."):
                resultado_rag = st.session_state.agente.responder_consulta(pregunta)
                respuesta_texto = resultado_rag["respuesta"]
                fuentes_usadas = resultado_rag["fuentes"]

                st.markdown(respuesta_texto)

                if fuentes_usadas:
                    with st.expander("📚 Ver fuentes y documentos utilizados"):
                        for f_idx, fuente in enumerate(fuentes_usadas, 1):
                            st.markdown(f"**Fragmento {f_idx}** *(Archivo Origen: `{fuente['origen']}`)*")
                            st.write(fuente["texto"])
                            st.divider()

        # Guardar la respuesta en el historial
        st.session_state.mensajes.append({
            "role": "assistant",
            "content": respuesta_texto,
            "fuentes": fuentes_usadas
        })
        #st.session_state.mensajes.append({"role": "assistant", "content": respuesta})

        st.rerun()