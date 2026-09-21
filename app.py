import streamlit as st
import pandas as pd
import json
from datetime import datetime

st.set_page_config(page_title="IT Smart Character Interview", page_icon="🧠", layout="wide")

st.markdown("""
<style>
.block-container{max-width:1200px;padding-top:1.5rem}
.question-card,.analysis-card{background:white;border:1px solid #dbe2ea;border-radius:16px;padding:24px;margin:14px 0}
.question-text{font-size:32px;font-weight:700;line-height:1.35;text-align:center;color:#0f172a}
.option{background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:18px;font-size:19px;line-height:1.45;margin:10px 0}
</style>
""", unsafe_allow_html=True)

# A/B options are mapped to behavioral dimensions.
RAW = [
(1,"Logical Thinking","Saat menghadapi masalah baru, kamu lebih memilih...","Langsung mencoba beberapa solusi untuk melihat hasilnya.","Mengumpulkan informasi dan memahami penyebab sebelum bertindak.","Action-oriented; perlu memastikan analisis akar masalah tetap dilakukan.","Systematic; cenderung memahami konteks sebelum bertindak.","Apakah kamu tetap melakukan root-cause analysis setelah tindakan awal?"),
(2,"Logical Thinking","Jika terjadi gangguan sistem, kamu cenderung...","Fokus pada penyebab yang paling mungkin terjadi.","Memeriksa beberapa kemungkinan penyebab secara sistematis.","Hypothesis-focused; berpotensi cepat mempersempit investigasi.","Systematic diagnosis; berpotensi lebih menyeluruh namun perlu menjaga kecepatan.","Bagaimana kamu memastikan penyebab yang paling mungkin bukan asumsi yang keliru?"),
(3,"Logical Thinking","Ketika masalah muncul setelah perubahan sistem, kamu akan...","Memeriksa perubahan terakhir yang dilakukan.","Melakukan pemeriksaan dasar secara menyeluruh.","Change-correlation; memulai dari indikasi perubahan terbaru.","Baseline-checking; memvalidasi kondisi dasar sistem.","Bagaimana kamu menghindari kesimpulan terlalu cepat bahwa perubahan terakhir adalah penyebabnya?"),
(4,"Logical Thinking","Ketika solusi pertama belum berhasil, kamu lebih memilih...","Memodifikasi solusi tersebut sampai berhasil.","Meninjau kembali asumsi dan mencoba hipotesis lain.","Iterative action; mencoba penyempurnaan langsung.","Assumption review; bersedia mengubah hipotesis.","Kapan kamu memutuskan berhenti memodifikasi solusi dan mengganti pendekatan?"),
(5,"Learning Agility","Saat mempelajari tools baru, kamu cenderung...","Mengeksplorasi dan mencari tahu secara mandiri.","Membaca dokumentasi atau bertanya kepada orang berpengalaman.","Self-exploration; belajar melalui percobaan.","Guided learning; memanfaatkan dokumentasi dan pengalaman orang lain.","Bagaimana kamu tahu kapan harus belajar sendiri dan kapan meminta bantuan?"),
(6,"Learning Agility","Saat mempelajari sebuah sistem, hal yang paling ingin kamu pahami adalah...","Cara sistem tersebut bekerja di balik layar.","Cara menggunakan sistem untuk menyelesaikan pekerjaan.","Technical depth; tertarik pada mekanisme sistem.","Task application; fokus pada manfaat praktis.","Bagaimana kamu menghubungkan pemahaman teknis dengan kebutuhan user?"),
(7,"Learning Agility","Jika ada metode baru untuk menyelesaikan pekerjaan, kamu akan...","Menggunakan metode lama yang sudah terbukti.","Mempelajari metode baru untuk melihat apakah lebih efektif.","Proven method; mengutamakan stabilitas.","Experimentation; terbuka menguji pendekatan baru.","Bagaimana kamu menguji metode baru tanpa mengganggu operasional?"),
(8,"Learning Agility","Ketika muncul pertanyaan saat bekerja, kamu lebih memilih...","Mencatatnya dan mempelajarinya nanti.","Langsung bertanya agar bisa memahami saat itu juga.","Self-research; mencoba mencari jawaban mandiri.","Immediate clarification; mencari klarifikasi dengan cepat.","Bagaimana kamu menghindari ketergantungan pada orang lain ketika sering bertanya?"),
(9,"Problem Solving","Saat prosedur standar tidak menyelesaikan masalah, kamu akan...","Mencari alternatif di luar prosedur standar.","Memeriksa prosedur standar secara lebih mendalam.","Creative alternative; mencari pendekatan di luar kebiasaan.","Process review; memeriksa kembali proses yang tersedia.","Bagaimana kamu memastikan alternatif yang dipilih tetap aman dan terdokumentasi?"),
(10,"Problem Solving","Untuk kebutuhan sistem baru, kamu lebih tertarik pada...","Solusi open-source yang bisa disesuaikan.","Solusi komersial yang matang dan memiliki dukungan vendor.","Customization; memperhatikan fleksibilitas dan penyesuaian.","Vendor support; memperhatikan kematangan dan dukungan.","Faktor apa yang kamu gunakan untuk membandingkan risiko dan biaya kedua pilihan?"),
(11,"Problem Solving","Jika menemukan pekerjaan berulang, kamu akan...","Mencari cara untuk mengotomatisasi pekerjaan tersebut.","Membuat prosedur manual yang lebih terstandarisasi.","Automation; mencari efisiensi melalui teknologi.","Standardization; memperkuat konsistensi proses.","Bagaimana kamu menilai apakah otomasi memang layak dilakukan?"),
(12,"Decision Making","Guest Wi-Fi mengalami gangguan besar. Kamu akan...","Segera melakukan tindakan untuk memulihkan layanan.","Memahami dampak dan melakukan pemeriksaan singkat terlebih dahulu.","Rapid restoration; mengutamakan pemulihan cepat.","Impact assessment; mengutamakan pemeriksaan dampak sebelum tindakan.","Apa tindakanmu jika informasi belum lengkap tetapi guest impact sangat tinggi?"),
(13,"Decision Making","Ketika diminta memberikan solusi dengan cepat, kamu akan...","Memberikan solusi sementara berdasarkan informasi yang tersedia.","Mengumpulkan informasi penting terlebih dahulu.","Provisional action; bersedia mengambil langkah sementara.","Information gathering; mengutamakan informasi kunci sebelum keputusan.","Bagaimana kamu mengomunikasikan risiko dari solusi sementara?"),
(14,"Decision Making","Jika pekerjaan belum selesai menjelang akhir jam kerja, kamu akan...","Tetap melanjutkan pekerjaan sampai selesai.","Mendokumentasikan status, mengomunikasikan kondisi, dan membuat rencana lanjutan.","Persistence; mengutamakan penyelesaian langsung.","Handover planning; mengutamakan komunikasi dan kesinambungan pekerjaan.","Dalam kondisi apa kamu memilih melanjutkan pekerjaan di luar jam kerja?"),
(15,"Practical Judgment","Ketika hasil pekerjaan sudah memenuhi requirement, kamu akan...","Menyelesaikannya dan melanjutkan pekerjaan berikutnya.","Melakukan penyempurnaan lebih lanjut agar hasilnya lebih sempurna.","Delivery focus; menjaga penyelesaian dan prioritas.","Quality refinement; memberi ruang untuk peningkatan kualitas.","Bagaimana kamu menentukan batas antara cukup baik dan over-engineering?"),
(16,"Practical Judgment","Jika menemukan kesalahan kecil pada data, kamu akan...","Memperbaiki kesalahan tersebut dan melanjutkan pekerjaan.","Mencari tahu apakah ada masalah yang lebih luas pada sumber data.","Local fix; menyelesaikan masalah yang terlihat.","Systemic investigation; mencari kemungkinan masalah yang lebih luas.","Bagaimana kamu menyeimbangkan kebutuhan memperbaiki laporan dengan waktu yang tersedia?"),
(17,"Initiative","Jika menemukan cara untuk meningkatkan efisiensi pekerjaan, kamu akan...","Mengusulkan perbaikan meskipun tidak diminta.","Memahami alasan di balik proses yang berjalan terlebih dahulu.","Proactive change; cenderung mengusulkan perbaikan.","Context first; memahami alasan proses sebelum perubahan.","Bagaimana kamu memperoleh dukungan sebelum mengubah proses yang digunakan tim?"),
(18,"Initiative","Setelah menyelesaikan pekerjaan rutin lebih cepat, kamu akan...","Menggunakan waktu yang tersisa untuk pekerjaan lain.","Mencari cara agar pekerjaan rutin tersebut bisa lebih efisien.","Task completion; memanfaatkan waktu untuk tugas lain.","Efficiency improvement; mencari peluang optimasi.","Ceritakan perbaikan proses yang pernah kamu lakukan tanpa diminta."),
(19,"Collaboration","Ketika solusi kamu berbeda dengan rekan kerja, kamu akan...","Menjelaskan mengapa solusi kamu lebih baik.","Menanyakan alasan dan pertimbangan di balik solusi rekan kerja.","Advocacy; menjelaskan dan mempertahankan sudut pandang.","Active listening; mencari pemahaman atas perspektif rekan kerja.","Bagaimana kamu mengambil keputusan ketika kedua pendekatan sama-sama memiliki alasan kuat?"),
(20,"Learning Orientation","Jika memiliki waktu untuk belajar, kamu cenderung memilih...","Topik yang langsung berguna untuk pekerjaan.","Topik menarik yang belum tentu langsung memiliki kegunaan.","Job relevance; mengutamakan penerapan langsung.","Broad curiosity; terbuka pada pengetahuan yang lebih luas.","Bagaimana kamu mengubah pengetahuan yang menarik menjadi manfaat praktis?")
]

