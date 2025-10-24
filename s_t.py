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
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# --- ESTILOS ---
st.markdown("""
    <style>
        body { background-color: #f5f6fa; }
        .stApp { background-color: #f8fafc; color: #1a1a1a; font-family: 'Poppins', sans-serif; }
        h1, h2, h3, h4 { color: #2f3640; text-align: center; }
        .css-1v3fvcr, .css-18ni7ap, .css-1n543e5 { background-color: #f0f4f8 !important; }
        .stButton>button {
            background: linear-gradient(to right, #0077b6, #0096c7);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            height: 3em;
            width: 100%;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background: linear-gradient(to right, #00b4d8, #48cae4);
            transform: scale(1.03);
        }
        .sidebar .sidebar-content {
            background-color: #e3f2fd;
        }
    </style>
""", unsafe_allow_html=True)

# --- TÍTULO PRINCIPAL ---
st.title("🎧 Traductor por Voz")
st.subheader("Escucho, traduzco y hablo por ti 🌍")

# --- IMAGEN PRINCIPAL ---
if os.path.exists('OIG7.jpg'):
    image = Image.open('OIG7.jpg')
    st.image(image, width=280)

# --- SIDEBAR ---
with st.sidebar:
    st.subheader("🔊 Instrucciones")
    st.write("""
    1️⃣ Presiona **Escuchar 🎤**  
    2️⃣ Habla claramente lo que deseas traducir  
    3️⃣ Selecciona idioma de entrada y salida  
    4️⃣ ¡Escucha tu traducción en voz alta!
    """)

# --- BOTÓN DE ESCUCHA ---
st.write("Pulsa el botón y habla lo que quieres traducir:")

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

# --- SI HAY RESULTADO ---
if result and "GET_TEXT" in result:
    text = str(result.get("GET_TEXT"))
    st.success(f"🗣️ Texto detectado: {text}")
    translator = Translator()

    st.markdown("---")
    st.header("🈹 Configura tu traducción")

    # --- Selección de idiomas ---
    idiomas = {
        "Inglés": "en",
        "Español": "es",
        "Bengalí": "bn",
        "Coreano": "ko",
        "Mandarín": "zh-cn",
        "Japonés": "ja",
    }

    input_language = idiomas[st.selectbox("🌐 Idioma de entrada", idiomas.keys())]
    output_language = idiomas[st.selectbox("🌍 Idioma de salida", idiomas.keys())]

    # --- Acento del inglés ---
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

    # --- Función de traducción y TTS ---
    def text_to_speech(input_lang, output_lang, text, tld):
        translation = translator.translate(text, src=input_lang, dest=output_lang)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_lang, tld=tld, slow=False)
        filename = "temp/audio_traducido.mp3"
        os.makedirs("temp", exist_ok=True)
        tts.save(filename)
        return filename, trans_text

    mostrar_texto = st.checkbox("📝 Mostrar texto traducido")

    if st.button("🔁 Convertir y reproducir"):
        audio_path, translated_text = text_to_speech(input_language, output_language, text, tld)
        st.audio(audio_path, format="audio/mp3")
        if mostrar_texto:
            st.markdown("### 🪶 Traducción:")
            st.info(translated_text)

    # --- Limpieza de archivos antiguos ---
    def remove_old_audio(days=7):
        mp3_files = glob.glob("temp/*.mp3")
        now = time.time()
        for f in mp3_files:
            if os.stat(f).st_mtime < now - (days * 86400):
                os.remove(f)
    remove_old_audio()
