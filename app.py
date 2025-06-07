import streamlit as st
import re
import string
import pandas as pd
from collections import Counter
import numpy as np
import requests
import json
import os

# PDF processing - try multiple libraries
try:
    import fitz  # PyMuPDF
    PDF_LIBRARY = "pymupdf"
except ImportError:
    try:
        import pdfplumber
        PDF_LIBRARY = "pdfplumber"
    except ImportError:
        try:
            from PyPDF2 import PdfReader
            PDF_LIBRARY = "pypdf2"
        except ImportError:
            PDF_LIBRARY = None
            st.error("❌ Tidak ada library PDF yang terinstall. Install salah satu: PyMuPDF, pdfplumber, atau PyPDF2")

# Konfigurasi halaman
st.set_page_config(
    page_title="AI CV Evaluator",
    page_icon="📄",
    layout="wide"
)

class OpenRouterClient:
    def __init__(self, api_key, model="anthropic/claude-3.5-sonnet"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "CV Evaluator App",
            "Content-Type": "application/json"
        }
        
        # Model pricing info (per 1M tokens)
        self.model_info = {
            "anthropic/claude-3.5-sonnet": {"name": "Claude 3.5 Sonnet", "cost": "$3", "quality": "Premium"},
            "openai/gpt-4o-mini": {"name": "GPT-4o Mini", "cost": "$0.15", "quality": "Good"},
            "google/gemini-flash-1.5": {"name": "Gemini Flash", "cost": "$0.075", "quality": "Good"},
            "meta-llama/llama-3.1-8b-instruct": {"name": "Llama 3.1 8B", "cost": "$0.055", "quality": "Budget"},
            "microsoft/wizardlm-2-8x22b": {"name": "WizardLM", "cost": "$0.50", "quality": "Good"},
            "mistralai/mixtral-8x7b-instruct": {"name": "Mixtral 8x7B", "cost": "$0.24", "quality": "Good"}
        }
    
    def analyze_cv_with_ai(self, cv_text):
        """Analisis CV menggunakan AI dari OpenRouter"""
        prompt = f"""
        Analisis CV berikut dan berikan penilaian dalam format JSON yang tepat:

        CV TEXT:
        {cv_text[:4000]}  # Batasi panjang text untuk API

        Berikan response dalam format JSON dengan struktur berikut:
        {{
            "overall_score": <nilai 0-100>,
            "section_scores": {{
                "structure": <nilai 0-25>,
                "experience": <nilai 0-25>, 
                "skills": <nilai 0-25>,
                "branding": <nilai 0-25>
            }},
            "strengths": [
                "kekuatan 1",
                "kekuatan 2"
            ],
            "weaknesses": [
                "kelemahan 1", 
                "kelemahan 2"
            ],
            "suggestions": [
                "saran 1",
                "saran 2",
                "saran 3"
            ],
            "job_roles": [
                {{
                    "role": "nama role",
                    "match_percentage": <nilai 0-100>,
                    "reason": "alasan mengapa cocok"
                }}
            ],
            "detected_skills": [
                "skill1", "skill2", "skill3"
            ]
        }}

        Kriteria penilaian:
        - Structure (25): Kelengkapan section, format, organisasi
        - Experience (25): Deskripsi kerja, pencapaian, impact
        - Skills (25): Technical skills, tools, expertise
        - Branding (25): Contact info, LinkedIn, portfolio, summary

        Berikan analisis yang mendalam dan konstruktif dalam bahasa Indonesia.
        """

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.3
        }

        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            
            # Handle specific error codes
            if response.status_code == 402:
                st.error("💳 **Payment Required**: Akun OpenRouter memerlukan top-up balance.")
                st.info("""
                **Cara mengatasi:**
                1. Kunjungi https://openrouter.ai/account
                2. Top-up balance minimal $5
                3. Atau gunakan mode analisis dasar (tanpa API key)
                """)
                return None
            elif response.status_code == 401:
                st.error("🔑 **API Key Invalid**: Periksa kembali API key Anda.")
                return None
            elif response.status_code == 429:
                st.error("⏰ **Rate Limit**: Terlalu banyak request. Coba lagi dalam beberapa menit.")
                return None
            
            response.raise_for_status()
            
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            # Parse JSON response
            try:
                # Ekstrak JSON dari response (jika ada text tambahan)
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    return json.loads(json_str)
                else:
                    return json.loads(ai_response)
            except json.JSONDecodeError:
                # Fallback jika parsing gagal
                return self._create_fallback_response(ai_response)
                
        except requests.exceptions.RequestException as e:
            if "402" in str(e):
                st.error("💳 **Insufficient Balance**: Silakan top-up akun OpenRouter Anda.")
            else:
                st.error(f"❌ **API Error**: {str(e)}")
            return None
        except Exception as e:
            st.error(f"❌ **Unexpected Error**: {str(e)}")
            return None
    
    def _create_fallback_response(self, ai_text):
        """Fallback response jika JSON parsing gagal"""
        return {
            "overall_score": 70,
            "section_scores": {
                "structure": 18,
                "experience": 17,
                "skills": 18,
                "branding": 17
            },
            "strengths": ["CV struktur cukup baik", "Informasi lengkap"],
            "weaknesses": ["Perlu lebih detail", "Format bisa diperbaiki"],
            "suggestions": [
                "Tambahkan ringkasan profil yang menarik",
                "Sertakan lebih banyak pencapaian dengan angka",
                "Update skills sesuai tren industri"
            ],
            "job_roles": [
                {"role": "General Position", "match_percentage": 70, "reason": "Profil umum yang cukup baik"}
            ],
            "detected_skills": ["Communication", "Teamwork", "Problem Solving"],
            "ai_raw_response": ai_text
        }

