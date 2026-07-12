import streamlit as st
from dotenv import load_dotenv

from modelo_agente import AgenteTienda

# Pestaña del navegador
st.set_page_config(
    page_title="Asistente Virtual - Tienda Online",
    page_icon="🤖",
    layout="centered"
)

load_dotenv()

# Inicializar el agente en la sesión de Streamlit para no recargarlo en cada clic
if "agente" not in st.session_state:
    try:
        st.session_state.agente = AgenteTienda()
    except Exception as e:
        st.error(f"Error al inicializar el agente: {e}")

# Inicializar historial de chat
if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": "¡Hola! Soy tu asistente de atención al cliente. ¿En qué puedo ayudarte hoy respecto a nuestro catálogo de productos o políticas de la tienda?"}
    ]

# Diseño de la interfaz

st.title("🤖 Asistente Virtual de Atención al Cliente")
st.subheader("Challenge Alura - Sistema RAG Avanzado")
st.write("Consulta disponibilidad de stock, precios de productos o detalles sobre nuestras políticas de privacidad y devoluciones de manera inmediata.")

st.divider()

# Mostrar los mensajes historicos del chat en la pantalla
for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Capturar entrada del usuario

if pregunta := st.chat_input("Escribe tu consulta aquí..."):
    # 1. Mostrar la pregunta del usuario en la UI
    with st.chat_message("user"):
        st.markdown(pregunta)
    # Guardar en el historial
    st.session_state.mensajes.append({"role": "user", "content": pregunta})

    # 2. Generar la respuesta usando nuestro backend

    if "agente" in st.session_state:
        with st.chat_message("assistant"):
            with st.spinner("Buscando en la base de conocimientos..."):
                respuesta = st.session_state.agente.responder_consulta(pregunta)
                st.markdown(respuesta)

        # Guardar la respuesta en el historial
        st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
    else:
        st.error("El agente no está disponible. Revisa la configuración de tu GEMINI_API_KEY.")