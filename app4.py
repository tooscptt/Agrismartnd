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

# --- 2. CSS SEDERHANA (HANYA WARNA & FONT) ---
# Kita hapus CSS yang bikin tombol macet. Cukup ganti warna background saja.
st.markdown("""
<style>
    /* Background Warna Krem Lembut (Khas Alam) */
    .stApp {
        background-color: #fdfcf0;
    }
    
    /* Tombol Utama Hijau */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        font-weight: bold;
        border: 1px solid #2e7d32;
    }
    
    /* Mempercantik Judul */
    h1, h2, h3 {
        color: #1b5e20;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. SETUP API KEY & SUARA ---
if 'enable_tts' not in st.session_state: st.session_state['enable_tts'] = True

try:
    if "API_KEY" in st.secrets:
        api_key = st.secrets["API_KEY"]
    else:
        api_key = "MASUKKAN_KEY_LOKAL" 
    if api_key and "MASUKKAN" not in api_key: genai.configure(api_key=api_key)
except: pass

def text_to_speech(text):
    if not st.session_state['enable_tts']: return None
    try:
        tts = gTTS(text=text, lang='id', slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            return fp.name
    except: return None

# --- 4. HALAMAN LOGIN (KARTU TENGAH) ---
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1]) # Biar posisinya di tengah
    with col2:
        # Gunakan 'border=True' pengganti CSS Card yang error kemarin
        with st.container(border=True):
            st.markdown("<h1 style='text-align: center;'>🌾 AgriSmart</h1>", unsafe_allow_html=True)
            st.write("Sistem Pakar Pertanian Berbasis AI")
            
            # Gambar Banner Login (Menggunakan link stabil Wikimedia)
            st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Padi_sawah.jpg/640px-Padi_sawah.jpg", caption="Mitra Petani Indonesia")
            
            with st.form("login"):
                user = st.text_input("Username", placeholder="admin")
                pwd = st.text_input("Password", type="password", placeholder="petani123")
                
                if st.form_submit_button("Masuk Sekarang", type="primary"):
                    if user == "admin" and pwd == "petani123":
                        st.session_state['is_logged_in'] = True
                        st.rerun()
                    else:
                        st.error("Gagal masuk. Cek username/password.")

# --- 5. DASHBOARD UTAMA ---
def dashboard_page():
    # Sidebar
    with st.sidebar:
        st.header("Menu Utama")
        selected = option_menu(
            menu_title=None,
            options=["Beranda", "Konsultasi", "Ensiklopedia", "Logout"],
            icons=["house", "robot", "book", "box-arrow-right"],
            default_index=0,
            styles={"nav-link-selected": {"background-color": "#2e7d32"}}
        )

    # --- KONTEN BERANDA ---
    if selected == "Beranda":
        st.title("Halo, Sobat Tani! 👋")
        
        # Gambar Banner Utama (Link stabil)
        # Jika gambar ini gagal load di HP, dia tidak akan bikin error
        try:
            st.image("https://upload.wikimedia.org/wikipedia/commons/9/98/Rice_fields_in_Bali.jpg", use_container_width=True)
        except:
            st.warning("Gambar tidak muncul karena sinyal, tapi aplikasi tetap aman!")

        st.divider()

        # MENU CEPAT (Pakai Kolom & Container Asli Streamlit - PASTI BISA DIKLIK)
        col1, col2 = st.columns(2)
        
        with col1:
            with st.container(border=True): # Ini kotak bergaris
                st.subheader("🤖 Tanya Dokter AI")
                st.write("Punya tanaman sakit? Foto dan tanya solusinya di sini.")
                # Tombol ini hanya dummy info, user harus klik sidebar
                st.info("👈 Klik menu 'Konsultasi' di kiri untuk mulai.")

        with col2:
            with st.container(border=True):
                st.subheader("📚 Kamus Hama")
                st.write("Cari info wereng, ulat, dan penyakit umum.")
                st.info("👈 Klik menu 'Ensiklopedia' di kiri.")

    # --- KONTEN KONSULTASI (INTI APLIKASI) ---
    elif selected == "Konsultasi":
        st.title("🤖 Dokter Tanaman")
        st.caption("Upload foto daun atau ketik keluhan Anda.")

        # Area Chat (Scrollable)
        chat_box = st.container(height=400, border=True)
        with chat_box:
            if "history" not in st.session_state: st.session_state.history = []
            for chat in st.session_state.history:
                with st.chat_message(chat["role"]):
                    st.markdown(chat["content"])
                    if "audio" in chat: st.audio(chat["audio"])

        # Area Input (Di Bawah)
        with st.container(border=True):
            col_up, col_in = st.columns([1, 4])
            with col_up:
                upl = st.file_uploader("📷 Foto", type=["jpg","png"], label_visibility="collapsed")
            with col_in:
                txt = st.chat_input("Tulis keluhan tanaman...")
            
            if upl: st.image(upl, width=100, caption="Siap kirim")

        # Logika AI
        if txt:
            # Update Tampilan User
            with chat_box:
                with st.chat_message("user"):
                    st.write(txt)
                    if upl: st.image(upl, width=200)
            st.session_state.history.append({"role":"user", "content":txt})

            # Proses AI
            with st.spinner("Sedang meneliti..."):
                try:
                    model = genai.GenerativeModel("gemini-flash-latest")
                    content = [txt]
                    prompt = "Kamu ahli tani. Jawab ringkas dan jelas. "
                    if upl:
                        img = PIL.Image.open(upl)
                        content.append(img)
                        prompt += "Analisa gambar ini. "
                    content[0] = prompt + content[0]

                    resp = model.generate_content(content)
                    ai_txt = resp.text
                    audio = text_to_speech(ai_txt)

                    # Tampilkan Jawaban
                    with chat_box:
                        with st.chat_message("assistant"):
                            st.markdown(ai_txt)
                            if audio: st.audio(audio)
                    
                    msg = {"role":"assistant", "content":ai_txt}
                    if audio: msg["audio"] = audio
                    st.session_state.history.append(msg)
                except Exception as e:
                    st.error("Gagal koneksi AI. Coba lagi.")

    # --- KONTEN ENSIKLOPEDIA ---
    elif selected == "Ensiklopedia":
        st.title("📚 Ensiklopedia Tani")
        with st.expander("🌾 Hama Wereng Coklat (Padi)"):
            st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Nilaparvata_lugens_01.jpg/320px-Nilaparvata_lugens_01.jpg")
            st.write("Menyebabkan padi kering terbakar. Obat: Imidakloprid.")
        with st.expander("🌶️ Penyakit Patek (Cabai)"):
            st.write("Jamur Colletotrichum. Buah jadi busuk hitam. Obat: Fungisida.")

    # --- LOGOUT ---
    elif selected == "Logout":
        st.session_state['is_logged_in'] = False
        st.rerun()

# --- 6. MAIN ---
if __name__ == "__main__":
    if 'is_logged_in' not in st.session_state: st.session_state['is_logged_in'] = False
    
    if st.session_state['is_logged_in']:
        dashboard_page()
    else:
        login_page()