class CVEvaluator:
    def __init__(self, openrouter_client=None):
        self.openrouter_client = openrouter_client
        
        # Database role dan skill yang terkait (sebagai backup)
        self.role_skills = {
            "Data Analyst": [
                "python", "sql", "excel", "tableau", "power bi", "pandas", "numpy", 
                "statistics", "data visualization", "analytics", "reporting", "dashboard"
            ],
            "Data Scientist": [
                "python", "r", "machine learning", "deep learning", "tensorflow", "pytorch",
                "scikit-learn", "statistics", "pandas", "numpy", "jupyter", "sql"
            ],
            "Software Engineer": [
                "python", "java", "javascript", "react", "node.js", "git", "api", 
                "backend", "frontend", "database", "sql", "mongodb"
            ],
            "UI/UX Designer": [
                "figma", "sketch", "adobe xd", "photoshop", "illustrator", "wireframe",
                "prototype", "user research", "design thinking", "html", "css"
            ],
            "Digital Marketing": [
                "google ads", "facebook ads", "seo", "sem", "google analytics", 
                "social media", "content marketing", "email marketing", "copywriting"
            ],
            "Content Writer": [
                "writing", "copywriting", "content creation", "seo", "wordpress",
                "blog", "social media", "research", "editing", "proofreading"
            ],
            "Project Manager": [
                "agile", "scrum", "jira", "trello", "project management", "leadership",
                "communication", "planning", "stakeholder management", "risk management"
            ],
            "Business Analyst": [
                "requirements analysis", "business process", "sql", "excel", "documentation",
                "stakeholder management", "process improvement", "data analysis"
            ]
        }

    def extract_text_from_pdf(self, pdf_file):
        """Ekstrak teks dari file PDF dengan multiple library support"""
        try:
            if PDF_LIBRARY == "pymupdf":
                doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                return text
                
            elif PDF_LIBRARY == "pdfplumber":
                pdf_file.seek(0)  # Reset file pointer
                with pdfplumber.open(pdf_file) as pdf:
                    text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    return text
                    
            elif PDF_LIBRARY == "pypdf2":
                pdf_file.seek(0)  # Reset file pointer
                pdf_reader = PdfReader(pdf_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
                
            else:
                st.error("❌ Tidak ada library PDF yang tersedia")
                return ""
                
        except Exception as e:
            st.error(f"Error membaca PDF: {str(e)}")
            return ""

    def clean_text(self, text):
        """Membersihkan dan memproses teks"""
        # Konversi ke lowercase untuk processing
        text_clean = text.lower()
        # Hapus karakter khusus berlebihan tapi pertahankan struktur
        text_clean = re.sub(r'[^\w\s@.-]', ' ', text_clean)
        # Hapus spasi berlebihan
        text_clean = re.sub(r'\s+', ' ', text_clean)
        return text_clean.strip()

    def fallback_analysis(self, text):
        """Analisis fallback menggunakan rule-based system"""
        clean_text = self.clean_text(text)
        
        # Basic scoring
        structure_score = self._calculate_structure_score(clean_text)
        experience_score = self._calculate_experience_score(clean_text)
        skills_score = self._calculate_skills_score(clean_text)
        branding_score = self._calculate_branding_score(clean_text)
        
        total_score = structure_score + experience_score + skills_score + branding_score
        
        return {
            "overall_score": total_score,
            "section_scores": {
                "structure": structure_score,
                "experience": experience_score,
                "skills": skills_score,
                "branding": branding_score
            },
            "strengths": ["CV terstruktur dengan baik", "Informasi lengkap tersedia"],
            "weaknesses": ["Bisa ditingkatkan dengan AI analysis"],
            "suggestions": [
                "Gunakan OpenRouter API untuk analisis yang lebih mendalam",
                "Tambahkan lebih banyak detail pencapaian",
                "Sertakan portfolio online"
            ],
            "job_roles": self._recommend_roles_basic(clean_text),
            "detected_skills": self._extract_skills_basic(clean_text)
        }

    def _calculate_structure_score(self, text):
        """Hitung skor struktur dasar"""
        sections = ["profile", "experience", "education", "skills", "contact"]
        score = 0
        for section in sections:
            if section in text:
                score += 5
        return min(score, 25)
    
    def _calculate_experience_score(self, text):
        """Hitung skor pengalaman dasar"""
        keywords = ["tahun", "year", "experience", "worked", "managed", "developed"]
        score = sum(2 for keyword in keywords if keyword in text)
        return min(score, 25)
    
    def _calculate_skills_score(self, text):
        """Hitung skor skills dasar"""
        all_skills = set()
        for skills_list in self.role_skills.values():
            all_skills.update(skills_list)
        
        skills_count = sum(1 for skill in all_skills if skill in text)
        return min(skills_count, 25)
    
    def _calculate_branding_score(self, text):
        """Hitung skor branding dasar"""
        score = 0
        if "@" in text: score += 6
        if "linkedin" in text: score += 6
        if "github" in text: score += 6
        if "portfolio" in text: score += 7
        return min(score, 25)
    
    def _recommend_roles_basic(self, text):
        """Rekomendasi role dasar"""
        roles = []
        for role, skills in list(self.role_skills.items())[:3]:
            match_count = sum(1 for skill in skills if skill in text)
            if match_count > 0:
                percentage = min((match_count / len(skills)) * 100, 100)
                roles.append({
                    "role": role,
                    "match_percentage": round(percentage, 1),
                    "reason": f"Ditemukan {match_count} skills yang relevan"
                })
        return roles
    
    def _extract_skills_basic(self, text):
        """Ekstrak skills dasar"""
        all_skills = set()
        for skills_list in self.role_skills.values():
            all_skills.update(skills_list)
        
        found_skills = [skill for skill in all_skills if skill in text]
        return found_skills[:10]  # Return top 10

    def evaluate_cv(self, pdf_file):
        """Evaluasi CV secara keseluruhan"""
        # Ekstrak teks
        text = self.extract_text_from_pdf(pdf_file)
        if not text:
            return None
        
        # Jika ada OpenRouter client, gunakan AI analysis
        if self.openrouter_client:
            try:
                ai_results = self.openrouter_client.analyze_cv_with_ai(text)
                if ai_results:
                    return ai_results
            except Exception as e:
                st.warning(f"AI analysis gagal, menggunakan analisis dasar: {str(e)}")
        
        # Fallback ke rule-based analysis
        return self.fallback_analysis(text)

# Interface Streamlit
def main():
    st.title("🤖 AI CV Evaluator with OpenRouter")
    st.subheader("Analisis CV Otomatis dengan AI Canggih")
    
    # Sidebar untuk API Key dan Model Selection
    with st.sidebar:
        st.header("🔑 OpenRouter API Setup")
        
        # Input API Key
        api_key = st.text_input(
            "OpenRouter API Key",
            type="password",
            help="Dapatkan API key dari https://openrouter.ai"
        )
        
        # Model Selection
        model_options = {
            "openai/gpt-4o-mini": "GPT-4o Mini ($0.15/1M tokens) - Recommended",
            "google/gemini-flash-1.5": "Gemini Flash ($0.075/1M tokens) - Budget",
            "meta-llama/llama-3.1-8b-instruct": "Llama 3.1 8B ($0.055/1M tokens) - Cheapest",
            "anthropic/claude-3.5-sonnet": "Claude 3.5 Sonnet ($3/1M tokens) - Premium",
            "mistralai/mixtral-8x7b-instruct": "Mixtral 8x7B ($0.24/1M tokens) - Good",
        }
        
        selected_model = st.selectbox(
            "Pilih Model AI",
            options=list(model_options.keys()),
            format_func=lambda x: model_options[x],
            help="Model yang lebih murah cocok untuk testing"
        )
        
        if api_key:
            st.success("✅ API Key tersimpan!")
            # Tampilkan estimasi cost
            st.info(f"💰 **Model**: {model_options[selected_model]}")
        else:
            st.warning("⚠️ Tanpa API key akan menggunakan analisis dasar")
        
        st.markdown("---")
        
        st.header("💡 Tips OpenRouter")
        st.write("""
        **Untuk mulai cepat:**
        1. 🆓 Daftar di openrouter.ai
        2. 💵 Top-up minimal $1-5 
        3. 🧪 Coba model murah dulu (Gemini Flash)
        4. 🚀 Upgrade ke model premium jika perlu
        """)
        
        st.header("ℹ️ Tentang Aplikasi")
        st.write("""
        **Dengan OpenRouter AI:**
        - 🧠 Analisis mendalam
        - 📊 Penilaian akurat  
        - 💡 Saran spesifik
        - 🎯 Role matching tepat
        """)
        
        st.header("📋 Kriteria Penilaian")
        st.write("""
        - **Struktur CV (25 poin)**
        - **Pengalaman Kerja (25 poin)**
        - **Skills & Tools (25 poin)**
        - **Personal Branding (25 poin)**
        """)
    
    # Main content
    uploaded_file = st.file_uploader(
        "📄 Upload CV Anda (Format PDF)",
        type=['pdf'],
        help="Maksimal ukuran file 10MB"
    )
    
    if uploaded_file is not None:
        # Validasi ukuran file
        if uploaded_file.size > 10 * 1024 * 1024:  # 10MB
            st.error("❌ Ukuran file terlalu besar! Maksimal 10MB.")
            return
        
        with st.spinner("🔄 Menganalisis CV dengan AI..."):
            # Setup OpenRouter client jika ada API key
            openrouter_client = None
            if api_key:
                openrouter_client = OpenRouterClient(api_key, selected_model)
            
            evaluator = CVEvaluator(openrouter_client)
            results = evaluator.evaluate_cv(uploaded_file)
        
        if results:
            # Tampilkan hasil
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Skor utama
                st.markdown("## 📊 Hasil Evaluasi CV")
                
                # Score gauge
                score = results['overall_score']
                if score >= 80:
                    color = "green"
                    status = "Excellent"
                elif score >= 60:
                    color = "orange"
                    status = "Good"
                else:
                    color = "red"
                    status = "Needs Improvement"
                
                st.markdown(f"""
                <div style="text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;">
                    <h1 style="color: {color}; margin: 0;">{score}/100</h1>
                    <h3 style="color: {color}; margin: 0;">{status}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Breakdown skor
                st.markdown("### 📈 Detail Penilaian")
                breakdown_data = []
                for criteria, score_val in results['section_scores'].items():
                    breakdown_data.append({
                        'Kriteria': criteria.title(),
                        'Skor': score_val,
                        'Skor Max': 25,
                        'Persentase': round((score_val / 25) * 100, 1)
                    })
                
                breakdown_df = pd.DataFrame(breakdown_data)
                st.dataframe(breakdown_df, use_container_width=True)
                
                # Progress bars
                for row in breakdown_data:
                    percentage = row['Skor'] / 25
                    st.progress(percentage, text=f"{row['Kriteria']}: {row['Skor']}/25")
            
            with col2:
                # Kekuatan dan Kelemahan
                st.markdown("### ✅ Kekuatan")
                for strength in results.get('strengths', [])[:3]:
                    st.write(f"• {strength}")
                
                st.markdown("### ⚠️ Area Perbaikan")
                for weakness in results.get('weaknesses', [])[:3]:
                    st.write(f"• {weakness}")
            
            # Rekomendasi Role dengan AI
            st.markdown("## 🎯 Rekomendasi Role Pekerjaan")
            if results.get('job_roles'):
                for rec in results['job_roles'][:3]:
                    with st.expander(f"🔥 {rec['role']} - {rec['match_percentage']}% Match"):
                        st.write(f"**Tingkat Kesesuaian**: {rec['match_percentage']}%")
                        st.write(f"**Alasan**: {rec['reason']}")
            else:
                st.warning("Tidak ada rekomendasi role yang ditemukan.")
            
            # Skills yang Terdeteksi
            st.markdown("## 🛠️ Skills Terdeteksi")
            if results.get('detected_skills'):
                skills_text = ", ".join(results['detected_skills'][:10])
                st.info(f"**Skills**: {skills_text}")
            
            # Saran Perbaikan dari AI
            st.markdown("## 💡 Saran Perbaikan AI")
            if results.get('suggestions'):
                for i, suggestion in enumerate(results['suggestions'], 1):
                    st.write(f"**{i}.** {suggestion}")
            
            # Tips tambahan
            st.markdown("## 🚀 Tips Tambahan")
            st.info("""
            **Untuk hasil analisis terbaik:**
            - Gunakan OpenRouter API key untuk analisis AI yang mendalam
            - Pastikan CV dalam format PDF yang bersih dan terbaca
            - Sertakan informasi lengkap di semua section
            - Update CV secara berkala dengan pencapaian terbaru
            """)
            
            # Debug info jika diperlukan
            if results.get('ai_raw_response') and st.checkbox("Tampilkan Raw AI Response"):
                with st.expander("AI Raw Response"):
                    st.text(results['ai_raw_response'])
        
        else:
            st.error("❌ Gagal memproses CV. Pastikan file PDF dapat dibaca dengan baik.")

if __name__ == "__main__":
    main()