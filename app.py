import streamlit as st
import pandas as pd
import json
import secrets
import string
import requests
from datetime import datetime
from io import BytesIO


st.set_page_config(
    page_title="IT Smart Character Interview",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CONFIGURATION
# ============================================================
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
# Prefer the server-side service-role key. Keep it only in Streamlit Secrets.
# The fallback supports the anon key for environments with explicit RLS policies.
SUPABASE_KEY = st.secrets.get(
    "SUPABASE_SERVICE_ROLE_KEY",
    st.secrets.get("SUPABASE_KEY", "")
)
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")
OPENAI_MODEL = st.secrets.get("OPENAI_MODEL", "gpt-5-mini")

PUBLIC_MODE = st.query_params.get("view", "interviewer").lower()
SESSION_CODE_FROM_URL = st.query_params.get("session", "")

st.markdown("""
<style>
.block-container {max-width:1250px;padding-top:1.5rem}
.question-card {background:#ffffff;border:1px solid #dbe2ea;border-radius:18px;padding:34px;margin:18px 0}
.question-text {font-size:32px;font-weight:750;line-height:1.35;text-align:center;color:#0f172a}
.option {background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:20px;font-size:21px;line-height:1.45;margin:12px 0}
.private-note {background:#fff7ed;border:1px solid #fed7aa;border-radius:12px;padding:16px}
.public-banner {background:#ecfdf5;border:1px solid #a7f3d0;border-radius:12px;padding:12px;text-align:center}
.private-banner {background:#fff7ed;border:1px solid #fed7aa;border-radius:12px;padding:12px}
.small-muted {color:#64748b;font-size:14px}
</style>
""", unsafe_allow_html=True)

RAW_QUESTIONS = [
(1,"Logical Thinking","Saat menghadapi masalah baru, kamu lebih memilih...","Langsung mencoba beberapa solusi untuk melihat hasilnya.","Mengumpulkan informasi dan memahami penyebab sebelum bertindak.","action_first","structured_analysis","Apakah kamu tetap melakukan root-cause analysis setelah tindakan awal?"),
(2,"Logical Thinking","Jika terjadi gangguan sistem, kamu cenderung...","Fokus pada penyebab yang paling mungkin terjadi.","Memeriksa beberapa kemungkinan penyebab secara sistematis.","hypothesis_focus","systematic_diagnosis","Bagaimana kamu memastikan penyebab yang paling mungkin bukan asumsi yang keliru?"),
(3,"Logical Thinking","Ketika masalah muncul setelah perubahan sistem, kamu akan...","Memeriksa perubahan terakhir yang dilakukan.","Melakukan pemeriksaan dasar secara menyeluruh.","change_correlation","baseline_check","Bagaimana kamu menghindari kesimpulan terlalu cepat bahwa perubahan terakhir adalah penyebabnya?"),
(4,"Logical Thinking","Ketika solusi pertama belum berhasil, kamu lebih memilih...","Memodifikasi solusi tersebut sampai berhasil.","Meninjau kembali asumsi dan mencoba hipotesis lain.","iterative_action","assumption_review","Kapan kamu memutuskan berhenti memodifikasi solusi dan mengganti pendekatan?"),
(5,"Learning Agility","Saat mempelajari tools baru, kamu cenderung...","Mengeksplorasi dan mencari tahu secara mandiri.","Membaca dokumentasi atau bertanya kepada orang berpengalaman.","self_exploration","guided_learning","Bagaimana kamu tahu kapan harus belajar sendiri dan kapan meminta bantuan?"),
(6,"Learning Agility","Saat mempelajari sebuah sistem, hal yang paling ingin kamu pahami adalah...","Cara sistem tersebut bekerja di balik layar.","Cara menggunakan sistem untuk menyelesaikan pekerjaan.","technical_depth","task_application","Bagaimana kamu menghubungkan pemahaman teknis dengan kebutuhan user?"),
(7,"Learning Agility","Jika ada metode baru untuk menyelesaikan pekerjaan, kamu akan...","Menggunakan metode lama yang sudah terbukti.","Mempelajari metode baru untuk melihat apakah lebih efektif.","proven_method","experimentation","Bagaimana kamu menguji metode baru tanpa mengganggu operasional?"),
(8,"Learning Agility","Ketika muncul pertanyaan saat bekerja, kamu lebih memilih...","Mencatatnya dan mempelajarinya nanti.","Langsung bertanya agar bisa memahami saat itu juga.","self_research","immediate_clarification","Bagaimana kamu menghindari ketergantungan pada orang lain ketika sering bertanya?"),
(9,"Problem Solving","Saat prosedur standar tidak menyelesaikan masalah, kamu akan...","Mencari alternatif di luar prosedur standar.","Memeriksa prosedur standar secara lebih mendalam.","creative_alternative","process_review","Bagaimana kamu memastikan alternatif yang dipilih tetap aman dan terdokumentasi?"),
(10,"Problem Solving","Untuk kebutuhan sistem baru, kamu lebih tertarik pada...","Solusi open-source yang bisa disesuaikan.","Solusi komersial yang matang dan memiliki dukungan vendor.","customization","vendor_support","Faktor apa yang kamu gunakan untuk membandingkan risiko dan biaya kedua pilihan?"),
(11,"Problem Solving","Jika menemukan pekerjaan berulang, kamu akan...","Mencari cara untuk mengotomatisasi pekerjaan tersebut.","Membuat prosedur manual yang lebih terstandarisasi.","automation","standardization","Bagaimana kamu menilai apakah otomasi memang layak dilakukan?"),
(12,"Decision Making","Guest Wi-Fi mengalami gangguan besar. Kamu akan...","Segera melakukan tindakan untuk memulihkan layanan.","Memahami dampak dan melakukan pemeriksaan singkat terlebih dahulu.","rapid_restoration","impact_assessment","Apa tindakanmu jika informasi belum lengkap tetapi guest impact sangat tinggi?"),
(13,"Decision Making","Ketika diminta memberikan solusi dengan cepat, kamu akan...","Memberikan solusi sementara berdasarkan informasi yang tersedia.","Mengumpulkan informasi penting terlebih dahulu.","provisional_action","information_gathering","Bagaimana kamu mengomunikasikan risiko dari solusi sementara?"),
(14,"Decision Making","Jika pekerjaan belum selesai menjelang akhir jam kerja, kamu akan...","Tetap melanjutkan pekerjaan sampai selesai.","Mendokumentasikan status, mengomunikasikan kondisi, dan membuat rencana lanjutan.","persistence","handover_planning","Dalam kondisi apa kamu memilih melanjutkan pekerjaan di luar jam kerja?"),
(15,"Practical Judgment","Ketika hasil pekerjaan sudah memenuhi requirement, kamu akan...","Menyelesaikannya dan melanjutkan pekerjaan berikutnya.","Melakukan penyempurnaan lebih lanjut agar hasilnya lebih sempurna.","delivery_focus","quality_refinement","Bagaimana kamu menentukan batas antara cukup baik dan over-engineering?"),
(16,"Practical Judgment","Jika menemukan kesalahan kecil pada data, kamu akan...","Memperbaiki kesalahan tersebut dan melanjutkan pekerjaan.","Mencari tahu apakah ada masalah yang lebih luas pada sumber data.","local_fix","systemic_investigation","Bagaimana kamu menyeimbangkan kebutuhan memperbaiki laporan dengan waktu yang tersedia?"),
(17,"Initiative","Jika menemukan cara untuk meningkatkan efisiensi pekerjaan, kamu akan...","Mengusulkan perbaikan meskipun tidak diminta.","Memahami alasan di balik proses yang berjalan terlebih dahulu.","proactive_change","context_first","Bagaimana kamu memperoleh dukungan sebelum mengubah proses yang digunakan tim?"),
(18,"Initiative","Setelah menyelesaikan pekerjaan rutin lebih cepat, kamu akan...","Menggunakan waktu yang tersisa untuk pekerjaan lain.","Mencari cara agar pekerjaan rutin tersebut bisa lebih efisien.","task_completion","efficiency_improvement","Ceritakan perbaikan proses yang pernah kamu lakukan tanpa diminta."),
(19,"Collaboration","Ketika solusi kamu berbeda dengan rekan kerja, kamu akan...","Menjelaskan mengapa solusi kamu lebih baik.","Menanyakan alasan dan pertimbangan di balik solusi rekan kerja.","advocacy","active_listening","Bagaimana kamu mengambil keputusan ketika kedua pendekatan sama-sama memiliki alasan kuat?"),
(20,"Learning Orientation","Jika memiliki waktu untuk belajar, kamu cenderung memilih...","Topik yang langsung berguna untuk pekerjaan.","Topik menarik yang belum tentu langsung memiliki kegunaan.","job_relevance","broad_curiosity","Bagaimana kamu mengubah pengetahuan yang menarik menjadi manfaat praktis?")
]

QUESTIONS = [
    {"id": r[0], "category": r[1], "question": r[2], "a": r[3], "b": r[4],
     "signal_a": r[5], "signal_b": r[6], "followup": r[7]}
    for r in RAW_QUESTIONS
]

# ============================================================
# AUTOMATIC ANALYSIS HELPERS
# ============================================================
SIGNAL_TEXT = {
    "action_first": ("memulai dari tindakan awal untuk mendapatkan respons", "respons cepat", "validasi risiko dan diagnosis"),
    "structured_analysis": ("mengumpulkan informasi dan memahami penyebab sebelum bertindak", "perhatian pada akar masalah", "jangan sampai analisis memperlambat respons"),
    "hypothesis_focus": ("memulai dari penyebab yang paling mungkin", "membuat hipotesis awal", "uji hipotesis dengan bukti"),
    "systematic_diagnosis": ("memeriksa beberapa kemungkinan secara sistematis", "mengurangi risiko melewatkan penyebab", "tetapkan prioritas pemeriksaan"),
    "change_correlation": ("menghubungkan gangguan dengan perubahan terakhir", "peka terhadap korelasi perubahan dan insiden", "konfirmasi korelasi melalui log atau pengujian"),
    "baseline_check": ("memeriksa kondisi dasar secara menyeluruh", "memperhatikan baseline", "jangan abaikan indikasi perubahan yang relevan"),
    "iterative_action": ("memodifikasi solusi secara bertahap", "bersedia melakukan iterasi", "tetapkan batas percobaan dan kriteria eskalasi"),
    "assumption_review": ("meninjau asumsi dan mencoba hipotesis lain", "terbuka mengevaluasi ulang pendekatan", "pastikan perubahan pendekatan berdasarkan data"),
    "self_exploration": ("mengeksplorasi tools baru secara mandiri", "inisiatif belajar mandiri", "lengkapi dengan dokumentasi dan validasi"),
    "guided_learning": ("memanfaatkan dokumentasi atau pengalaman orang lain", "memakai sumber belajar terarah", "pastikan pengetahuan juga dapat diterapkan mandiri"),
    "technical_depth": ("memahami cara kerja sistem di balik layar", "ketertarikan pada kedalaman teknis", "hubungkan teknis dengan kebutuhan user dan bisnis"),
    "task_application": ("memahami cara menggunakan sistem untuk menyelesaikan pekerjaan", "orientasi penerapan praktis", "pastikan risiko dan konteks tetap dipahami"),
    "proven_method": ("mempertahankan metode yang sudah terbukti", "memperhatikan stabilitas", "evaluasi peluang improvement"),
    "experimentation": ("menguji metode baru untuk melihat efektivitasnya", "terbuka terhadap eksperimen", "gunakan pengujian terkontrol"),
    "self_research": ("mencari dan mempelajari jawaban secara mandiri", "kecenderungan mencari informasi sendiri", "tentukan kapan perlu eskalasi"),
    "immediate_clarification": ("meminta klarifikasi secara langsung", "mengurangi ketidakjelasan lebih awal", "seimbangkan bertanya dengan riset mandiri"),
    "creative_alternative": ("mencari alternatif di luar prosedur standar", "terbuka pada pendekatan alternatif", "pastikan persetujuan, kontrol risiko, dan dokumentasi"),
    "process_review": ("meninjau prosedur standar secara lebih mendalam", "memperhatikan proses dan kontrol", "kenali kapan prosedur perlu diperbaiki"),
    "customization": ("mempertimbangkan solusi open-source yang dapat disesuaikan", "memperhatikan fleksibilitas", "evaluasi keamanan, biaya, kompetensi, dan dukungan"),
    "vendor_support": ("mempertimbangkan solusi komersial dengan dukungan vendor", "memperhatikan kematangan dan dukungan", "bandingkan biaya, ketergantungan, dan fleksibilitas"),
    "automation": ("mencari peluang otomasi pada pekerjaan berulang", "peka terhadap efisiensi", "pastikan monitoring dan fallback tersedia"),
    "standardization": ("menstandarkan prosedur manual", "memperhatikan konsistensi", "evaluasi apakah otomasi lebih sesuai"),
    "rapid_restoration": ("memprioritaskan pemulihan layanan secara cepat", "memperhatikan dampak operasional", "tetap lakukan pengamanan dan dokumentasi"),
    "impact_assessment": ("memahami dampak sebelum melakukan tindakan", "mempertimbangkan konsekuensi", "tetapkan batas waktu analisis"),
    "provisional_action": ("memberikan solusi sementara berdasarkan informasi tersedia", "mampu bertindak di tengah informasi terbatas", "komunikasikan risiko dan rencana permanen"),
    "information_gathering": ("mengumpulkan informasi penting terlebih dahulu", "membuat keputusan berbasis informasi", "bedakan informasi wajib dan tambahan"),
    "persistence": ("melanjutkan pekerjaan sampai selesai", "dorongan menyelesaikan tanggung jawab", "pertimbangkan kelelahan, eskalasi, dan handover"),
    "handover_planning": ("mendokumentasikan status dan menyiapkan rencana lanjutan", "memperhatikan kesinambungan", "pastikan isu kritis tetap dieskalasikan"),
    "delivery_focus": ("menyelesaikan pekerjaan ketika requirement terpenuhi", "orientasi penyelesaian", "tetap periksa kualitas dan risiko"),
    "quality_refinement": ("melakukan penyempurnaan lebih lanjut", "memperhatikan kualitas dan detail", "tetapkan batas agar tidak over-engineering"),
    "local_fix": ("memperbaiki kesalahan lokal dan melanjutkan pekerjaan", "menjaga progres", "pastikan masalah sistemik tidak terlewat"),
    "systemic_investigation": ("memeriksa kemungkinan masalah yang lebih luas", "memperhatikan risiko sistemik", "prioritaskan investigasi berdasarkan dampak"),
    "proactive_change": ("mengusulkan perbaikan meskipun tidak diminta", "kecenderungan proaktif", "libatkan konteks dan stakeholder"),
    "context_first": ("memahami alasan dan konteks proses sebelum mengubahnya", "memperhatikan dampak perubahan", "jangan sampai konteks menghambat improvement"),
    "task_completion": ("menggunakan waktu tersisa untuk pekerjaan lain", "memperhatikan penyelesaian pekerjaan", "tetap identifikasi peluang efisiensi"),
    "efficiency_improvement": ("mencari cara agar pekerjaan rutin lebih efisien", "memperhatikan continuous improvement", "uji improvement berdasarkan dampak"),
    "advocacy": ("menjelaskan alasan mengapa solusi sendiri lebih baik", "mampu menyampaikan argumen", "tetap terbuka pada masukan dan bukti"),
    "active_listening": ("menanyakan alasan dan pertimbangan rekan kerja", "mendengarkan perspektif", "arahkan diskusi menuju keputusan jelas"),
    "job_relevance": ("memilih topik belajar yang langsung relevan dengan pekerjaan", "orientasi penerapan praktis", "tetap beri ruang untuk wawasan baru"),
    "broad_curiosity": ("mengeksplorasi topik baru meskipun manfaatnya belum langsung terlihat", "rasa ingin tahu luas", "hubungkan pembelajaran dengan eksperimen praktis"),
}

def signal_info(signal):
    return SIGNAL_TEXT.get(signal, (signal.replace('_', ' '), 'preferensi pendekatan tertentu', 'validasi melalui contoh nyata'))

def rich_interpretation(q, answer):
    if answer not in ('A', 'B'):
        return 'Belum ada pilihan A/B yang dicatat.'
    signal = q['signal_a'] if answer == 'A' else q['signal_b']
    label, strength, watchout = signal_info(signal)
    return (f"Kandidat memilih pendekatan yang {label}. "
            f"Potensi kekuatan yang perlu digali: {strength}. "
            f"Hal yang perlu divalidasi: {watchout}.")

def category_analysis(session, category):
    answers = session.get('answers') or {}
    notes = session.get('notes') or {}
    labels, strengths, watchouts = [], [], []
    answered, noted = 0, 0
    for q in QUESTIONS:
        if q['category'] != category:
            continue
        answer = answers.get(str(q['id']))
        if answer not in ('A', 'B'):
            continue
        answered += 1
        signal = q['signal_a'] if answer == 'A' else q['signal_b']
        label, strength, watchout = signal_info(signal)
        labels.append(label); strengths.append(strength); watchouts.append(watchout)
        if str(notes.get(str(q['id']), '')).strip():
            noted += 1
    unique = lambda xs: list(dict.fromkeys(xs))
    return {
        'answered': answered,
        'noted': noted,
        'pattern': '; '.join(unique(labels)) if labels else 'Belum ada jawaban yang tercatat.',
        'strengths': unique(strengths),
        'watchouts': unique(watchouts),
    }

def automatic_conclusion(session):
    answers = session.get('answers') or {}
    completed = sum(1 for value in answers.values() if value in ('A', 'B'))
    if not completed:
        return 'Belum ada jawaban yang cukup untuk membuat ringkasan otomatis.'
    parts = []
    for category in dict.fromkeys(q['category'] for q in QUESTIONS):
        data = category_analysis(session, category)
        if data['answered']:
            parts.append(f"{category}: {data['pattern']}. Validasi: {'; '.join(data['watchouts'][:2])}.")
    return (f"Ringkasan indikasi awal dari {completed} jawaban. "
            "Pola ini harus dibaca bersama jawaban verbal dan catatan interviewer. "
            + ' '.join(parts) + " Ini bukan skor otomatis atau keputusan hiring.")

def build_ai_prompt(session):
    answers = session.get("answers") or {}
    notes = session.get("notes") or {}
    rows = []
    for q in QUESTIONS:
        answer = answers.get(str(q["id"]), "")
        if answer not in ("A", "B"):
            continue
        chosen = q["a"] if answer == "A" else q["b"]
        rows.append({
            "question_id": q["id"],
            "category": q["category"],
            "question": q["question"],
            "selected_option": answer,
            "selected_text": chosen,
            "interviewer_note": notes.get(str(q["id"]), ""),
        })
    return {
        "candidate_name": session.get("candidate_name", ""),
        "position": session.get("position", ""),
        "interview_date": session.get("interview_date", ""),
        "responses": rows,
    }


def generate_ai_assessment(session):
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY belum dikonfigurasi di Streamlit Secrets.")

    system_prompt = (
        "You are an HR interview assessment assistant for an IT hotel operations role. "
        "Write the assessment in clear professional Indonesian. Treat A/B choices as "
        "behavioral preferences, not as automatic good/bad scores. Do not invent evidence. "
        "Separate observed evidence from hypotheses and validation needs. Do not make a "
        "final hiring decision. Return Markdown with these headings: Executive Summary, "
        "Competency Review, Potential Strengths to Validate, Areas Requiring Validation, "
        "Suggested Follow-up Questions, and Interviewer Decision Support."
    )
    user_prompt = (
        "Analyze the following interview data. Mention when interviewer notes are absent "
        "or insufficient. Use balanced, evidence-based language.\\n\\n"
        + json.dumps(build_ai_prompt(session), ensure_ascii=False, indent=2)
    )
    response = requests.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": OPENAI_MODEL,
            "input": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        },
        timeout=90,
    )
    if not response.ok:
        raise RuntimeError(
            f"OpenAI request failed ({response.status_code}): "
            f"{response.text[:500]}"
        )
    data = response.json()
    output_text = data.get("output_text", "")
    if not output_text:
        for item in data.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    output_text += content.get("text", "")
    if not output_text.strip():
        raise RuntimeError("OpenAI tidak mengembalikan teks analisis.")
    return output_text.strip()