QUESTIONS = [
    {"id":r[0],"category":r[1],"question":r[2],"a":r[3],"b":r[4],
     "pattern_a":r[5],"pattern_b":r[6],"followup":r[7]}
    for r in RAW
]

DEFAULTS = {
    "page":"setup","candidate_name":"","position":"IT Executive",
    "interview_date":datetime.now().date(),"index":0,"answers":{},
    "notes":{},"assessments":{},"overall":"","started_at":None
}
for key,value in DEFAULTS.items():
    if key not in st.session_state: st.session_state[key]=value

def reset():
    for key,value in DEFAULTS.items(): st.session_state[key]=value

def by_category(category):
    return [q for q in QUESTIONS if q["category"]==category]

def counts(category=None):
    qs=by_category(category) if category else QUESTIONS
    a=sum(st.session_state.answers.get(q["id"])=="A" for q in qs)
    b=sum(st.session_state.answers.get(q["id"])=="B" for q in qs)
    return a,b

def live_interpretation(q,answer):
    if answer not in ("A","B"):
        return "Belum ada pilihan yang dicatat."
    pattern=q["pattern_a"] if answer=="A" else q["pattern_b"]
    return f"Jawaban {answer} mengindikasikan {pattern} Ini adalah indikasi awal dan perlu dibaca bersama jawaban lain serta penjelasan kandidat."

