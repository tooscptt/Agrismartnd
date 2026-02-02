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
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed" # Sidebar tertutup saat login
)

# --- 2. CSS MODERN (TAMPILAN) ---
st.markdown("""
<style>
    .stApp {background-color: #f0f2f6;}
    
    /* Style Kartu Login */
    div[data-testid="stForm"] {
        background-color: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    
    /* Chat Bubble */
    .stChatMessage {
        background-color: white;
        border-radius: 15px;
        padding: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. API KEY HANDLER ---
try:
    if "API_KEY" in st.secrets:
        api_key = st.secrets["API_KEY"]
    else:
        # Fallback lokal
        api_key = "MASUKKAN_KEY_MANUAL_DISINI_JIKA_LOKAL" 
        
    if not api_key or "MASUKKAN" in api_key:
        # Jika key kosong/salah, jangan error merah, tapi info sopan
        pass 
    else:
        genai.configure(api_key=api_key)
except:
    st.warning("⚠️ API Key belum dikonfigurasi.")

# --- 4. FUNGSI SUARA (TTS) ---
def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang='id', slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            return fp.name
    except:
        return None

# --- 5. HALAMAN LOGIN (MODERN CARD) ---
def login_page():
    # Bikin kolom kosong kiri-kanan biar form ada di tengah (Centering)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center; color: #2e7d32;'>🌾 AgriSmart Pro</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Sistem Pakar Pertanian Berbasis AI</p>", unsafe_allow_html=True)
        st.write("") # Spacer

        # Form Login
        with st.form("login_form"):
            st.subheader("Login Akses")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Masuk Sistem", use_container_width=True)
            
            if submitted:
                if username == "admin" and password == "petani123":
                    st.session_state['is_logged_in'] = True
                    st.rerun()
                else:
                    st.error("Username atau Password salah!")

# --- 6. DASHBOARD UTAMA (SETELAH LOGIN) ---
def dashboard_page():
    # Sidebar hanya muncul setelah login
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/628/628283.png", width=80)
        
        selected = option_menu(
            menu_title="Navigasi",
            options=["Konsultasi AI", "Panduan", "Logout"],
            icons=["robot", "book", "box-arrow-right"],
            menu_icon="list",
            default_index=0,
            styles={
                "nav-link-selected": {"background-color": "#2e7d32"},
            }
        )

    # --- LOGIKA HALAMAN ---
    
    # A. HALAMAN KONSULTASI
    if selected == "Konsultasi AI":
        st.title("🤖 Konsultasi Dokter Tanaman")
        st.caption("Silakan tanya atau upload foto daun yang sakit.")
        st.divider()

        # History Chat
        if "history" not in st.session_state:
            st.session_state.history = []

        # Tampilkan Chat
        for chat in st.session_state.history:
            with st.chat_message(chat["role"]):
                st.markdown(chat["content"])
                if "audio" in chat:
                    st.audio(chat["audio"], format="audio/mp3")

        # Area Input (Fixed di bawah)
        with st.container():
            col_upload, col_text = st.columns([1, 4])
            with col_upload:
                # Tombol upload kecil
                uploaded_file = st.file_uploader("📸 Foto", type=["jpg","png"], label_visibility="collapsed")
            
            with col_text:
                user_input = st.chat_input("Tulis keluhan tanaman...")

        # Preview Gambar jika ada
        if uploaded_file:
            st.image(uploaded_file, caption="Foto akan dikirim...", width=150)

        # Proses Logika AI
        if user_input:
            # Tampilkan user input
            with st.chat_message("user"):
                st.write(user_input)
                if uploaded_file:
                    st.image(uploaded_file, width=200)
            
            st.session_state.history.append({"role": "user", "content": user_input})

            # AI Processing
            with st.spinner("Sedang menganalisa & memproses suara..."):
                try:
                    model = genai.GenerativeModel("gemini-flash-latest")
                    
                    # Siapkan konten
                    content = [user_input]
                    prompt_add = "Jawablah sebagai ahli pertanian yang ramah. Ringkas saja. "
                    
                    if uploaded_file:
                        img = PIL.Image.open(uploaded_file)
                        content.append(img)
                        prompt_add += "Analisa gambar ini. "
                    
                    # Modifikasi prompt sistem lewat text input
                    content[0] = prompt_add + content[0]

                    response = model.generate_content(content)
                    ai_text = response.text
                    
                    # Bikin Suara
                    audio_path = text_to_speech(ai_text)

                    # Tampilkan Balasan
                    with st.chat_message("assistant"):
                        st.markdown(ai_text)
                        if audio_path:
                            st.audio(audio_path, format="audio/mp3")
                    
                    # Simpan ke history
                    msg = {"role": "assistant", "content": ai_text}
                    if audio_path: msg["audio"] = audio_path
                    st.session_state.history.append(msg)

                except Exception as e:
                    st.error(f"Error: {e}")

    # B. HALAMAN PANDUAN
    elif selected == "Panduan":
        st.title("📖 Panduan Penggunaan")
        st.info("Aplikasi ini menggunakan Gemini 2.0 Flash Latest.")
        st.markdown("""
        1. **Login** menggunakan akun admin.
        2. Masuk ke menu **Konsultasi AI**.
        3. Klik ikon 📸 untuk upload foto daun (opsional).
        4. Ketik pertanyaan dan kirim.
        5. Dengarkan jawaban AI lewat speaker.
        """)

    # C. LOGOUT
    elif selected == "Logout":
        st.session_state['is_logged_in'] = False
        st.rerun()

# --- 7. MAIN CONTROL FLOW ---
if __name__ == "__main__":
    # Cek status login
    if 'is_logged_in' not in st.session_state:
        st.session_state['is_logged_in'] = False

    # Tentukan halaman mana yang muncul
    if st.session_state['is_logged_in']:
        dashboard_page() # Masuk Dashboard
    else:
        login_page()     # Tampilkan Login