# ============================================================
# PDF EXPORT
# ============================================================
def build_pdf_export(session, questions_rows, ai_assessment, conclusion):
    """Create an interviewer-only PDF report in memory."""
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from xml.sax.saxutils import escape

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title=f"Interview Report - {session.get('candidate_name', '')}",
        author="IT Smart Character Interview",
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle", parent=styles["Title"], alignment=TA_CENTER,
        fontSize=18, leading=22, spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name="Small", parent=styles["BodyText"], fontSize=8.5, leading=11,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="Section", parent=styles["Heading2"], fontSize=13, leading=16,
        spaceBefore=10, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="Question", parent=styles["BodyText"], fontSize=8.5, leading=11,
        spaceAfter=5,
    ))
    styles.add(ParagraphStyle(
        name="AI", parent=styles["BodyText"], fontSize=9, leading=12,
        spaceAfter=5,
    ))

    story = []
    story.append(Paragraph("IT Smart Character Interview Report", styles["ReportTitle"]))
    info = [
        ["Candidate", escape(str(session.get("candidate_name", "")))],
        ["Position", escape(str(session.get("position", "")))],
        ["Interview Date", escape(str(session.get("interview_date", "")))],
        ["Session Code", escape(str(session.get("session_code", "")))],
        ["Status", escape(str(session.get("status", "")))],
    ]
    info_table = Table(info, colWidths=[38 * mm, 135 * mm])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF0F6")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B8C4D1")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.extend([info_table, Spacer(1, 10)])

    story.append(Paragraph("AI Full Assessment", styles["Section"]))
    if ai_assessment:
        # Convert common Markdown patterns into readable PDF paragraphs.
        for raw_line in str(ai_assessment).splitlines():
            line = raw_line.strip()
            if not line:
                story.append(Spacer(1, 4))
                continue
            if line.startswith("### "):
                story.append(Paragraph(escape(line[4:]), styles["Section"]))
            elif line.startswith("## "):
                story.append(Paragraph(escape(line[3:]), styles["Section"]))
            elif line.startswith("# "):
                story.append(Paragraph(escape(line[2:]), styles["Section"]))
            elif line.startswith("- ") or line.startswith("* "):
                story.append(Paragraph("• " + escape(line[2:]), styles["AI"]))
            else:
                story.append(Paragraph(escape(line), styles["AI"]))
    else:
        story.append(Paragraph("AI assessment belum dibuat.", styles["Small"]))

    story.append(Paragraph("Automatic Interview Conclusion", styles["Section"]))
    story.append(Paragraph(escape(str(automatic_conclusion(session))), styles["AI"]))

    story.append(Paragraph("Interviewer Final Notes", styles["Section"]))
    story.append(Paragraph(escape(str(conclusion or "Belum ada catatan final.")), styles["AI"]))

    story.append(PageBreak())
    story.append(Paragraph("Question-by-Question Record", styles["Section"]))
    for row in questions_rows:
        question_header = f"{row['Question']}. {row['Category']}"
        story.append(Paragraph(escape(question_header), styles["Section"]))
        details = [
            ["Question", row["Question Text"]],
            ["Selected Answer", row["Selected Answer"] or "Not answered"],
            ["Option A", row["Option A"]],
            ["Option B", row["Option B"]],
            ["Behavioral Interpretation", row["Behavioral Interpretation"]],
            ["Interviewer Note", row["Interviewer Note"] or "-"],
            ["Follow-up", row["Follow-up"]],
        ]
        safe_details = [[escape(str(k)), escape(str(v))] for k, v in details]
        q_table = Table(safe_details, colWidths=[39 * mm, 134 * mm], repeatRows=0)
        q_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F4F6F8")),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C7D0D9")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("LEADING", (0, 0), (-1, -1), 10),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.extend([q_table, Spacer(1, 8)])

    doc.build(story)
    return buffer.getvalue()


