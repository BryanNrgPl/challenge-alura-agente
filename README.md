# Asistente Virtual RAG - Tienda Online

Este proyecto implementa un **Agente de Atención al Cliente Inteligente** basado en la arquitectura RAG (Retrieval-Augmented Generation). El sistema recupera en tiempo real información estructurada de productos (CSV) y políticas internas (TXT) para dar respuestas precisas y libres de alucinaciones.

El agente se encuentra completamente desplegado en producción dentro de **Oracle Cloud Infrastructure (OCI)** con HTTPS activo, logs en tiempo real y almacenamiento de auditoría.

---

## Decisiones de Diseño e Inferencia (Groq vs. Gemini)

Originalmente, el sistema operaba únicamente con Google Gemini. Sin embargo, bajo la capa gratuita (*Free Tier*), el envío continuo de contexto vectorizado provocaba constantes bloqueos por límite de cuota (`429 RESOURCE_EXHAUSTED`). Debido al sistema de reintentos automáticos del SDK, la latencia de respuesta se disparaba hasta los **~30 segundos**.

### Arquitectura de Inferencia Actual:

* **Modelo Principal:** **`llama-3.3-70b-versatile` a través de Groq**. Gracias a su tecnología LPU (Language Processing Unit), procesa y responde las consultas del RAG en **milisegundos (menos de 1 segundo)**.
* **Modelo de Fallback (Resiliencia):** **`gemini-3.5-flash`** integrado de forma nativa mediante `with_fallbacks` de LangChain. Si la API de Groq llega a fallar o excede cuotas, Gemini absorbe la petición inmediatamente sin interrumpir la experiencia de usuario.

---

## Infraestructura y Despliegue en OCI

El despliegue en producción fue diseñado bajo buenas prácticas de administración de sistemas y redes en la nube:

* **Instancia de Cómputo (VM Compute):** Servidor Linux en OCI ejecutando la aplicación Streamlit en segundo plano.
* **Red Virtual (VCN):** Configuración de listas de seguridad de OCI para abrir únicamente los puertos de navegación estándar: `80` (HTTP) y `443` (HTTPS).
* **Nginx (Reverse Proxy):** Servidor web que actúa como proxy inverso, recibiendo las conexiones en el puerto de internet y redirigiéndolas internamente al puerto nativo de Streamlit (`8501`).
* **SSL / HTTPS:** Certificado SSL instalado y configurado en Nginx para cifrar todo el tráfico de datos y forzar la redirección automática de HTTP a HTTPS.
* **Control de Versiones (Git):** Despliegue automatizado directo desde el repositorio remoto en GitHub hacia la máquina virtual.

---

## Registro de Ejecución y Evidencias (OCI Object Storage)

Para cumplir con los requisitos de auditoría y trazabilidad de la ejecución en la nube, las capturas de logs y el video de demostración se alojan de forma óptima en un bucket público de **OCI Object Storage**:

### Demostración en Vivo (Video)

* **[Ver Video de Ejecución del Agente en OCI](https://objectstorage.us-ashburn-1.oraclecloud.com/n/idszb3n9s7g9/b/assets-agente-rag/o/video.mp4)** *(Demostración en caliente con preguntas rápidas y flujo de logs).*

### Capturas de Trazabilidad y Logs

A continuación, se adjuntan las evidencias de la interfaz web, el sistema de logs locales que corre en la VM y las fuentes utilizadas para responder:

#### 1. Consola de Auditoría en Producción
La barra lateral integrada permite auditar las últimas líneas de `ejecucion.log` directamente desde la app en caliente.

![Logs en Caliente](https://objectstorage.us-ashburn-1.oraclecloud.com/n/idszb3n9s7g9/b/assets-agente-rag/o/captura1.jpg)

#### 2. Trazabilidad RAG (Uso de Fuentes)
El agente expone al usuario final y al auditor las fuentes exactas de los documentos indexados de donde extrajo los datos.

![Trazabilidad de Fuentes](https://objectstorage.us-ashburn-1.oraclecloud.com/n/idszb3n9s7g9/b/assets-agente-rag/o/captura2.jpg)

#### 3. Auditoría del Servidor OCI
Logs internos que registran el timestamp, el inicio de carga del Vector Store (FAISS) y las consultas procesadas.

![Logs del Servidor](https://objectstorage.us-ashburn-1.oraclecloud.com/n/idszb3n9s7g9/b/assets-agente-rag/o/captura3.jpg)

---

## Configuración y Ejecución Local

Para probar o replicar el proyecto en tu máquina local de forma aislada sin ensuciar tus dependencias globales, sigue estos pasos estructurados:

### 1. Clonar el código fuente
Clona el repositorio en tu máquina local y accede a la carpeta del proyecto:

```bash
git clone https://github.com/BryanNrgPl/challenge-alura-agente.git
cd challenge-alura-agente
```
### 2. Inicializar Entorno Virtual
Crea un entorno virtual para aislar las librerías de Python:

* En Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
* En Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar Dependencias
Asegúrate de instalar los requisitos del sistema listados en el archivo requirements.txt:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
### 4. Variables de Entorno
Crea un archivo .env en la raíz del proyecto y define tus credenciales de API de la siguiente manera:
```bash
GEMINI_API_KEY="tu-clave-api-de-google-gemini"
GROQ_API_KEY="tu-clave-api-de-groq"
```
### 5. Iniciar la Aplicación
Ejecuta el servidor web local. Al iniciar por primera vez, el sistema autodetectará que no existe la base vectorial y procesará los CSV/TXT locales de inmediato:
```bash
streamlit run app.py
```
---

## Tecnologías y Herramientas Utilizadas

El ecosistema de desarrollo e infraestructura de este proyecto está compuesto por las siguientes herramientas:

### Inteligencia Artificial y RAG
* **LangChain:** Framework para la orquestación del flujo RAG, gestión de prompts y políticas de fallback.
* **FAISS (Facebook AI Similarity Search):** Base de datos vectorial local para el almacenamiento y búsqueda de similitud eficiente de los embeddings.
* **Llama 3.3 (vía Groq):** Modelo de lenguaje principal optimizado para baja latencia de respuesta.
* **Gemini 3.5 Flash (vía Google AI):** Modelo de lenguaje secundario configurado como respaldo de alta resiliencia.

### Desarrollo y Lenguajes
* **Python:** Lenguaje principal para toda la lógica de backend, procesamiento de datos y embeddings.
* **Streamlit:** Framework ágil de Python utilizado para construir la interfaz de usuario web y la consola de logs en tiempo real.

### Infraestructura y Redes (Cloud & DevOps)
* **Oracle Cloud Infrastructure (OCI):**
  * **VM Compute Instance:** Servidor en la nube (Linux) que aloja y ejecuta la aplicación en producción de manera continua.
  * **VCN (Virtual Cloud Network):** Configuración de subredes y reglas de seguridad de puertos para el tráfico web seguro.
  * **OCI Object Storage:** Almacenamiento de objetos en la nube utilizado para servir de forma pública los assets, capturas de auditoría y videos de demostración.
* **Nginx:** Servidor web configurado como Proxy Inverso para redirigir de forma segura el tráfico externo hacia el puerto interno de Streamlit.
* **Certbot (Let's Encrypt):** Herramienta para la generación y renovación automática del certificado SSL gratuito.
* **DuckDNS:** Servicio de DNS dinámico utilizado para asociar un dominio gratuito y amigable a la dirección IP pública de la máquina virtual en OCI.
* **Git & GitHub:** Herramientas para el control de versiones y el flujo de despliegue continuo hacia el servidor.