def overall_summary():
    result=[]
    for category in dict.fromkeys(q["category"] for q in QUESTIONS):
        a,b=counts(category)
        total=a+b
        if not total: continue
        if a==b:
            pattern="pola pilihan relatif seimbang"
        elif a>b:
            pattern="lebih sering memilih pendekatan pada opsi A"
        else:
            pattern="lebih sering memilih pendekatan pada opsi B"
        result.append((category,pattern,a,b))
    return result

def export_rows():
    rows=[]
    for q in QUESTIONS:
        ans=st.session_state.answers.get(q["id"],"")
        rows.append({
            "Question":q["id"],"Category":q["category"],
            "Question":q["question"],"Option A":q["a"],"Option B":q["b"],
            "Selected Answer":ans,"Behavioral Interpretation":live_interpretation(q,ans),
            "Interviewer Note":st.session_state.notes.get(q["id"],"")
        })
    return rows

def setup():
    st.title("🧠 IT Smart Character Interview")
    st.write("A/B behavioral interview dengan analisis otomatis sementara dan kesimpulan lengkap setelah interview.")
    st.info("Selama interview, analisis sementara hanya ditampilkan di bagian bawah halaman interviewer. Kandidat tidak melihatnya jika area tersebut tidak ikut dibagikan.")
    with st.form("setup_form"):
        name=st.text_input("Nama Kandidat",value=st.session_state.candidate_name)
        position=st.selectbox("Posisi",["IT Executive","IT Supervisor","Assistant IT Manager","IT Manager","Other"])
        date=st.date_input("Tanggal Interview",value=st.session_state.interview_date)
        start=st.form_submit_button("Mulai Interview",type="primary",use_container_width=True)
    if start:
        if not name.strip(): st.error("Nama kandidat wajib diisi.")
        else:
            st.session_state.candidate_name=name.strip()
            st.session_state.position=position
            st.session_state.interview_date=date
            st.session_state.started_at=datetime.now().isoformat()
            st.session_state.page="interview"
            st.rerun()