# ============================================================
# SUPABASE HELPERS
# Required tables are provided in supabase_schema.sql.
# ============================================================
def configured():
    return bool(SUPABASE_URL and SUPABASE_KEY)

def headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }

def db_request(method, table, params=None, payload=None):
    if not configured():
        return None
    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/{table}"
    response = requests.request(
        method, url, headers=headers(), params=params, json=payload, timeout=15
    )
    if not response.ok:
        # Show a useful but controlled error to the interviewer.
        # Do not print the Supabase key or authorization headers.
        detail = response.text[:500] if response.text else "No response body"
        raise RuntimeError(
            f"Supabase request failed ({response.status_code}) "
            f"for {method} {table}: {detail}"
        )
    if response.text:
        return response.json()
    return []

def generate_code(length=6):
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

def create_session(name, position, interview_date):
    session_id = secrets.token_urlsafe(18)
    presenter_token = secrets.token_urlsafe(24)
    interviewer_token = secrets.token_urlsafe(24)
    code = generate_code()
    payload = {
        "id": session_id,
        "session_code": code,
        "candidate_name": name,
        "position": position,
        "interview_date": str(interview_date),
        "current_index": 0,
        "status": "active",
        "presenter_token": presenter_token,
        "interviewer_token": interviewer_token,
        "answers": {},
        "notes": {},
        "assessments": {},
        "overall_conclusion": "",
        "updated_at": datetime.utcnow().isoformat(),
    }
    result = db_request("POST", "interview_sessions", payload=payload)
    return payload if result is not None else None

