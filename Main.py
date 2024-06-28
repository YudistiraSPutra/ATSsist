import streamlit as st
import ollama
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import time
import re
import nltk
from nltk.corpus import stopwords

# Set page configuration
st.set_page_config(layout="centered", page_title="Ekstraksi Kata Kunci dan Rekomendasi CV", page_icon="📝")

# Download stopwords
nltk.download('stopwords')
stop_words = set(stopwords.words('indonesian') + stopwords.words('english'))


# Fungsi preprocessing
def preprocessing(teks):
    # Mengubah teks menjadi huruf kecil
    teks = teks.lower()
    # Menghilangkan tanda baca dan karakter non-alfabetik
    teks = re.sub(r'[^a-zA-Z\s]', '', teks)
    # Menghilangkan spasi berlebih
    teks = re.sub(r'\s+', ' ', teks).strip()
    # Menghilangkan stopwords
    teks = ' '.join([word for word in teks.split() if word not in stop_words])
    return teks


# Fungsi ekstraksi kata kunci
def ekstrak_kata_kunci(deskripsi_pekerjaan):
    deskripsi_pekerjaan_bersih = preprocessing(deskripsi_pekerjaan)
    prompt = f"Ekstrak kata kunci maksimal 10 kata berdasarkan konteks dari teks berikut dalam bahasa Indonesia: {deskripsi_pekerjaan_bersih}"
    response = ollama.generate(model='aya', prompt=prompt)
    return response['response']


# Fungsi untuk membuat rekomendasi kalimat untuk CV
def buat_rekomendasi_cv(kata_kunci):
    prompt = f"Berdasarkan kata kunci berikut, layaknya seorang konsultan karir buatlah contoh keahlian untuk CV dalam bahasa Indonesia: {kata_kunci}"
    response = ollama.generate(model='mistral', prompt=prompt)
    return response['response']


# Fungsi untuk menampilkan animasi teks "mengolah..."
def animasi_mengolah(placeholder, duration=3):
    for _ in range(duration * 4):
        for dot in range(4):
            placeholder.text(f"Mengolah{'.' * dot}")
            time.sleep(0.25)


# Sidebar untuk navigasi
st.sidebar.markdown("<h1 style='font-size: 44px;'>ATSsist</h1>", unsafe_allow_html=True)
pilihan = st.sidebar.radio("Pilih halaman:", ["Tentang Aplikasi", "Aplikasi Utama"])

# Halaman Tentang Aplikasi
if pilihan == "Tentang Aplikasi":
    st.title("Tentang Aplikasi")
    st.write("""
        Aplikasi ini dirancang untuk membantu pencari kerja menemukan kata kunci yang relevan dari deskripsi pekerjaan. 
        Dengan menggunakan aplikasi ini, Anda dapat meningkatkan peluang Anda untuk lolos dari sistem ATS (Applicant Tracking System).

        **Cara Penggunaan:**
        1. Masukkan deskripsi pekerjaan ke dalam teks area yang disediakan.
        2. Klik tombol "Ekstrak Kata Kunci dan Buat Rekomendasi CV" untuk memulai proses.
        3. Kata kunci dan rekomendasi CV akan ditampilkan dalam tab yang berbeda.
    """)

# Halaman Aplikasi Utama
elif pilihan == "Aplikasi Utama":
    st.title("Ekstraksi Kata Kunci dan Rekomendasi CV")

    # Area teks untuk deskripsi pekerjaan
    st.subheader("Masukkan Deskripsi Pekerjaan:")
    deskripsi_pekerjaan = st.text_area("Deskripsi Pekerjaan", height=200)

    # Tampilkan kata kunci yang diekstraksi dan rekomendasi kalimat untuk CV
    if st.button("Ekstrak Kata Kunci dan Buat Rekomendasi CV"):
        if deskripsi_pekerjaan.strip() != "":
            placeholder = st.empty()

            # Mulai animasi teks "mengolah..."
            animasi_mengolah(placeholder)

            try:
                kata_kunci = ekstrak_kata_kunci(deskripsi_pekerjaan)
                rekomendasi_cv = buat_rekomendasi_cv(kata_kunci)

                # Hapus placeholder animasi
                placeholder.empty()

                st.success("Proses ekstraksi dan rekomendasi selesai!")

                tabs = st.tabs(["Kata Kunci", "Rekomendasi CV", "Visualisasi"])

                with tabs[0]:
                    st.subheader("Kata Kunci yang Diekstraksi")
                    st.text_area("Kata Kunci:", value=kata_kunci, height=200)

                with tabs[1]:
                    st.subheader("Rekomendasi Kalimat untuk CV")
                    st.text_area("Rekomendasi CV:", value=rekomendasi_cv, height=200)
                    # Tombol untuk mengunduh rekomendasi CV
                    st.download_button(
                        label="Unduh Rekomendasi CV",
                        data=rekomendasi_cv,
                        file_name="rekomendasi_cv.txt",
                        mime="text/plain",
                    )

                with tabs[2]:
                    st.subheader("Visualisasi Kata Kunci")
                    wordcloud = WordCloud(width=800, height=400).generate(kata_kunci)
                    plt.figure(figsize=(10, 5))
                    plt.imshow(wordcloud, interpolation="bilinear")
                    plt.axis("off")
                    st.pyplot(plt)
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
        else:
            st.warning("Harap masukkan deskripsi pekerjaan.")
