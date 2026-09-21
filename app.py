import streamlit as st
import pandas as pd
import json
from datetime import datetime

st.set_page_config(
    page_title="IT Smart Character Interview",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
.block-container {max-width:1200px;padding-top:2rem}
.question-card {background:#fff;border:1px solid #dbe2ea;border-radius:18px;padding:32px;margin:20px 0}
.question-text {font-size:32px;font-weight:700;line-height:1.35;text-align:center;color:#0f172a}
.option {background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:20px;font-size:20px;line-height:1.45;margin:10px 0}
.private-note {background:#fff7ed;border:1px solid #fed7aa;border-radius:12px;padding:16px}
</style>
""", unsafe_allow_html=True)

# Each option has a behavioral signal. Signals are not automatically treated as good/bad.
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
{"id":x[0],"category":x[1],"question":x[2],"a":x[3],"b":x[4],
 "signal_a":x[5],"signal_b":x[6],"followup":x[7]} for x in RAW_QUESTIONS
]

DEFAULTS = {
    "page":"setup","candidate_name":"","position":"IT Executive",
    "interview_date":datetime.now().date(),"index":0,"answers":{},
    "notes":{},"assessments":{},"started_at":None
}
for k,v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k]=v

def reset():
    for k,v in DEFAULTS.items(): st.session_state[k]=v

def category_questions(category):
    return [q for q in QUESTIONS if q["category"] == category]

def category_summary():
    result={}
    for q in QUESTIONS:
        c=q["category"]
        result.setdefault(c,{"answered":0,"a":0,"b":0,"assessment":[]})
        ans=st.session_state.answers.get(q["id"])
        if ans in ("A","B"):
            result[c]["answered"] += 1
            result[c][ans.lower()] += 1
    for c in result:
        result[c]["assessment"] = [
            st.session_state.assessments.get(q["id"])
            for q in category_questions(c)
            if st.session_state.assessments.get(q["id"])
        ]
    return result

def export_rows():
    rows=[]
    for q in QUESTIONS:
        rows.append({
            "Question":q["id"],"Category":q["category"],
            "Question Text":q["question"],"Option A":q["a"],
            "Option B":q["b"],"Selected Answer":st.session_state.answers.get(q["id"],""),
            "Interviewer Note":st.session_state.notes.get(q["id"],""),
            "Assessment":st.session_state.assessments.get(q["id"],"")
        })
    return rows

def render_setup():
    st.title("🧠 IT Smart Character Interview")
    st.write("Interview berbasis perilaku untuk membantu interviewer menggali pola berpikir dan pengalaman nyata kandidat.")
    st.info("Sebelum screen sharing, isi data kandidat. Selama interview, kandidat hanya melihat pertanyaan dan pilihan A/B. Analisis tersedia setelah interview selesai.")
    with st.form("setup"):
        name=st.text_input("Nama Kandidat",value=st.session_state.candidate_name)
        position=st.selectbox("Posisi",["IT Executive","IT Supervisor","Assistant IT Manager","IT Manager","Other"])
        date=st.date_input("Tanggal Interview",value=st.session_state.interview_date)
        submitted=st.form_submit_button("Mulai Interview",type="primary",use_container_width=True)
    if submitted:
        if not name.strip():
            st.error("Nama kandidat wajib diisi.")
        else:
            st.session_state.candidate_name=name.strip()
            st.session_state.position=position
            st.session_state.interview_date=date
            st.session_state.started_at=datetime.now().isoformat()
            st.session_state.page="interview"
            st.rerun()

def render_interview():
    q=QUESTIONS[st.session_state.index]
    total=len(QUESTIONS)
    answered=len(st.session_state.answers)
    st.markdown(f"### Candidate: {st.session_state.candidate_name}")
    st.progress(answered/total)
    st.caption(f"Question {q['id']} of {total} • Answered {answered}/{total}")
    st.markdown('<div class="question-card">',unsafe_allow_html=True)
    st.markdown(f'<div class="question-text">{q["question"]}</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="option"><b>A.</b> {q["a"]}</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="option"><b>B.</b> {q["b"]}</div>',unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)

    current=st.session_state.answers.get(q["id"])
    choice=st.radio("Catat pilihan kandidat",["A","B"],
                    index=["A","B"].index(current) if current in ("A","B") else None,
                    horizontal=True,key=f"choice_{q['id']}")
    if choice: st.session_state.answers[q["id"]]=choice

    st.markdown("---")
    c1,c2,c3=st.columns(3)
    with c1:
        if st.button("← Previous",disabled=st.session_state.index==0,use_container_width=True):
            st.session_state.index-=1;st.rerun()
    with c2:
        if st.button("Reset",use_container_width=True):
            reset();st.rerun()
    with c3:
        label="Finish Interview" if st.session_state.index==total-1 else "Next →"
        if st.button(label,type="primary",use_container_width=True):
            if q["id"] not in st.session_state.answers:
                st.warning("Pilih A atau B terlebih dahulu.")
            elif st.session_state.index < total-1:
                st.session_state.index+=1;st.rerun()
            else:
                st.session_state.page="results";st.rerun()
    st.caption("Catatan interviewer dan analisis tidak ditampilkan selama halaman interview.")

def render_results():
    st.title("📊 Private Interview Analysis")
    st.warning("Pastikan screen sharing sudah dihentikan sebelum membaca halaman ini.")
    st.write(f"**Candidate:** {st.session_state.candidate_name}")
    st.write(f"**Position:** {st.session_state.position}")
    st.write(f"**Date:** {st.session_state.interview_date}")
    st.markdown("## 1. Competency Review")
    st.caption("Pola jawaban adalah bahan eksplorasi, bukan bukti final tentang karakter kandidat.")

    for category, values in category_summary().items():
        with st.expander(category,expanded=True):
            st.write(f"Answered: {values['answered']} | A: {values['a']} | B: {values['b']}")
            for q in category_questions(category):
                ans=st.session_state.answers.get(q["id"],"-")
                st.markdown(f"**Q{q['id']} — Answer: {ans}**")
                st.write(q["question"])
                st.caption("Follow-up question")
                st.write(q["followup"])
                note=st.text_area("Observation / evidence",value=st.session_state.notes.get(q["id"],""),key=f"result_note_{q['id']}")
                st.session_state.notes[q["id"]]=note
            assessment=st.selectbox(
                "Overall interviewer assessment",
                ["Not assessed","1 - Not demonstrated","2 - Partially demonstrated","3 - Demonstrated","4 - Strong evidence"],
                index=["Not assessed","1 - Not demonstrated","2 - Partially demonstrated","3 - Demonstrated","4 - Strong evidence"].index(
                    st.session_state.assessments.get(category,"Not assessed")
                ) if st.session_state.assessments.get(category,"Not assessed") in ["Not assessed","1 - Not demonstrated","2 - Partially demonstrated","3 - Demonstrated","4 - Strong evidence"] else 0,
                key=f"assessment_{category}"
            )
            st.session_state.assessments[category]=assessment

    st.markdown("## 2. Overall Interview Conclusion")
    conclusion=st.text_area(
        "Write a balanced conclusion",
        value=st.session_state.notes.get("overall",""),
        placeholder="Ringkas kekuatan yang didukung bukti, area yang perlu divalidasi, dan rekomendasi pertanyaan lanjutan.",
        height=180
    )
    st.session_state.notes["overall"]=conclusion

    rows=export_rows()
    payload={
        "candidate_name":st.session_state.candidate_name,
        "position":st.session_state.position,
        "interview_date":str(st.session_state.interview_date),
        "started_at":st.session_state.started_at,
        "completed_at":datetime.now().isoformat(),
        "category_assessments":st.session_state.assessments,
        "overall_conclusion":conclusion,
        "questions":rows
    }
    json_data=json.dumps(payload,ensure_ascii=False,indent=2)
    csv_data=pd.DataFrame(rows).to_csv(index=False)

    a,b,c=st.columns(3)
    with a:
        st.download_button("Download JSON",json_data,
                           file_name="it_interview_result.json",
                           mime="application/json",use_container_width=True)
    with b:
        st.download_button("Download CSV",csv_data,
                           file_name="it_interview_result.csv",
                           mime="text/csv",use_container_width=True)
    with c:
        if st.button("Interview Baru",use_container_width=True):
            reset();st.rerun()

if st.session_state.page=="setup":
    render_setup()
elif st.session_state.page=="interview":
    render_interview()
else:
    render_results()