def load_session(code, token=None, role=None):
    params = {"session_code": f"eq.{code}", "select": "*"}
    rows = db_request("GET", "interview_sessions", params=params)
    if not rows:
        return None
    session = rows[0]
    if role == "presenter" and token and token != session.get("presenter_token"):
        return None
    if role == "interviewer" and token and token != session.get("interviewer_token"):
        return None
    return session

def update_session(session_id, changes):
    changes = dict(changes)
    changes["updated_at"] = datetime.utcnow().isoformat()
    params = {"id": f"eq.{session_id}"}
    result = db_request("PATCH", "interview_sessions", params=params, payload=changes)
    return result is not None

def live_interpretation(q, answer):
    return rich_interpretation(q, answer)

def category_summary(session):
    answers = session.get("answers") or {}
    result = {}
    for q in QUESTIONS:
        category = q["category"]
        result.setdefault(category, {"answered": 0, "a": 0, "b": 0})
        answer = answers.get(str(q["id"]))
        if answer in ("A", "B"):
            result[category]["answered"] += 1
            result[category][answer.lower()] += 1
    return result

def session_url(view, code, token):
    base = "https://speedqui.streamlit.app"
    return f"{base}/?view={view}&session={code}&token={token}"

# ============================================================
# SETUP / AUTHENTICATION
# ============================================================
token_from_url = st.query_params.get("token", "")

