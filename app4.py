import streamlit as st
import google.generativeai as genai
import PIL.Image
from streamlit_option_menu import option_menu
from gtts import gTTS
import tempfile
import os

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="AgriSmart Pro",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS MODERN (YANG SUDAH DIPERBAIKI) ---
# Saya hapus bagian yang bikin tombol macet.
# Sekarang backgroundnya warna bersih, bukan gambar full screen yang berat.
st.markdown("""
<style>
    /* Latar belakang aplikasi yang bersih */
    .stApp {
        background-color: #f4f6f8;
    }
    
    /* Mempercantik Tombol agar terlihat modern */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid #2e7d32;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #2e7d32;
        color: white;
    }

    /* Mempercantik judul */
    h1, h2, h3 {
        color: #1b5e20;
        font-family: 'Segoe UI', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. API KEY HANDLER ---
try:
    if "API_KEY" in st.secrets:
        api_key = st.secrets["API_KEY"]
    else:
        api_key = "MASUKKAN_KEY_LOKAL_JIKA_ADA"
        
    if api_key and "MASUKKAN" not in api_key:
        genai.configure(api_key=api_key)
except: pass

# --- 4. FUNGSI SUARA (TTS) ---
def text_to_speech(text):
    if 'enable_tts' not in st.session_state: st.session_state['enable_tts'] = True
    if not st.session_state['enable_tts']: return None
    try:
        tts = gTTS(text=text, lang='id', slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            return fp.name
    except: return None

# --- 5. HALAMAN LOGIN (MODERN & RAPI) ---
def login_page():
    # Membuat 3 kolom agar kotak login ada di tengah (Centering)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        # Gunakan Container dengan Border (Pengganti Card CSS yang error)
        with st.container(border=True):
            st.markdown("<h1 style='text-align: center;'>🌾 AgriSmart</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: grey;'>Sistem Pakar Pertanian AI</p>", unsafe_allow_html=True)
            
            # Gambar Login (Saya ganti pakai Emoji besar biar pasti muncul)
            st.markdown("<h1 style='text-align: center; font-size: 60px;'>🚜</h1>", unsafe_allow_html=True)
            
            with st.form("login_form"):
                user = st.text_input("Username", placeholder="admin")
                pwd = st.text_input("Password", type="password", placeholder="petani123")
                st.write("") # Spasi
                
                # Tombol Submit
                submit = st.form_submit_button("🚀 Masuk Aplikasi", type="primary")
                
                if submit:
                    if user == "admin" and pwd == "petani123":
                        st.session_state['is_logged_in'] = True
                        st.rerun()
                    else:
                        st.error("Username/Password Salah!")

# --- 6. DASHBOARD (ISI APLIKASI) ---
def dashboard_page():
    # Sidebar Menu
    with st.sidebar:
        st.header("AgriSmart Pro")
        selected = option_menu(
            menu_title=None,
            options=["Beranda", "Konsultasi AI", "Ensiklopedia", "Pengaturan", "Logout"],
            icons=["house", "robot", "book", "gear", "box-arrow-right"],
            default_index=0,
            styles={
                "nav-link-selected": {"background-color": "#2e7d32"},
            }
        )

    # --- HALAMAN BERANDA ---
    if selected == "Beranda":
        st.title("Halo, Sobat Tani! 👋")
        st.write("Selamat datang di dashboard operasional.")
        st.divider()

        # Menu Cepat (Quick Actions)
        c1, c2, c3 = st.columns(3)
        
        with c1:
            with st.container(border=True):
                st.subheader("🤖 Konsultasi")
                st.write("Tanya jawab masalah tanaman.")
                # Tombol ini hanya info visual
                st.info("👈 Pilih menu 'Konsultasi AI'")
        
        with c2:
            with st.container(border=True):
                st.subheader("📚 Pustaka")
                st.write("Cari data hama & penyakit.")
                st.info("👈 Pilih menu 'Ensiklopedia'")

        with c3:
            with st.container(border=True):
                st.subheader("⚙️ Status")
                st.metric("Koneksi AI", "Online 🟢")
                st.write("Sistem berjalan normal.")

    # --- HALAMAN KONSULTASI (INTI) ---
    elif selected == "Konsultasi AI":
        st.title("🤖 Dokter Tanaman")
        st.caption("Upload foto daun atau ketik pertanyaan di bawah.")
        
        # Area Chat (Scrollable)
        chat_container = st.container(height=400, border=True)
        with chat_container:
            if "history" not in st.session_state: st.session_state.history = []
            for chat in st.session_state.history:
                with st.chat_message(chat["role"]):
                    st.markdown(chat["content"])
                    if "audio" in chat: st.audio(chat["audio"])

        # Area Input (Fixed di bawah)
        with st.container(border=True):
            c_up, c_txt = st.columns([1, 4])
            with c_up:
                upl = st.file_uploader("📷 Foto", type=["jpg","png"], label_visibility="collapsed")
            with c_txt:
                txt = st.chat_input("Tulis keluhan tanaman...")
            
            if upl: st.image(upl, width=100, caption="Foto Terlampir")

        # Logika AI
        if txt:
            # Tampilkan pesan user
            with chat_container:
                with st.chat_message("user"):
                    st.write(txt)
                    if upl: st.image(upl, width=200)
            st.session_state.history.append({"role":"user", "content":txt})

            # Proses AI
            with st.spinner("AI sedang berpikir..."):
                try:
                    model = genai.GenerativeModel("gemini-flash-latest")
                    content = [txt]
                    prompt = "Kamu ahli tani. Jawab ringkas & jelas. "
                    if upl:
                        content.append(PIL.Image.open(upl))
                        prompt += "Analisa gambar ini. "
                    content[0] = prompt + content[0]

                    resp = model.generate_content(content)
                    ai_txt = resp.text
                    audio = text_to_speech(ai_txt)

                    # Tampilkan balasan AI
                    with chat_container:
                        with st.chat_message("assistant"):
                            st.markdown(ai_txt)
                            if audio: st.audio(audio)
                    
                    msg = {"role":"assistant", "content":ai_txt}
                    if audio: msg["audio"] = audio
                    st.session_state.history.append(msg)
                except Exception as e:
                    st.error("Gagal koneksi AI.")

    # --- HALAMAN ENSIKLOPEDIA ---
    elif selected == "Ensiklopedia":
        st.title("📚 Pustaka Hama")
        
        with st.expander("🌾 Wereng Coklat (Padi)"):
            st.write("Gejala: Tanaman menguning dan kering (puso).")
            st.write("Solusi: Gunakan varietas tahan wereng & insektisida berbahan aktif imidakloprid.")
        
        with st.expander("🌶️ Patek / Antraknosa (Cabai)"):
            st.write("Gejala: Bercak hitam melingkar pada buah cabai.")
            st.write("Solusi: Potong buah sakit, semprot fungisida mankozeb.")

    # --- HALAMAN PENGATURAN ---
    elif selected == "Pengaturan":
        st.title("⚙️ Pengaturan")
        st.write("Sesuaikan preferensi aplikasi.")
        with st.container(border=True):
            st.session_state['enable_tts'] = st.toggle("Aktifkan Suara Robot", value=st.session_state.get('enable_tts', True))

    # --- LOGOUT ---
    elif selected == "Logout":
        st.session_state['is_logged_in'] = False
        st.rerun()

# --- 7. MAIN EXECUTION ---
if __name__ == "__main__":
    if 'is_logged_in' not in st.session_state:
        st.session_state['is_logged_in'] = False

    if st.session_state['is_logged_in']:
        dashboard_page()
    else:
        login_page()