def interview():
    q=QUESTIONS[st.session_state.index]
    total=len(QUESTIONS)
    answered=len(st.session_state.answers)
    st.markdown(f"### {st.session_state.candidate_name}")
    st.progress(answered/total)
    st.caption(f"Question {q['id']} of {total} • Answered {answered}/{total}")

    st.markdown('<div class="question-card">',unsafe_allow_html=True)
    st.markdown(f'<div class="question-text">{q["question"]}</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="option"><b>A.</b> {q["a"]}</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="option"><b>B.</b> {q["b"]}</div>',unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)

    answer=st.radio("Pilihan kandidat",["A","B"],
                    index=["A","B"].index(st.session_state.answers.get(q["id"]))
                    if st.session_state.answers.get(q["id"]) in ("A","B") else None,
                    horizontal=True,key=f"answer_{q['id']}")
    if answer: st.session_state.answers[q["id"]]=answer

    # Live analysis is intentionally below the question area.
    st.markdown("### 🔒 Interviewer Panel — Live Analysis")
    st.caption("Jangan ikutkan bagian ini ketika membagikan layar kepada kandidat.")
    with st.container(border=True):
        if answer:
            st.write(live_interpretation(q,answer))
            st.write("**Suggested follow-up:**")
            st.write(q["followup"])
        else:
            st.info("Pilih jawaban untuk melihat interpretasi sementara.")

        note=st.text_area("Private interviewer note",value=st.session_state.notes.get(q["id"],""),key=f"note_{q['id']}",height=100)
        st.session_state.notes[q["id"]]=note

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
            elif st.session_state.index<total-1:
                st.session_state.index+=1;st.rerun()
            else:
                st.session_state.page="results";st.rerun()

def results():
    st.title("📊 Private Interview Analysis")
    st.warning("Hentikan screen sharing sebelum membaca halaman ini.")
    st.write(f"**Candidate:** {st.session_state.candidate_name}  |  **Position:** {st.session_state.position}")

    st.markdown("## 1. Automatic Overall Conclusion")
    summaries=overall_summary()
    if not summaries:
        st.info("Belum ada data jawaban.")
    else:
        for category,pattern,a,b in summaries:
            st.markdown(f"### {category}")
            st.write(f"**Pattern:** {pattern}. (A: {a}, B: {b})")
            category_qs=by_category(category)
            selected=[q for q in category_qs if st.session_state.answers.get(q["id"]) in ("A","B")]
            patterns=[]
            for q in selected:
                ans=st.session_state.answers[q["id"]]
                patterns.append(q["pattern_a"] if ans=="A" else q["pattern_b"])
            st.write("**Behavioral signals:** " + " ".join(patterns))
            st.write("**Interpretation:** Pola ini perlu dipahami bersama konteks jawaban verbal, pengalaman kerja, dan contoh konkret kandidat.")
            st.write("**Validation focus:** " + " ".join(q["followup"] for q in selected[:2]))

    st.markdown("## 2. Competency Assessment")
    assessment_options=["Not assessed","1 - Not demonstrated","2 - Partially demonstrated","3 - Demonstrated","4 - Strong evidence"]
    for category,_,_,_ in summaries:
        current=st.session_state.assessments.get(category,"Not assessed")
        choice=st.selectbox(category,assessment_options,
                             index=assessment_options.index(current) if current in assessment_options else 0,
                             key=f"assessment_{category}")
        st.session_state.assessments[category]=choice

    st.markdown("## 3. Overall Interview Conclusion")
    st.session_state.overall=st.text_area(
        "Kesimpulan interviewer",
        value=st.session_state.overall,
        height=180,
        placeholder="Tuliskan kekuatan berdasarkan bukti, area risiko yang perlu divalidasi, dan hal yang perlu diperhatikan untuk posisi yang dilamar."
    )

    rows=export_rows()
    payload={
        "candidate_name":st.session_state.candidate_name,
        "position":st.session_state.position,
        "interview_date":str(st.session_state.interview_date),
        "started_at":st.session_state.started_at,
        "completed_at":datetime.now().isoformat(),
        "category_assessments":st.session_state.assessments,
        "overall_conclusion":st.session_state.overall,
        "questions":rows
    }
    json_data=json.dumps(payload,ensure_ascii=False,indent=2)
    csv_data=pd.DataFrame(rows).to_csv(index=False)
    x,y,z=st.columns(3)
    with x:
        st.download_button("Download JSON",json_data,"interview_result.json","application/json",use_container_width=True)
    with y:
        st.download_button("Download CSV",csv_data,"interview_result.csv","text/csv",use_container_width=True)
    with z:
        if st.button("Interview Baru",use_container_width=True):
            reset();st.rerun()

if st.session_state.page=="setup":
    setup()
elif st.session_state.page=="interview":
    interview()
else:
    results()
