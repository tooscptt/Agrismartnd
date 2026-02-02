import streamlit as st
import google.generativeai as genai
import PIL.Image
from streamlit_option_menu import option_menu # Library menu cantik
from gtts import gTTS # Library suara
import tempfile # Untuk simpan file suara sementara

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="AgriSmart Pro",
    page_icon="🌱",
    layout="wide", # Tampilan lebar (Widescreen) agar lebih lega
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (Agar Tampilan Lebih Elegan) ---
st.markdown("""
<style>
    /* Menyembunyikan footer Streamlit default */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Mengubah font agar lebih modern */
    .stApp {
        background-color: #f5f7f9;
    }
    
    /* Style untuk chat bubble user */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #e8f5e9;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- KEAMANAN API KEY ---
try:
    if "API_KEY" in st.secrets:
        api_key = st.secrets["API_KEY"]
    else:
        api_key = "MASUKKAN_KEY_KALAU_DI_LOCALHOST" # Ganti kalau testing lokal
        if api_key == "MASUKKAN_KEY_KALAU_DI_LOCALHOST":
            st.warning("⚠️ Menggunakan mode Demo tanpa API Key")
            st.stop()
except:
    st.error("Konfigurasi Secrets belum diatur.")
    st.stop()

genai.configure(api_key=api_key)

# --- FUNGSI TEXT-TO-SPEECH (SUARA) ---
def text_to_speech(text):
    try:
        # Buat suara bahasa Indonesia ('id')
        tts = gTTS(text=text, lang='id', slow=False)
        
        # Simpan ke file sementara
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            return fp.name
    except Exception as e:
        return None

# --- MAIN APPLICATION ---
def main():
    # --- SIDEBAR MENU MODERN ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/628/628283.png", width=100) # Logo Petani dummy
        st.title("AgriSmart Pro")
        
        # Menu Navigasi dengan Icon
        selected = option_menu(
            menu_title="Menu Utama",
            options=["Konsultasi AI", "Tentang Aplikasi", "Logout"],
            icons=["chat-dots-fill", "info-circle", "box-arrow-right"],
            menu_icon="cast",
            default_index=0,
            styles={
                "nav-link-selected": {"background-color": "#2e7d32"}, # Warna Hijau Petani
            }
        )

    # --- HALAMAN 1: KONSULTASI AI ---
    if selected == "Konsultasi AI":
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### 🤖 Asisten Cerdas Pertanian")
            st.caption("Diagnosa penyakit tanaman & solusi budidaya dengan teknologi Computer Vision.")
        with col2:
            # Tombol Clear History
            if st.button("Hapus Riwayat Chat", type="primary"):
                st.session_state.history_chat = []
                st.rerun()

        # Inisialisasi History
        if "history_chat" not in st.session_state:
            st.session_state.history_chat = []

        # Tampilkan History
        for chat in st.session_state.history_chat:
            with st.chat_message(chat["role"]):
                st.markdown(chat["content"])
                # Jika ada audio di history, tampilkan player
                if "audio" in chat:
                    st.audio(chat["audio"], format="audio/mp3")

        # --- AREA INPUT ---
        with st.container():
            # Fitur Upload Foto (Dibuat lebih compact)
            uploaded_file = st.file_uploader("📸 Upload Foto Tanaman (Opsional)", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
            
            if uploaded_file:
                st.image(uploaded_file, caption="Foto Terlampir", width=200)

            # Input Text
            user_input = st.chat_input("Ketik keluhan tanaman Anda di sini...")

            if user_input:
                # 1. Tampilkan User Input
                with st.chat_message("user"):
                    st.write(user_input)
                    if uploaded_file:
                        st.image(uploaded_file, width=200)
                
                st.session_state.history_chat.append({"role": "user", "content": user_input})

                # 2. Proses AI
                model = genai.GenerativeModel("gemini-flash-latest")
                
                with st.spinner("🔄 Sedang menganalisa & membuat suara..."):
                    try:
                        final_input = [user_input]
                        system_prompt = "Kamu adalah pakar pertanian ramah. Jawab ringkas maksimal 3 paragraf. "
                        
                        if uploaded_file:
                            img = PIL.Image.open(uploaded_file)
                            final_input.append(img)
                            system_prompt += "Analisa gambar ini. "
                        
                        # Gabung prompt (trik biar nurut)
                        final_input[0] = system_prompt + final_input[0]

                        response = model.generate_content(final_input)
                        ai_reply = response.text
                        
                        # Generate Suara (Fitur Modern)
                        audio_file = text_to_speech(ai_reply)

                        # 3. Tampilkan Jawaban AI
                        with st.chat_message("assistant"):
                            st.markdown(ai_reply)
                            if audio_file:
                                st.audio(audio_file, format="audio/mp3", start_time=0)
                        
                        # Simpan ke history
                        msg_data = {"role": "assistant", "content": ai_reply}
                        if audio_file:
                            msg_data["audio"] = audio_file
                        
                        st.session_state.history_chat.append(msg_data)

                    except Exception as e:
                        st.error(f"Error: {e}")

    # --- HALAMAN 2: TENTANG ---
    if selected == "Tentang Aplikasi":
        st.title("Tentang AgriSmart")
        st.info("Aplikasi ini dibuat sebagai Tugas Akhir Teknik Informatika.")
        st.markdown("""
        **Fitur Unggulan:**
        - 🧠 **Gemini AI 2.0 Flash:** Model AI terbaru yang cepat.
        - 👁️ **Computer Vision:** Mampu mendiagnosa penyakit dari foto daun.
        - 🗣️ **Voice Feedback:** Ramah disabilitas dengan fitur suara.
        - 📱 **Responsive:** Cocok dibuka di HP maupun Laptop.
        """)
        st.balloons() # Efek animasi balon

    # --- HALAMAN 3: LOGOUT ---
    if selected == "Logout":
        st.warning("Apakah anda yakin ingin keluar?")
        if st.button("Ya, Keluar"):
            st.success("Berhasil Logout")
            st.stop()

if __name__ == "__main__":
    main()