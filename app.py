
import streamlit as st
import json
import csv
import io
from datetime import datetime

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="IT Smart Character Interview",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background: #f5f7fb;
    }

    .main-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #172033;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        color: #667085;
        font-size: 0.95rem;
        margin-bottom: 1.4rem;
    }

    .question-card {
        background: white;
        border-radius: 18px;
        padding: 28px;
        border: 1px solid #e5eaf2;
        box-shadow: 0 4px 18px rgba(15, 23, 42, 0.04);
        margin: 12px 0 20px 0;
    }

    .question-number {
        color: #64748b;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .question-title {
        font-size: 1.35rem;
        font-weight: 750;
        color: #172033;
        line-height: 1.45;
        margin-top: 10px;
        margin-bottom: 22px;
    }

    .choice-label {
        font-size: 0.92rem;
        font-weight: 650;
        color: #475467;
        margin-bottom: 4px;
    }

    .metric-card {
        background: white;
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #e5eaf2;
        margin-bottom: 10px;
    }

    .metric-label {
        color: #667085;
        font-size: 0.85rem;
    }

    .metric-value {
        color: #172033;
        font-size: 1.65rem;
        font-weight: 800;
    }

    .section-title {
        font-size: 1.2rem;
        font-weight: 750;
        color: #172033;
        margin-top: 18px;
        margin-bottom: 10px;
    }

    div.stButton > button {
        border-radius: 10px;
        font-weight: 650;
        min-height: 42px;
    }

    [data-testid="stMetric"] {
        background: white;
        padding: 12px;
        border-radius: 12px;
        border: 1px solid #e5eaf2;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# QUESTIONS
# ============================================================

QUESTIONS = [
    {
        "id": 1,
        "category": "Logical Thinking",
        "question": "Saat menghadapi masalah baru, kamu lebih memilih...",
        "a": "Langsung mencoba beberapa solusi untuk melihat hasilnya.",
        "b": "Mengumpulkan informasi dan memahami penyebab sebelum bertindak.",
    },
    {
        "id": 2,
        "category": "Logical Thinking",
        "question": "Kamu menemukan dua kemungkinan penyebab masalah.",
        "a": "Fokus pada penyebab yang paling mungkin terlebih dahulu.",
        "b": "Periksa kedua kemungkinan secara sistematis sebelum menyimpulkan.",
    },
    {
        "id": 3,
        "category": "Logical Thinking",
        "question": "Sebuah sistem bekerja normal selama 6 bulan, lalu tiba-tiba bermasalah.",
        "a": "Mulai dari hal-hal yang baru berubah.",
        "b": "Mulai dari pemeriksaan dasar sistem secara menyeluruh.",
    },
    {
        "id": 4,
        "category": "Logical Thinking",
        "question": "Kamu punya solusi yang menurutmu benar, tetapi hasil pengujian tidak sesuai.",
        "a": "Coba modifikasi solusi sampai mendapatkan hasil yang diharapkan.",
        "b": "Kembali memeriksa asumsi awal dan menguji hipotesis lain.",
    },
    {
        "id": 5,
        "category": "Learning Ability",
        "question": "Diberikan aplikasi baru yang belum pernah kamu gunakan.",
        "a": "Eksplorasi sendiri sampai memahami cara kerjanya.",
        "b": "Cari dokumentasi atau orang berpengalaman untuk mempercepat belajar.",
    },
    {
        "id": 6,
        "category": "Learning Ability",
        "question": "Saat training, kamu lebih tertarik...",
        "a": "Memahami bagaimana sistem bekerja di balik layar.",
        "b": "Memahami bagaimana sistem digunakan untuk menyelesaikan pekerjaan.",
    },
    {
        "id": 7,
        "category": "Learning Ability",
        "question": "Kamu diberi tugas yang bisa selesai dengan cara lama, tetapi ada metode baru.",
        "a": "Gunakan cara lama yang sudah terbukti berhasil.",
        "b": "Pelajari cara baru untuk melihat apakah bisa lebih efektif.",
    },
    {
        "id": 8,
        "category": "Learning Ability",
        "question": "Kamu mendengar penjelasan teknis yang belum sepenuhnya kamu pahami.",
        "a": "Simpan pertanyaan dan pelajari sendiri setelahnya.",
        "b": "Langsung bertanya agar bisa memahami saat itu juga.",
    },
    {
        "id": 9,
        "category": "Creative Problem Solving",
        "question": "Sistem utama mengalami gangguan dan solusi standar belum berhasil.",
        "a": "Cari solusi alternatif yang berbeda dari prosedur biasa.",
        "b": "Periksa kembali prosedur standar secara mendalam.",
    },
    {
        "id": 10,
        "category": "Creative Problem Solving",
        "question": "Kamu punya anggaran terbatas untuk menyelesaikan kebutuhan IT.",
        "a": "Cari tools atau solusi open-source yang bisa disesuaikan.",
        "b": "Pilih solusi komersial yang sudah matang dan didukung vendor.",
    },
    {
        "id": 11,
        "category": "Creative Problem Solving",
        "question": "Kamu harus menyelesaikan pekerjaan berulang setiap hari.",
        "a": "Cari cara untuk mengotomatisasi pekerjaan tersebut.",
        "b": "Buat prosedur kerja yang rapi agar proses manual lebih konsisten.",
    },
    {
        "id": 12,
        "category": "Decision Making",
        "question": "Tamu hotel mengalami masalah Wi-Fi dan meminta bantuan segera.",
        "a": "Segera lakukan tindakan untuk memulihkan koneksi.",
        "b": "Pahami dampak dan lakukan pemeriksaan singkat sebelum menentukan tindakan.",
    },
    {
        "id": 13,
        "category": "Decision Making",
        "question": "Atasan meminta solusi segera, tetapi informasi yang kamu miliki belum lengkap.",
        "a": "Sampaikan solusi sementara berdasarkan informasi yang tersedia.",
        "b": "Minta waktu untuk mengumpulkan informasi penting sebelum merekomendasikan solusi.",
    },
    {
        "id": 14,
        "category": "Decision Making",
        "question": "Kamu sedang mengerjakan masalah sulit dan waktu kerja hampir selesai.",
        "a": "Lanjutkan sampai masalah selesai meskipun harus melewati jam kerja.",
        "b": "Dokumentasikan progres, komunikasikan status, dan lanjutkan dengan rencana yang jelas.",
    },
    {
        "id": 15,
        "category": "Practical Judgment",
        "question": "Sebuah laporan sudah memenuhi kebutuhan pengguna, tetapi masih bisa diperbaiki.",
        "a": "Selesaikan dan serahkan karena kebutuhan utama sudah terpenuhi.",
        "b": "Sempurnakan terlebih dahulu agar hasilnya lebih optimal.",
    },
    {
        "id": 16,
        "category": "Practical Judgment",
        "question": "Kamu menemukan kesalahan kecil dalam data yang akan digunakan untuk laporan manajemen.",
        "a": "Perbaiki kesalahan yang ditemukan dan lanjutkan pekerjaan.",
        "b": "Telusuri apakah kesalahan itu menunjukkan masalah yang lebih luas pada sumber data.",
    },
    {
        "id": 17,
        "category": "Curiosity & Initiative",
        "question": "Kamu menemukan bahwa cara kerja tim saat ini kurang efisien.",
        "a": "Sampaikan usulan perbaikan meskipun belum diminta.",
        "b": "Pahami dulu alasan proses tersebut dibuat sebelum mengusulkan perubahan.",
    },
    {
        "id": 18,
        "category": "Curiosity & Initiative",
        "question": "Kamu mendapat tugas yang sangat mudah, tetapi berulang dan membosankan.",
        "a": "Selesaikan sesuai instruksi dan gunakan waktu untuk tugas lain.",
        "b": "Cari tahu apakah tugas tersebut bisa dibuat lebih efisien.",
    },
    {
        "id": 19,
        "category": "Collaboration & Openness",
        "question": "Rekan kerja memberikan solusi yang berbeda dari pendapatmu.",
        "a": "Jelaskan alasan mengapa solusi milikmu menurutmu lebih baik.",
        "b": "Tanyakan alasan dan pertimbangan di balik solusi rekan kerja tersebut.",
    },
    {
        "id": 20,
        "category": "Learning Orientation",
        "question": "Jika kamu memiliki satu jam untuk mempelajari sesuatu yang baru...",
        "a": "Pilih topik yang langsung berguna untuk pekerjaanmu saat ini.",
        "b": "Pilih topik yang menarik, meskipun belum tahu kapan akan berguna.",
    },
]

CATEGORIES = sorted(set(q["category"] for q in QUESTIONS))

# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "page": "Interview",
    "current_question": 0,
    "answers": {},
    "notes": {},
    "candidate_name": "",
    "candidate_position": "IT Executive",
    "interviewer_name": "",
    "interview_date": datetime.now().date().isoformat(),
    "interview_started": False,
    "interview_finished": False,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def reset_interview():
    for key, value in DEFAULT_STATE.items():
        st.session_state[key] = value


def get_answer(question_id):
    return st.session_state.answers.get(question_id)


def get_category_answers(category):
    result = []
    for q in QUESTIONS:
        if q["category"] == category and q["id"] in st.session_state.answers:
            result.append(st.session_state.answers[q["id"]])
    return result


def category_summary(category):
    answers = get_category_answers(category)

    if not answers:
        return "Belum ada jawaban"

    a_count = answers.count("A")
    b_count = answers.count("B")

    if a_count > b_count:
        return f"Pilihan A lebih dominan ({a_count} A / {b_count} B)"
    elif b_count > a_count:
        return f"Pilihan B lebih dominan ({a_count} A / {b_count} B)"
    else:
        return f"Pilihan seimbang ({a_count} A / {b_count} B)"


def generate_recommendations():
    recommendations = []

    # Logical Thinking
    logical = get_category_answers("Logical Thinking")
    if logical:
        recommendations.append(
            "Logical Thinking: Gali satu kasus troubleshooting dan minta kandidat menjelaskan "
            "hipotesis, data yang dibutuhkan, dan cara memverifikasi penyebab."
        )

    # Learning
    learning = (
        get_category_answers("Learning Ability")
        + get_category_answers("Learning Orientation")
    )
    if learning:
        recommendations.append(
            "Learning Ability: Tanyakan contoh ketika kandidat mempelajari sistem baru. "
            "Gali langkah belajar, sumber referensi, dan bagaimana menguji pemahaman."
        )

    # Creative
    creative = get_category_answers("Creative Problem Solving")
    if creative:
        recommendations.append(
            "Problem Solving: Berikan kasus dengan keterbatasan anggaran atau tools. "
            "Minta kandidat membandingkan dua solusi beserta risiko dan effort-nya."
        )

    # Decision
    decision = get_category_answers("Decision Making")
    if decision:
        recommendations.append(
            "Decision Making: Berikan skenario gangguan hotel. "
            "Minta kandidat menjelaskan prioritas, dampak operasional, dan komunikasi eskalasi."
        )

    # Practical
    practical = get_category_answers("Practical Judgment")
    if practical:
        recommendations.append(
            "Practical Judgment: Minta kandidat menjelaskan bagaimana menentukan pekerjaan "
            "sudah cukup baik untuk diserahkan, termasuk quality check dan deadline."
        )

    # Initiative
    initiative = get_category_answers("Curiosity & Initiative")
    if initiative:
        recommendations.append(
            "Initiative: Minta contoh perbaikan proses yang pernah dilakukan. "
            "Gali bagaimana kandidat memvalidasi manfaat dan melibatkan tim."
        )

    # Collaboration
    collaboration = get_category_answers("Collaboration & Openness")
    if collaboration:
        recommendations.append(
            "Collaboration: Tanyakan pengalaman ketika pendapat teknisnya berbeda dengan "
            "rekan atau atasan, serta bagaimana keputusan akhirnya dibuat."
        )

    return recommendations


def build_result():
    category_counts = {}

    for category in CATEGORIES:
        answers = get_category_answers(category)

        category_counts[category] = {
            "A": answers.count("A"),
            "B": answers.count("B"),
            "answered": len(answers),
        }

    result = {
        "application": "IT Smart Character Interview",
        "version": "1.0",
        "candidate": {
            "name": st.session_state.candidate_name,
            "position": st.session_state.candidate_position,
            "interviewer": st.session_state.interviewer_name,
            "interview_date": st.session_state.interview_date,
        },
        "answers": [
            {
                "question_id": q["id"],
                "category": q["category"],
                "question": q["question"],
                "choice": st.session_state.answers.get(q["id"]),
                "note": st.session_state.notes.get(q["id"], ""),
            }
            for q in QUESTIONS
        ],
        "category_summary": category_counts,
        "recommendations": generate_recommendations(),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }

    return result


def result_to_csv(result):
    output = io.StringIO()

    fieldnames = [
        "question_id",
        "category",
        "question",
        "choice",
        "note",
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for row in result["answers"]:
        writer.writerow(row)

    return output.getvalue()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## 🧠 IT Smart Interview")
    st.caption("Character & Thinking Interview")

    st.divider()

    st.markdown("### Candidate Profile")

    st.session_state.candidate_name = st.text_input(
        "Candidate Name",
        value=st.session_state.candidate_name,
        placeholder="Enter candidate name",
    )

    st.session_state.candidate_position = st.selectbox(
        "Position",
        [
            "IT Executive",
            "IT Engineer",
            "IT Support",
            "Data Analyst",
            "IT Trainee",
            "Other",
        ],
        index=[
            "IT Executive",
            "IT Engineer",
            "IT Support",
            "Data Analyst",
            "IT Trainee",
            "Other",
        ].index(st.session_state.candidate_position)
        if st.session_state.candidate_position
        in [
            "IT Executive",
            "IT Engineer",
            "IT Support",
            "Data Analyst",
            "IT Trainee",
            "Other",
        ]
        else 0,
    )

    st.session_state.interviewer_name = st.text_input(
        "Interviewer",
        value=st.session_state.interviewer_name,
        placeholder="Interviewer name",
    )

    st.session_state.interview_date = st.date_input(
        "Interview Date",
        value=datetime.fromisoformat(
            st.session_state.interview_date
        ).date(),
    ).isoformat()

    st.divider()

    answered_count = len(st.session_state.answers)
    total_count = len(QUESTIONS)

    st.markdown("### Progress")
    st.progress(answered_count / total_count)
    st.caption(f"{answered_count} / {total_count} answered")

    st.divider()

    if st.button("🏠 Interview", use_container_width=True):
        st.session_state.page = "Interview"

    if st.button("📊 Results", use_container_width=True):
        st.session_state.page = "Results"

    if st.button("🔄 New Interview", use_container_width=True):
        reset_interview()
        st.rerun()

# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">IT Smart Character Interview</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">Rapid A/B interview • Logical thinking • Learning • Decision making</div>',
    unsafe_allow_html=True,
)

# ============================================================
# INTERVIEW PAGE
# ============================================================

if st.session_state.page == "Interview":

    current_index = st.session_state.current_question
    question = QUESTIONS[current_index]
    question_id = question["id"]

    st.progress((current_index + 1) / len(QUESTIONS))

    st.markdown(
        f"""
        <div class="question-card">
            <div class="question-number">
                QUESTION {current_index + 1} OF {len(QUESTIONS)}
                &nbsp; • &nbsp; {question["category"]}
            </div>
            <div class="question-title">
                {question["question"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    current_choice = get_answer(question_id)

    st.markdown('<div class="choice-label">Candidate Choice</div>', unsafe_allow_html=True)

    choice = st.radio(
        "Select candidate answer",
        options=["A", "B"],
        format_func=lambda x: (
            f"A — {question['a']}"
            if x == "A"
            else f"B — {question['b']}"
        ),
        index=["A", "B"].index(current_choice)
        if current_choice in ["A", "B"]
        else None,
        key=f"choice_{question_id}",
        label_visibility="collapsed",
    )

    if choice:
        st.session_state.answers[question_id] = choice

    st.markdown("#### Interviewer Notes")

    note = st.text_area(
        "Write observations or candidate's reasoning",
        value=st.session_state.notes.get(question_id, ""),
        placeholder=(
            "Example: Explains assumptions clearly, asks for logs, "
            "considers business impact..."
        ),
        height=110,
        key=f"note_{question_id}",
        label_visibility="collapsed",
    )

    st.session_state.notes[question_id] = note

    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if current_index > 0:
            if st.button("← Previous", use_container_width=True):
                st.session_state.current_question -= 1
                st.rerun()

    with col2:
        if st.button(
            "Finish Interview" if current_index == len(QUESTIONS) - 1 else "Save & Continue →",
            use_container_width=True,
            type="primary",
        ):
            if not choice:
                st.warning("Please select A or B before continuing.")
            else:
                if current_index < len(QUESTIONS) - 1:
                    st.session_state.current_question += 1
                    st.rerun()
                else:
                    st.session_state.interview_finished = True
                    st.session_state.page = "Results"
                    st.rerun()

    with col3:
        if st.button("Results →", use_container_width=True):
            st.session_state.page = "Results"
            st.rerun()

# ============================================================
# RESULTS PAGE
# ============================================================

elif st.session_state.page == "Results":

    st.markdown("## 📊 Interview Results")

    answered_count = len(st.session_state.answers)
    total_count = len(QUESTIONS)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Answered", f"{answered_count}/{total_count}")

    with col2:
        st.metric(
            "A Choices",
            sum(1 for a in st.session_state.answers.values() if a == "A"),
        )

    with col3:
        st.metric(
            "B Choices",
            sum(1 for a in st.session_state.answers.values() if a == "B"),
        )

    st.divider()

    st.markdown("### Candidate")

    candidate_col1, candidate_col2 = st.columns(2)

    with candidate_col1:
        st.write(f"**Name:** {st.session_state.candidate_name or 'Not specified'}")
        st.write(f"**Position:** {st.session_state.candidate_position}")

    with candidate_col2:
        st.write(f"**Interviewer:** {st.session_state.interviewer_name or 'Not specified'}")
        st.write(f"**Date:** {st.session_state.interview_date}")

    st.divider()

    st.markdown("### Category Overview")

    for category in CATEGORIES:
        answers = get_category_answers(category)

        a_count = answers.count("A")
        b_count = answers.count("B")

        with st.expander(category, expanded=True):
            col_a, col_b, col_c = st.columns(3)

            with col_a:
                st.metric("Answered", len(answers))

            with col_b:
                st.metric("A", a_count)

            with col_c:
                st.metric("B", b_count)

            st.caption(category_summary(category))

    st.divider()

    st.markdown("### 🔍 Interviewer Recommendation")

    st.info(
        "This section identifies useful areas for follow-up. "
        "A/B choices alone do not establish intelligence, character, "
        "or job suitability."
    )

    recommendations = generate_recommendations()

    if recommendations:
        for index, recommendation in enumerate(recommendations, start=1):
            st.markdown(f"**{index}.** {recommendation}")
    else:
        st.warning("Complete more questions to generate recommendations.")

    st.divider()

    st.markdown("### 📝 Interview Notes")

    for q in QUESTIONS:
        answer = st.session_state.answers.get(q["id"])
        note = st.session_state.notes.get(q["id"], "")

        if answer or note:
            with st.expander(
                f"Q{q['id']} — {q['category']} — Choice: {answer or '-'}"
            ):
                st.write(q["question"])

                if answer == "A":
                    st.write(f"**A:** {q['a']}")
                elif answer == "B":
                    st.write(f"**B:** {q['b']}")

                st.write(f"**Interviewer Note:** {note or '-'}")

    st.divider()

    result = build_result()

    st.markdown("### 📥 Export Results")

    json_data = json.dumps(result, indent=2, ensure_ascii=False)
    csv_data = result_to_csv(result)

    col_json, col_csv = st.columns(2)

    with col_json:
        st.download_button(
            "⬇️ Download JSON",
            data=json_data,
            file_name=(
                f"interview_"
                f"{st.session_state.candidate_name or 'candidate'}_"
                f"{st.session_state.interview_date}.json"
            ),
            mime="application/json",
            use_container_width=True,
        )

    with col_csv:
        st.download_button(
            "⬇️ Download CSV",
            data=csv_data,
            file_name=(
                f"interview_"
                f"{st.session_state.candidate_name or 'candidate'}_"
                f"{st.session_state.interview_date}.csv"
            ),
            mime="text/csv",
            use_container_width=True,
        )

    st.divider()

    if st.button("← Back to Interview", use_container_width=True):
        st.session_state.page = "Interview"
        st.rerun()
