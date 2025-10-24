import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
from gtts import gTTS
from googletrans import Translator
import time
import glob

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Traductor por voz",
    page_icon="🎧",
    layout="centered",
)

# --- ESTILOS ---
st.markdown("""
    <style>
        /* Fondo general */
        .stApp {
            background: linear-gradient(180deg, #dbeafe 0%, #e0f2fe 50%, #f8fafc 100%);
            color: #1e293b;
            font-family: 'Poppins', sans-serif;
        }

        /* Títulos */
        h1 {
            text-align: center;
            font-size: 2.5em;
            background: linear-gradient(to right, #0ea5e9, #0284c7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }

        h2, h3 {
            text-align: center;
            color: #1e3a8a;
            font-weight: 600;
        }

        /* Botones principales */
        .stButton>button {
            background: linear-gradient(90deg, #2563eb, #1d4ed8);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            padding: 10px 25px;
            width: 100%;
            transition: 0.3s ease-in-out;
            box-shadow: 0px 4px 10px rgba(29, 78, 216, 0.3);
        }

        .stButton>button:hover {
            background: linear-gradient(90deg, #1e40af, #3b82f6);
            transform: scale(1.03);
            box-shadow: 0px 6px 14px rgba(29, 78, 216, 0.4);
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #eff6ff;
            border-right: 2px solid #bfdbfe;
        }

        /* Texto destacado */
        .highlight {
            background-color: #e0f2fe;
            border-left: 5px solid #0284c7;
            padding: 10px;
            border-radius: 6px;
        }

        /* Cuadros */
        .stSelectbox, .stTextInput, .stCheckbox {
            background-color: #f1f5f9 !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- INTERFAZ ---
st.title("🎧 Traductor por Voz")
st.markdown("<h3>Habla, traduce y escucha tu voz en otro idioma 🌍</h3>", unsafe_allow_html=True)

# --- Imagen principal ---
if os.path.exists('OIG7.jpg'):
    image = Image.open('OIG7.jpg')
    st.image(image, width=280)

# --- SIDEBAR ---
with st.sidebar:
    st.header("🗒️ Instrucciones")
    st.markdown("""
    1️⃣ Presiona **Escuchar 🎤**  
    2️⃣ Habla claramente lo que deseas traducir  
    3️⃣ Selecciona los idiomas de entrada y salida  
    4️⃣ Presiona **Convertir** y escucha tu traducción 🎶
    """)

# --- BOTÓN DE ESCUCHA ---
st.markdown("<div class='highlight'>Presiona el botón y habla lo que quieras traducir:</div>", unsafe_allow_html=True)
stt_button = Button(label="🎤 Escuchar", width=300, height=50)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'es-ES';
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0,
)

# --- PROCESAMIENTO ---
if result and "GET_TEXT" in result:
    text = str(result.get("GET_TEXT"))
    st.success(f"🗣️ Texto detectado: {text}")
    translator = Translator()

    st.divider()
    st.header("🌐 Configuración de traducción")

    # --- Idiomas disponibles ---
    idiomas = {
        "Inglés": "en",
        "Español": "es",
        "Bengalí": "bn",
        "Coreano": "ko",
        "Mandarín": "zh-cn",
        "Japonés": "ja",
    }

    input_language = idiomas[st.selectbox("🗨️ Idioma de entrada", idiomas.keys())]
    output_language = idiomas[st.selectbox("🔊 Idioma de salida", idiomas.keys())]

    # --- Acentos ---
    acentos = {
        "Defecto": "com",
        "Español": "com.mx",
        "Reino Unido": "co.uk",
        "Estados Unidos": "com",
        "Canadá": "ca",
        "Australia": "com.au",
        "Irlanda": "ie",
        "Sudáfrica": "co.za",
    }

    tld = acentos[st.selectbox("🎙️ Acento del inglés", acentos.keys())]

    # --- Función de traducción y voz ---
    def text_to_speech(input_lang, output_lang, text, tld):
        translation = translator.translate(text, src=input_lang, dest=output_lang)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_lang, tld=tld, slow=False)
        filename = "temp/audio_traducido.mp3"
        os.makedirs("temp", exist_ok=True)
        tts.save(filename)
        return filename, trans_text

    mostrar_texto = st.checkbox("📝 Mostrar texto traducido")

    if st.button("🔁 Traducir y reproducir"):
        audio_path, translated_text = text_to_speech(input_language, output_language, text, tld)
        st.markdown("### 🎧 Audio generado:")
        st.audio(audio_path, format="audio/mp3")
        if mostrar_texto:
            st.markdown("### 🪶 Traducción:")
            st.info(translated_text)

    # --- Limpieza automática ---
    def remove_old_audio(days=7):
        mp3_files = glob.glob("temp/*.mp3")
        now = time.time()
        for f in mp3_files:
            if os.stat(f).st_mtime < now - (days * 86400):
                os.remove(f)
    remove_old_audio()