if not configured():
    st.error("Supabase belum dikonfigurasi. Tambahkan URL dan server-side key di Streamlit Secrets.")
    st.code(
        'SUPABASE_URL = "https://your-project.supabase.co"\n'
        'SUPABASE_SERVICE_ROLE_KEY = "your-service-role-key"'
    )
    st.stop()

if PUBLIC_MODE == "presenter":
    st.markdown('<div class="public-banner">🟢 PRESENTER VIEW — Hanya pertanyaan untuk kandidat</div>', unsafe_allow_html=True)
    if not SESSION_CODE_FROM_URL or not token_from_url:
        st.warning("Presenter URL belum lengkap. Gunakan URL yang dibuat dari Interviewer View.")
        st.stop()
    session = load_session(SESSION_CODE_FROM_URL, token_from_url, "presenter")
    if not session:
        st.error("Session tidak ditemukan atau presenter token tidak valid.")
        st.stop()
else:
    st.markdown('<div class="private-banner">🔒 INTERVIEWER VIEW — Informasi internal dan analisis privat</div>', unsafe_allow_html=True)
    session = None
    if SESSION_CODE_FROM_URL and token_from_url:
        session = load_session(SESSION_CODE_FROM_URL, token_from_url, "interviewer")

# ============================================================
# PRESENTER VIEW
# ============================================================
if PUBLIC_MODE == "presenter":
    index = int(session.get("current_index", 0))
    q = QUESTIONS[index]
    answers = session.get("answers") or {}
    answered = len(answers)

    st.title("🧠 IT Smart Character Interview")
    st.progress(answered / len(QUESTIONS))
    st.caption(f"Question {index + 1} of {len(QUESTIONS)}")

    st.markdown('<div class="question-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="question-text">{q["question"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="option"><b>A.</b> {q["a"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="option"><b>B.</b> {q["b"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.caption("Silakan pilih jawaban berdasarkan pertanyaan interviewer.")
    if st.button("🔄 Refresh Question", use_container_width=True):
        st.rerun()
    st.stop()

# ============================================================
# INTERVIEWER VIEW — SETUP
# ============================================================
if not session:
    st.title("🧠 IT Smart Character Interview")
    st.write("Buat sesi interview untuk mendapatkan Presenter URL dan Interviewer URL.")
    with st.form("create_session_form"):
        candidate_name = st.text_input("Nama Kandidat")
        position = st.selectbox(
            "Posisi",
            ["IT Executive", "IT Supervisor", "Assistant IT Manager", "IT Manager", "Other"]
        )
        interview_date = st.date_input("Tanggal Interview", value=datetime.now().date())
        submitted = st.form_submit_button("Create Interview Session", type="primary", use_container_width=True)

    if submitted:
        if not candidate_name.strip():
            st.error("Nama kandidat wajib diisi.")
        else:
            session = create_session(candidate_name.strip(), position, interview_date)
            if session:
                st.query_params.update(
                    view="interviewer",
                    session=session["session_code"],
                    token=session["interviewer_token"]
                )
                st.rerun()
            else:
                st.error("Session gagal dibuat.")
    st.stop()

# ============================================================
# INTERVIEWER VIEW — MAIN
# ============================================================
st.title("📋 Interviewer Dashboard")
st.caption("App version: AUTO-CONCLUSION-V2 | If this label is not visible after deployment, Streamlit is still running an older commit.")
st.write(f"**Candidate:** {session['candidate_name']}  |  **Position:** {session['position']}  |  **Date:** {session['interview_date']}")

with st.expander("🔗 Screen Sharing Links", expanded=True):
    st.info("Bagikan hanya Presenter URL melalui Microsoft Teams atau Zoom. Jangan membagikan Interviewer URL.")
    presenter_link = session_url("presenter", session["session_code"], session["presenter_token"])
    interviewer_link = session_url("interviewer", session["session_code"], session["interviewer_token"])
    st.text_input("Session Code", value=session["session_code"], disabled=True)
    st.text_input("Presenter URL — share this only", value=presenter_link)
    st.text_input("Interviewer URL — keep private", value=interviewer_link)
    st.caption("Presenter URL dapat dibagikan melalui Microsoft Teams atau Zoom. Jangan bagikan Interviewer URL.")

index = int(session.get("current_index", 0))
q = QUESTIONS[index]
answers = session.get("answers") or {}
notes = session.get("notes") or {}
assessments = session.get("assessments") or {}

st.progress(len(answers) / len(QUESTIONS))
st.caption(f"Question {index + 1} of {len(QUESTIONS)} • Answered {len(answers)}/{len(QUESTIONS)}")

st.markdown("### Current Question")
st.markdown(f'<div class="question-card"><div class="question-text">{q["question"]}</div><div class="option"><b>A.</b> {q["a"]}</div><div class="option"><b>B.</b> {q["b"]}</div></div>', unsafe_allow_html=True)

current_answer = answers.get(str(q["id"]), "")
answer = st.radio(
    "Catat pilihan kandidat",
    ["A", "B"],
    index=["A", "B"].index(current_answer) if current_answer in ("A", "B") else None,
    horizontal=True,
    key=f"answer_question_{q['id']}",
)
if answer and answer != current_answer:
    answers[str(q["id"])] = answer
    update_session(session["id"], {"answers": answers})
    session["answers"] = answers

c1, c2, c3 = st.columns(3)
with c1:
    if st.button("← Previous", disabled=index == 0, use_container_width=True):
        update_session(session["id"], {"current_index": index - 1})
        st.rerun()
with c2:
    if st.button("🔄 Refresh Presenter", use_container_width=True):
        st.rerun()
with c3:
    if st.button("Next →", disabled=index >= len(QUESTIONS) - 1, type="primary", use_container_width=True):
        if str(q["id"]) not in answers:
            st.warning("Catat pilihan A atau B terlebih dahulu.")
        else:
            update_session(session["id"], {"current_index": index + 1})
            st.rerun()

st.divider()
st.subheader("🔒 Live Behavioral Analysis")
st.write(live_interpretation(q, answer))

st.subheader("Suggested Follow-up")
st.info(q["followup"])

note_value = st.text_area(
    "Private Observation / Evidence",
    value=notes.get(str(q["id"]), ""),
    placeholder="Tuliskan contoh nyata, bukti perilaku, respons kandidat, dan hal yang perlu divalidasi.",
)
if note_value != notes.get(str(q["id"]), ""):
    notes[str(q["id"])] = note_value
    update_session(session["id"], {"notes": notes})

st.divider()
st.subheader("📊 Private Summary by Competency")
for category in dict.fromkeys(q["category"] for q in QUESTIONS):
    data = category_analysis(session, category)
    with st.expander(f"{category} — {data['answered']} answered / {data['noted']} notes"):
        st.markdown("**Observed pattern**")
        st.write(data["pattern"])
        if data["strengths"]:
            st.markdown("**Potential strengths to validate**")
            for item in data["strengths"]:
                st.write(f"- {item}")
        if data["watchouts"]:
            st.markdown("**Validation points**")
            for item in data["watchouts"]:
                st.write(f"- {item}")

st.divider()
st.subheader("🤖 AI Full Assessment")
st.caption("Private interviewer-only analysis. The candidate should not see this section.")

if "ai_assessment" not in st.session_state:
    saved_assessment = session.get("assessments") or {}
    if isinstance(saved_assessment, dict):
        saved_assessment = saved_assessment.get("ai_markdown", "")
    st.session_state["ai_assessment"] = saved_assessment or ""

if st.button("✨ Generate / Refresh AI Analysis", type="primary", use_container_width=True):
    with st.spinner("Generating AI assessment..."):
        try:
            ai_result = generate_ai_assessment(session)
            st.session_state["ai_assessment"] = ai_result
            update_session(session["id"], {"assessments": {"ai_markdown": ai_result}})
            st.success("AI assessment berhasil dibuat dan disimpan.")
        except Exception as exc:
            st.error(str(exc))

if st.session_state.get("ai_assessment"):
    st.markdown(st.session_state["ai_assessment"])
else:
    st.info("Klik tombol di atas untuk membuat analisis AI lengkap.")

st.divider()
st.subheader("🏁 Automatic Interview Conclusion")
st.success("Automatic analysis generated from the answers currently saved in Supabase.")
st.markdown(
    f"""
    <div style="border: 2px solid #2e7d32; border-radius: 12px; padding: 18px;
                background-color: rgba(46, 125, 50, 0.06); line-height: 1.65;">
        {automatic_conclusion(session)}
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Interviewer Final Notes")
conclusion = st.text_area(
    "Balanced conclusion",
    value=session.get("overall_conclusion", ""),
    placeholder="Ringkas kekuatan yang didukung bukti, area yang perlu divalidasi, dan pertanyaan lanjutan.",
    height=180,
)
if conclusion != session.get("overall_conclusion", ""):
    update_session(session["id"], {"overall_conclusion": conclusion})

if st.button("Mark Interview as Completed", type="primary", use_container_width=True):
    update_session(session["id"], {"status": "completed"})
    st.success("Interview ditandai sebagai completed.")

export_rows = []
for item in QUESTIONS:
    item_answer = answers.get(str(item["id"]), "")
    export_rows.append({
        "Question": item["id"],
        "Category": item["category"],
        "Question Text": item["question"],
        "Option A": item["a"],
        "Option B": item["b"],
        "Selected Answer": item_answer,
        "Behavioral Interpretation": rich_interpretation(item, item_answer),
        "Interviewer Note": notes.get(str(item["id"]), ""),
        "Follow-up": item["followup"],
    })

payload = {
    "candidate_name": session["candidate_name"],
    "position": session["position"],
    "interview_date": session["interview_date"],
    "session_code": session["session_code"],
    "status": session.get("status"),
    "answers": answers,
    "notes": notes,
    "assessments": assessments,
    "overall_conclusion": conclusion,
    "questions": export_rows,
}
st.download_button(
    "Download JSON",
    json.dumps(payload, ensure_ascii=False, indent=2),
    file_name=f"interview_{session['session_code']}.json",
    mime="application/json",
    use_container_width=True,
)
st.download_button(
    "Download CSV",
    pd.DataFrame(export_rows).to_csv(index=False),
    file_name=f"interview_{session['session_code']}.csv",
    mime="text/csv",
    use_container_width=True,
)

try:
    pdf_bytes = build_pdf_export(
        session=session,
        questions_rows=export_rows,
        ai_assessment=st.session_state.get("ai_assessment", ""),
        conclusion=conclusion,
    )
    st.download_button(
        "Download PDF Report",
        data=pdf_bytes,
        file_name=f"interview_{session['session_code']}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
except Exception as exc:
    st.warning(f"PDF export belum tersedia. Pastikan dependency reportlab terpasang. Detail: {exc}")
