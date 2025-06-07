# 🤖 AI CV Evaluator with OpenRouter

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-streamlit-app-url) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Aplikasi web inovatif yang membantu Anda mengevaluasi dan meningkatkan kualitas CV Anda menggunakan kekuatan AI. Dengan memanfaatkan API OpenRouter, aplikasi ini menganalisis CV Anda secara mendalam, memberikan penilaian komprehensif, mengidentifikasi kekuatan dan kelemahan, merekomendasikan peran pekerjaan yang sesuai, serta menawarkan saran perbaikan yang spesifik.

Jika Anda tidak memiliki API Key OpenRouter, aplikasi ini juga menyediakan analisis dasar berbasis aturan.

---

## ✨ Fitur Utama

* **Analisis CV Berbasis AI (via OpenRouter):** Dapatkan penilaian mendalam pada struktur, pengalaman, keahlian, dan personal branding CV Anda.
* **Penilaian Komprehensif:** Skor keseluruhan CV (0-100) beserta skor detail untuk setiap bagian kunci.
* **Identifikasi Kekuatan & Kelemahan:** Pahami apa yang sudah baik di CV Anda dan area mana yang perlu ditingkatkan.
* **Rekomendasi Peran Pekerjaan:** Temukan posisi yang paling cocok dengan profil Anda berdasarkan analisis AI.
* **Deteksi Keterampilan Otomatis:** Melihat daftar keterampilan yang terdeteksi dari CV Anda.
* **Saran Perbaikan Spesifik:** Dapatkan rekomendasi yang dapat ditindaklanjuti untuk mengoptimalkan CV Anda.
* **Dukungan Multi-PDF Library:** Mampu mengekstrak teks dari PDF menggunakan PyMuPDF, pdfplumber, atau PyPDF2.
* **Analisis Fallback:** Jika API Key tidak tersedia atau ada masalah, aplikasi akan melakukan analisis dasar berbasis aturan.
* **Pilihan Model AI:** Fleksibilitas untuk memilih berbagai model AI dari OpenRouter (misal: GPT-4o Mini, Gemini Flash, Claude 3.5 Sonnet) sesuai kebutuhan dan budget Anda.

---

## 🚀 Instalasi & Penggunaan

Ikuti langkah-langkah di bawah ini untuk menjalankan aplikasi secara lokal.

### Prasyarat

* Python 3.8+
* `pip` (manajer paket Python)

### Langkah-langkah Instalasi

1.  **Clone repositori:**
    ```bash
    git clone https://github.com/raratdit/ai-cv-evaluator.git
    cd ai-cv-evaluator
    ```

2.  **Buat virtual environment (direkomendasikan):**
    ```bash
    python -m venv venv
    source venv/bin/activate # Di macOS/Linux
    # venv\Scripts\activate   # Di Windows
    ```

3.  **Instal dependensi:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Anda perlu membuat file `requirements.txt` terlebih dahulu. Lihat bagian di bawah.)*

### Membuat `requirements.txt`

Pastikan file `requirements.txt` Anda berisi dependensi yang digunakan dalam kode:

```
streamlit
requests
pandas
numpy
PyMuPDF # atau fitz
pdfplumber
PyPDF2
```

*Catatan: Anda dapat memilih untuk menginstal salah satu atau semua library PDF (`PyMuPDF`, `pdfplumber`, `PyPDF2`). Aplikasi akan mencoba yang tersedia secara berurutan.*

### Menjalankan Aplikasi

1.  **Dapatkan OpenRouter API Key (Opsional tapi Direkomendasikan):**
    * Kunjungi [https://openrouter.ai](https://openrouter.ai) dan daftar.
    * Dapatkan API Key Anda dari halaman akun.

2.  **Jalankan aplikasi Streamlit:**
    ```bash
    streamlit run app.py # Asumsikan nama file Anda adalah app.py
    ```
    Aplikasi akan terbuka di browser default Anda (biasanya `http://localhost:8501`).

---

## ⚙️ Konfigurasi (Sidebar)

Di sidebar aplikasi, Anda akan menemukan opsi konfigurasi:

* **OpenRouter API Key:** Masukkan API Key Anda di sini. Tanpa API Key, aplikasi akan beralih ke analisis dasar.
* **Pilih Model AI:** Pilih model AI yang ingin Anda gunakan dari OpenRouter. Model yang lebih murah cocok untuk pengujian, sementara model premium menawarkan analisis yang lebih akurat.

---

## 📄 Struktur Kode

* `app.py`: File utama aplikasi Streamlit yang berisi UI dan logika evaluasi CV.
* `OpenRouterClient` Class: Menangani interaksi dengan OpenRouter API untuk analisis AI.
* `CVEvaluator` Class: Mengelola ekstraksi teks PDF, pembersihan teks, dan logika evaluasi (baik AI maupun fallback).

---

## 🤝 Kontribusi

Kami menerima kontribusi! Jika Anda memiliki saran atau ingin meningkatkan aplikasi ini, silakan:

1.  Fork repositori ini.
2.  Buat branch baru (`git checkout -b feature/nama-fitur`).
3.  Lakukan perubahan Anda.
4.  Commit perubahan Anda (`git commit -m 'Tambahkan fitur baru'`).
5.  Push ke branch Anda (`git push origin feature/nama-fitur`).
6.  Buka Pull Request.

---

## 📜 Lisensi

Proyek ini dilisensikan di bawah Lisensi MIT. Lihat file [LICENSE](LICENSE) untuk detail lebih lanjut.

---

## 📧 Kontak

Jika Anda memiliki pertanyaan atau masalah, silakan buka *issue* di repositori ini.