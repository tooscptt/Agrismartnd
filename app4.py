import streamlit as st
import google.generativeai as genai
import PIL.Image
from streamlit_option_menu import option_menu
from gtts import gTTS
import tempfile
import os

# --- 1. KONFIGURASI HALAMAN & CSS MODERN ---
st.set_page_config(
    page_title="AgriSmart Pro",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# URL Gambar Bernuansa Tani (Bisa diganti link lain)
LOGIN_BG_URL = "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1932&auto=format&fit=crop"
BANNER_URL = "https://images.unsplash.com/photo-1625246333195-584d94797c91?q=80&w=2071&auto=format&fit=crop"

st.markdown(f"""
<style>
    /* Latar Belakang Halaman Utama (Dashboard) */
    .stApp {{
        background-color: #f8f9fa;
    }}
    
    /* CSS Khusus Halaman Login (Background Gambar Full) */
    [data-testid="stHeader"] {{background: transparent;}}
    .login-bg {{
        background-image: url("{LOGIN_BG_URL}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        z-index: -1;
        filter: brightness(0.7); /* Gelapkan dikit biar tulisan terbaca */
    }}
    
    /* Style Kartu Login yang Minimalis Transparan */
    .login-card {{
        background-color: rgba(255, 255, 255, 0.95);
        padding: 40px;
        border-radius: 25px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        text-align: center;
    }}

    /* Style Container/Kartu di Dashboard */
    .dashboard-card {{
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #eef0f2;
    }}
    
    /* Menghias Chat Bubble */
    .stChatMessage {{
        background-color: white;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
    }}
    
    /* Judul Halaman yang Modern */
    .page-title {{
        font-size: 2.2rem;
        font-weight: 700;
        color: #2e7d32; /* Hijau Tani */
        margin-bottom: 10px;
    }}
</style>
""", unsafe_allow_html=True)

# --- 2. HANDLER API KEY & SETTINGS ---
# Inisialisasi state untuk pengaturan suara
if 'enable_tts' not in st.session_state:
    st.session_state['enable_tts'] = True

try:
    if "API_KEY" in st.secrets:
        api_key = st.secrets["API_KEY"]
    else:
        api_key = "MASUKKAN_KEY_LOKAL_DISINI"
        
    if not api_key or "MASUKKAN" in api_key: pass
    else: genai.configure(api_key=api_key)
except: pass

# --- 3. FUNGSI TEXT-TO-SPEECH ---
def text_to_speech(text):
    # Cek dulu apakah fitur suara diaktifkan di pengaturan
    if not st.session_state['enable_tts']:
        return None
    try:
        tts = gTTS(text=text, lang='id', slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            return fp.name
    except: return None

# --- 4. HALAMAN LOGIN (DENGAN BACKGROUND TANI) ---
def login_page():
    # Suntikkan div background
    st.markdown('<div class="login-bg"></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    with col2:
        # Gunakan container untuk efek kartu
        with st.container():
            st.markdown('<div class="login-card">', unsafe_allow_html=True)
            st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=100)
            st.markdown("<h2 style='color: #2e7d32;'>Selamat Datang Petani</h2>", unsafe_allow_html=True)
            st.write("Masuk untuk memulai konsultasi cerdas.")
            
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Contoh: admin")
                password = st.text_input("Password", type="password", placeholder="Contoh: petani123")
                st.write("")
                submitted = st.form_submit_button("🚀 Masuk Aplikasi", use_container_width=True, type="primary")
                
                if submitted:
                    if username == "admin" and password == "petani123":
                        st.session_state['is_logged_in'] = True
                        st.rerun()
                    else:
                        st.error("Akun tidak ditemukan.")
            st.markdown('</div>', unsafe_allow_html=True)

# --- 5. DASHBOARD UTAMA (ISI APLIKASI) ---
def dashboard_page():
    # --- SIDEBAR NAVIGASI ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/628/628283.png", width=70)
        st.markdown("### AgriSmart Pro")
        
        selected_menu = option_menu(
            menu_title=None, # Judul disembunyikan biar minimalis
            options=["Beranda", "Konsultasi AI", "Ensiklopedia Tani", "Pengaturan", "Logout"],
            icons=["house-door-fill", "robot", "book-half", "gear-fill", "box-arrow-left"],
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#f8f9fa"},
                "nav-link": {"font-size": "14px", "text-align": "left", "margin":"5px"},
                "nav-link-selected": {"background-color": "#2e7d32", "font-weight":"bold"},
            }
        )

    # --- ROUTING HALAMAN ---
    
    # ================= HALAMAN 1: BERANDA (DASHBOARD) =================
    if selected_menu == "Beranda":
        # Banner Selamat Datang
        st.image(BANNER_URL, use_column_width=True)
        st.markdown('<div class="page-title">Halo, Sobat Tani! 👋</div>', unsafe_allow_html=True)
        st.write("Selamat datang di dashboard AgriSmart. Apa yang ingin Anda lakukan hari ini?")
        st.divider()

        # Kartu Menu Cepat (Quick Actions)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            st.markdown("### 🤖 Konsultasi Cepat")
            st.write("Tanya jawab langsung dengan AI mengenai masalah tanaman.")
            st.button("Mulai Konsultasi", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            st.markdown("### 📚 Cek Ensiklopedia")
            st.write("Cari informasi hama dan penyakit umum di database kami.")
            st.button("Buka Pustaka", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
             st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
             st.markdown("### ⚙️ Atur Suara AI")
             st.write("Aktifkan atau matikan fitur respon suara (Text-to-Speech).")
             st.button("Ke Pengaturan", use_container_width=True)
             st.markdown('</div>', unsafe_allow_html=True)

    # ================= HALAMAN 2: KONSULTASI AI (INTI) =================
    elif selected_menu == "Konsultasi AI":
        st.markdown('<div class="page-title">🤖 Dokter Tanaman AI</div>', unsafe_allow_html=True)
        st.caption("Upload foto daun yang sakit atau ketik pertanyaan Anda di bawah.")

        # Container Chat History agar rapi
        chat_container = st.container()
        with chat_container:
             if "history" not in st.session_state: st.session_state.history = []
             for chat in st.session_state.history:
                 with st.chat_message(chat["role"]):
                     st.markdown(chat["content"])
                     if "audio" in chat: st.audio(chat["audio"], format="audio/mp3")

        st.write("") # Spacer

        # Area Input yang Lebih Bersih (Di dalam Card)
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        col_img, col_input = st.columns([1, 3])
        
        with col_img:
            uploaded_file = st.file_uploader("📸 Upload Foto", type=["jpg","png"], label_visibility="collapsed")
            if uploaded_file:
                st.image(uploaded_file, caption="Preview", width=150)
            else:
                # Placeholder image kalau belum upload
                st.image("https://cdn-icons-png.flaticon.com/512/1635/1635678.png", width=100, caption="Belum ada foto")

        with col_input:
            st.write("⬇️ **Ketik keluhan Anda di sini:**")
            user_input = st.chat_input("Contoh: Daun padi saya menguning dan ada bercak...")

        st.markdown('</div>', unsafe_allow_html=True)

        # Logika Pemrosesan
        if user_input:
            with chat_container: # Tampilkan chat baru di container atas
                with st.chat_message("user"):
                    st.write(user_input)
                    if uploaded_file: st.image(uploaded_file, width=250)
                st.session_state.history.append({"role": "user", "content": user_input})

                with st.spinner("Sedang mendiagnosa..."):
                    try:
                        model = genai.GenerativeModel("gemini-flash-latest")
                        content = [user_input]
                        prompt_sys = "Jawablah sebagai ahli pertanian profesional secara ringkas. "
                        if uploaded_file:
                            img = PIL.Image.open(uploaded_file)
                            content.append(img)
                            prompt_sys += "Analisa gambar ini secara visual. "
                        content[0] = prompt_sys + content[0]

                        response = model.generate_content(content)
                        ai_text = response.text
                        audio_path = text_to_speech(ai_text)

                        with st.chat_message("assistant"):
                            st.markdown(ai_text)
                            if audio_path: st.audio(audio_path, format="audio/mp3")
                        
                        msg = {"role": "assistant", "content": ai_text}
                        if audio_path: msg["audio"] = audio_path
                        st.session_state.history.append(msg)
                    except Exception as e:
                        st.error(f"Error koneksi: {e}")

    # ================= HALAMAN 3: ENSIKLOPEDIA (FITUR BARU) =================
    elif selected_menu == "Ensiklopedia Tani":
        st.markdown('<div class="page-title">📚 Pustaka Hama & Penyakit</div>', unsafe_allow_html=True)
        st.write("Informasi dasar seputar masalah umum pada tanaman utama.")
        
        # Menggunakan Expander untuk tampilan minimalis
        with st.expander("🌾 Hama Wereng Coklat (Pada Padi)"):
             st.markdown("""
             **Gejala:** Tanaman menguning, kering seperti terbakar (hopperburn).
             **Penyebab:** Serangga *Nilaparvata lugens*.
             **Pengendalian:** Gunakan varietas tahan, atur jarak tanam, musuh alami (laba-laba), insektisida berbahan aktif imidakloprid (jika parah).
             """)
        
        with st.expander("🌶️ Penyakit Antraknosa/Patek (Pada Cabai)"):
             st.markdown("""
             **Gejala:** Bercak melingkar cekung pada buah, berwarna coklat/hitam.
             **Penyebab:** Jamur *Colletotrichum spp*.
             **Pengendalian:** Buang buah yang sakit, perbaiki drainase agar tidak lembab, fungisida kontak (mankozeb) atau sistemik (difenokonazol).
             """)
        
        with st.expander("🌽 Ulat Grayak (Pada Jagung)"):
             st.markdown("""
             **Gejala:** Daun berlubang-lubang tidak beraturan, terdapat kotoran ulat.
             **Penyebab:** Larva *Spodoptera frugiperda*.
             **Pengendalian:** Pengumpulan telur/ulat secara manual, pemasangan perangkap feromon, penyemprotan insektisida di pucuk tanaman.
             """)
        st.caption("Catatan: Ini adalah data statis untuk contoh. Gunakan 'Konsultasi AI' untuk diagnosa real-time.")

    # ================= HALAMAN 4: PENGATURAN (FITUR BARU) =================
    elif selected_menu == "Pengaturan":
        st.markdown('<div class="page-title">⚙️ Pengaturan Aplikasi</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.subheader("Aksesibilitas")
        # Toggle Switch untuk Suara
        tts_toggle = st.toggle("Aktifkan Respon Suara AI (Text-to-Speech)", value=st.session_state['enable_tts'])
        
        if tts_toggle:
            st.session_state['enable_tts'] = True
            st.success("✅ Fitur suara aktif. AI akan membacakan jawabannya.")
        else:
            st.session_state['enable_tts'] = False
            st.info("ℹ️ Fitur suara nonaktif. Jawaban hanya berupa teks.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ================= HALAMAN 5: LOGOUT =================
    elif selected_menu == "Logout":
        st.session_state['is_logged_in'] = False
        st.rerun()

# --- 6. MAIN CONTROL FLOW ---
if __name__ == "__main__":
    if 'is_logged_in' not in st.session_state:
        st.session_state['is_logged_in'] = False

    if st.session_state['is_logged_in']:
        dashboard_page()
    else:
        login_page()