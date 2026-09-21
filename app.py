
import streamlit as st
import pandas as pd
import json
from datetime import datetime

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="IT Smart Character Interview",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f5f7fa;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .question-number {
        color: #64748b;
        font-size: 14px;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    .question-title {
        font-size: 34px;
        font-weight: 700;
        line-height: 1.3;
        color: #0f172a;
        text-align: center;
        margin: 20px 0 30px 0;
    }

    .option-card {
        background-color: white;
        border: 1px solid #dbe2ea;
        border-radius: 14px;
        padding: 24px;
        min-height: 130px;
        display: flex;
        align-items: center;
        font-size: 21px;
        line-height: 1.5;
        color: #1e293b;
        margin-bottom: 12px;
    }

    .interview-header {
        background-color: white;
        border-radius: 16px;
        padding: 20px 25px;
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }

    .result-card {
        background-color: white;
        border-radius: 14px;
        padding: 22px;
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
    }

    .small-label {
        color: #64748b;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
    }

    div[data-testid="stRadio"] label {
        font-size: 18px;
    }

    .stButton button {
        border-radius: 10px;
        min-height: 44px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# QUESTION BANK
# ============================================================

QUESTIONS = [
    {
        "id": 1,
        "category": "Logical Thinking",
        "question": "Saat menghadapi masalah baru, kamu lebih memilih...",
        "a": "Langsung mencoba beberapa solusi untuk melihat hasilnya.",
        "b": "Mengumpulkan informasi dan memahami penyebab sebelum bertindak."
    },
    {
        "id": 2,
        "category": "Logical Thinking",
        "question": "Jika terjadi gangguan sistem, kamu cenderung...",
        "a": "Fokus pada penyebab yang paling mungkin terjadi.",
        "b": "Memeriksa beberapa kemungkinan penyebab secara sistematis."
    },
    {
        "id": 3,
        "category": "Logical Thinking",
        "question": "Ketika masalah muncul setelah perubahan sistem, kamu akan...",
        "a": "Memeriksa perubahan terakhir yang dilakukan.",
        "b": "Melakukan pemeriksaan dasar secara menyeluruh."
    },
    {
        "id": 4,
        "category": "Logical Thinking",
        "question": "Ketika solusi pertama belum berhasil, kamu lebih memilih...",
        "a": "Memodifikasi solusi tersebut sampai berhasil.",
        "b": "Meninjau kembali asumsi dan mencoba hipotesis lain."
    },
    {
        "id": 5,
        "category": "Learning & Curiosity",
        "question": "Saat mempelajari tools baru, kamu cenderung...",
        "a": "Mengeksplorasi dan mencari tahu secara mandiri.",
        "b": "Membaca dokumentasi atau bertanya kepada orang berpengalaman."
    },
    {
        "id": 6,
        "category": "Learning & Curiosity",
        "question": "Saat mempelajari sebuah sistem, hal yang paling ingin kamu pahami adalah...",
        "a": "Cara sistem tersebut bekerja di balik layar.",
        "b": "Cara menggunakan sistem untuk menyelesaikan pekerjaan."
    },
    {
        "id": 7,
        "category": "Learning & Curiosity",
        "question": "Jika ada metode baru untuk menyelesaikan pekerjaan, kamu akan...",
        "a": "Menggunakan metode lama yang sudah terbukti.",
        "b": "Mempelajari metode baru untuk melihat apakah lebih efektif."
    },
    {
        "id": 8,
        "category": "Learning & Curiosity",
        "question": "Ketika muncul pertanyaan saat bekerja, kamu lebih memilih...",
        "a": "Mencatatnya dan mempelajarinya nanti.",
        "b": "Langsung bertanya agar bisa memahami saat itu juga."
    },
    {
        "id": 9,
        "category": "Creative Problem Solving",
        "question": "Saat prosedur standar tidak menyelesaikan masalah, kamu akan...",
        "a": "Mencari alternatif di luar prosedur standar.",
        "b": "Memeriksa prosedur standar secara lebih mendalam."
    },
    {
        "id": 10,
        "category": "Creative Problem Solving",
        "question": "Untuk kebutuhan sistem baru, kamu lebih tertarik pada...",
        "a": "Solusi open-source yang bisa disesuaikan.",
        "b": "Solusi komersial yang matang dan memiliki dukungan vendor."
    },
    {
        "id": 11,
        "category": "Creative Problem Solving",
        "question": "Jika menemukan pekerjaan berulang, kamu akan...",
        "a": "Mencari cara untuk mengotomatisasi pekerjaan tersebut.",
        "b": "Membuat prosedur manual yang lebih terstandarisasi."
    },
    {
        "id": 12,
        "category": "Calmness & Decision Making",
        "question": "Guest Wi-Fi mengalami gangguan besar. Kamu akan...",
        "a": "Segera melakukan tindakan untuk memulihkan layanan.",
        "b": "Memahami dampak dan melakukan pemeriksaan singkat terlebih dahulu."
    },
    {
        "id": 13,
        "category": "Calmness & Decision Making",
        "question": "Ketika diminta memberikan solusi dengan cepat, kamu akan...",
        "a": "Memberikan solusi sementara berdasarkan informasi yang tersedia.",
        "b": "Mengumpulkan informasi penting terlebih dahulu."
    },
    {
        "id": 14,
        "category": "Calmness & Decision Making",
        "question": "Jika pekerjaan belum selesai menjelang akhir jam kerja, kamu akan...",
        "a": "Tetap melanjutkan pekerjaan sampai selesai.",
        "b": "Mendokumentasikan status, mengomunikasikan kondisi, dan membuat rencana lanjutan."
    },
    {
        "id": 15,
        "category": "Practical Execution",
        "question": "Ketika hasil pekerjaan sudah memenuhi requirement, kamu akan...",
        "a": "Menyelesaikannya dan melanjutkan pekerjaan berikutnya.",
        "b": "Melakukan penyempurnaan lebih lanjut agar hasilnya lebih sempurna."
    },
    {
        "id": 16,
        "category": "Practical Execution",
        "question": "Jika menemukan kesalahan kecil pada data, kamu akan...",
        "a": "Memperbaiki kesalahan tersebut dan melanjutkan pekerjaan.",
        "b": "Mencari tahu apakah ada masalah yang lebih luas pada sumber data."
    },
    {
        "id": 17,
        "category": "Initiative",
        "question": "Jika menemukan cara untuk meningkatkan efisiensi pekerjaan, kamu akan...",
        "a": "Mengusulkan perbaikan meskipun tidak diminta.",
        "b": "Memahami alasan di balik proses yang berjalan terlebih dahulu."
    },
    {
        "id": 18,
        "category": "Initiative",
        "question": "Setelah menyelesaikan pekerjaan rutin lebih cepat, kamu akan...",
        "a": "Menggunakan waktu yang tersisa untuk pekerjaan lain.",
        "b": "Mencari cara agar pekerjaan rutin tersebut bisa lebih efisien."
    },
    {
        "id": 19,
        "category": "Collaboration",
        "question": "Ketika solusi kamu berbeda dengan rekan kerja, kamu akan...",
        "a": "Menjelaskan mengapa solusi kamu lebih baik.",
        "b": "Menanyakan alasan dan pertimbangan di balik solusi rekan kerja."
    },
    {
        "id": 20,
        "category": "Learning Orientation",
        "question": "Jika memiliki waktu untuk belajar, kamu cenderung memilih...",
        "a": "Topik yang langsung berguna untuk pekerjaan.",
        "b": "Topik menarik yang belum tentu langsung memiliki kegunaan."
    }
]

# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "page": "setup",
    "candidate_name": "",
    "candidate_position": "IT Executive",
    "interview_date": datetime.now().date(),
    "current_question": 0,
    "answers": {},
    "notes": {},
    "completed": False
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


def save_answer(question_id, answer):
    st.session_state.answers[question_id] = answer


def get_answer_label(answer):
    if answer == "A":
        return "A"
    if answer == "B":
        return "B"
    return "-"


def calculate_category_summary():
    summary = {}

    for question in QUESTIONS:
        category = question["category"]
        answer = st.session_state.answers.get(question["id"])

        if category not in summary:
            summary[category] = {
                "total": 0,
                "answered": 0,
                "A": 0,
                "B": 0
            }

        summary[category]["total"] += 1

        if answer in ["A", "B"]:
            summary[category]["answered"] += 1
            summary[category][answer] += 1

    return summary


def generate_observations():
    summary = calculate_category_summary()
    observations = []

    for category, values in summary.items():
        if values["answered"] == 0:
            continue

        if values["A"] > values["B"]:
            tendency = "lebih sering memilih opsi A"
        elif values["B"] > values["A"]:
            tendency = "lebih sering memilih opsi B"
        else:
            tendency = "memiliki pilihan yang relatif seimbang"

        observations.append({
            "Category": category,
            "Answered": values["answered"],
            "Option A": values["A"],
            "Option B": values["B"],
            "Observation": tendency
        })

    return observations


def generate_recommendation():
    summary = calculate_category_summary()

    notes = []

    for category, values in summary.items():
        if values["answered"] == 0:
            continue

        if values["A"] == values["B"]:
            notes.append(
                f"{category}: pilihan relatif seimbang. "
                "Perlu pendalaman melalui pertanyaan lanjutan."
            )
        elif values["A"] > values["B"]:
            notes.append(
                f"{category}: kandidat lebih sering memilih opsi A. "
                "Validasi kecenderungan ini melalui contoh pengalaman nyata."
            )
        else:
            notes.append(
                f"{category}: kandidat lebih sering memilih opsi B. "
                "Validasi kecenderungan ini melalui contoh pengalaman nyata."
            )

    return notes


def create_export_data():
    rows = []

    for question in QUESTIONS:
        question_id = question["id"]
        answer = st.session_state.answers.get(question_id)

        rows.append({
            "Question": question_id,
            "Category": question["category"],
            "Question Text": question["question"],
            "Option A": question["a"],
            "Option B": question["b"],
            "Selected Answer": answer or "",
            "Interviewer Note": st.session_state.notes.get(question_id, "")
        })

    return rows


# ============================================================
# SETUP PAGE
# ============================================================

def render_setup():
    st.markdown(
        """
        <div class="interview-header">
            <div class="small-label">IT Recruitment</div>
            <h1>🧠 IT Smart Character Interview</h1>
            <p>
                Interview berbasis pertanyaan A/B untuk mengeksplorasi
                pola berpikir, cara mengambil keputusan, dan karakter kerja.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info(
        "Gunakan aplikasi ini saat screen sharing. "
        "Interviewer membacakan pertanyaan dan mencatat jawaban kandidat."
    )

    with st.form("setup_form"):
        candidate_name = st.text_input(
            "Nama Kandidat",
            value=st.session_state.candidate_name,
            placeholder="Masukkan nama kandidat"
        )

        candidate_position = st.selectbox(
            "Posisi",
            [
                "IT Executive",
                "IT Supervisor",
                "Assistant IT Manager",
                "IT Manager",
                "Other"
            ],
            index=0
        )

        interview_date = st.date_input(
            "Tanggal Interview",
            value=st.session_state.interview_date
        )

        st.markdown("---")

        st.write("**Format Interview**")
        st.write("- 20 pertanyaan A/B")
        st.write("- Kandidat menjawab secara lisan")
        st.write("- Tidak ada jawaban benar atau salah")
        st.write("- Interviewer mencatat konteks dan penjelasan kandidat")

        submitted = st.form_submit_button(
            "Mulai Interview",
            type="primary",
            use_container_width=True
        )

        if submitted:
            if not candidate_name.strip():
                st.error("Nama kandidat wajib diisi.")
            else:
                st.session_state.candidate_name = candidate_name.strip()
                st.session_state.candidate_position = candidate_position
                st.session_state.interview_date = interview_date
                st.session_state.page = "interview"
                st.session_state.current_question = 0
                st.session_state.completed = False
                st.rerun()


# ============================================================
# INTERVIEW PAGE
# ============================================================

def render_interview():
    question_index = st.session_state.current_question
    question = QUESTIONS[question_index]
    question_id = question["id"]

    answered_count = len(st.session_state.answers)
    total_questions = len(QUESTIONS)

    st.markdown(
        f"""
        <div class="interview-header">
            <div class="small-label">Candidate</div>
            <h2>{st.session_state.candidate_name}</h2>
            <p>{st.session_state.candidate_position}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    progress = answered_count / total_questions
    st.progress(progress)

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(
            f'<div class="question-number">'
            f'Question {question_index + 1} of {total_questions}'
            f'</div>',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f'<div style="text-align:right;color:#64748b;">'
            f'Answered: {answered_count}/{total_questions}'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        f'<div class="question-title">{question["question"]}</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="option-card"><b>A.&nbsp;&nbsp;</b>{question["a"]}</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="option-card"><b>B.&nbsp;&nbsp;</b>{question["b"]}</div>',
        unsafe_allow_html=True
    )

    st.markdown("### Catat Jawaban Kandidat")

    current_answer = st.session_state.answers.get(question_id)

    selected_answer = st.radio(
        "Pilihan kandidat",
        options=["A", "B"],
        index=["A", "B"].index(current_answer)
        if current_answer in ["A", "B"] else None,
        horizontal=True,
        key=f"answer_{question_id}",
        label_visibility="collapsed"
    )

    if selected_answer:
        save_answer(question_id, selected_answer)

    current_note = st.session_state.notes.get(question_id, "")

    note = st.text_area(
        "Catatan interviewer",
        value=current_note,
        placeholder=(
            "Catat alasan kandidat, contoh pengalaman, "
            "atau observasi penting..."
        ),
        height=110,
        key=f"note_{question_id}"
    )

    st.session_state.notes[question_id] = note

    st.markdown("---")

    nav1, nav2, nav3 = st.columns([1, 1, 1])

    with nav1:
        if st.button(
            "← Previous",
            disabled=question_index == 0,
            use_container_width=True
        ):
            st.session_state.current_question -= 1
            st.rerun()

    with nav2:
        if st.button(
            "Reset Interview",
            use_container_width=True
        ):
            reset_interview()
            st.rerun()

    with nav3:
        if question_index < total_questions - 1:
            if st.button(
                "Next →",
                type="primary",
                use_container_width=True
            ):
                st.session_state.current_question += 1
                st.rerun()
        else:
            if st.button(
                "Finish Interview",
                type="primary",
                use_container_width=True
            ):
                st.session_state.completed = True
                st.session_state.page = "results"
                st.rerun()

    st.caption(
        "Catatan: pilihan A/B digunakan sebagai bahan diskusi, "
        "bukan sebagai keputusan otomatis."
    )


# ============================================================
# RESULTS PAGE
# ============================================================

def render_results():
    st.markdown(
        """
        <div class="interview-header">
            <div class="small-label">Interview Completed</div>
            <h1>📊 Interview Result</h1>
            <p>Ringkasan untuk interviewer</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.success("Interview telah selesai.")

    info1, info2, info3 = st.columns(3)

    with info1:
        st.metric("Candidate", st.session_state.candidate_name)

    with info2:
        st.metric("Position", st.session_state.candidate_position)

    with info3:
        st.metric(
            "Answered",
            f"{len(st.session_state.answers)}/{len(QUESTIONS)}"
        )

    st.markdown("## Ringkasan Pilihan")

    observations = generate_observations()

    if observations:
        observation_df = pd.DataFrame(observations)
        st.dataframe(
            observation_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Belum ada jawaban yang tersimpan.")

    st.markdown("## Interviewer Notes")

    for question in QUESTIONS:
        question_id = question["id"]
        answer = st.session_state.answers.get(question_id, "-")
        note = st.session_state.notes.get(question_id, "")

        with st.expander(
            f"Question {question_id} | Answer: {answer}"
        ):
            st.write(question["question"])
            st.write(f"**A:** {question['a']}")
            st.write(f"**B:** {question['b']}")

            if note:
                st.write("**Note:**")
                st.write(note)
            else:
                st.caption("Tidak ada catatan.")

    st.markdown("## Recommendation untuk Interviewer")

    st.warning(
        "Recommendation berikut adalah indikasi awal berdasarkan pola "
        "pilihan, bukan keputusan otomatis atau penilaian final."
    )

    recommendations = generate_recommendation()

    for recommendation in recommendations:
        st.write(f"- {recommendation}")

    st.markdown("---")

    export_rows = create_export_data()

    export_payload = {
        "candidate_name": st.session_state.candidate_name,
        "candidate_position": st.session_state.candidate_position,
        "interview_date": str(st.session_state.interview_date),
        "completed_at": datetime.now().isoformat(),
        "answers": export_rows
    }

    json_data = json.dumps(
        export_payload,
        indent=2,
        ensure_ascii=False
    )

    csv_data = pd.DataFrame(export_rows).to_csv(index=False)

    download1, download2, action = st.columns(3)

    with download1:
        st.download_button(
            "Download JSON",
            data=json_data,
            file_name=(
                f"interview_"
                f"{st.session_state.candidate_name.replace(' ', '_')}.json"
            ),
            mime="application/json",
            use_container_width=True
        )

    with download2:
        st.download_button(
            "Download CSV",
            data=csv_data,
            file_name=(
                f"interview_"
                f"{st.session_state.candidate_name.replace(' ', '_')}.csv"
            ),
            mime="text/csv",
            use_container_width=True
        )

    with action:
        if st.button(
            "Interview Baru",
            use_container_width=True
        ):
            reset_interview()
            st.rerun()


# ============================================================
# MAIN ROUTER
# ============================================================

if st.session_state.page == "setup":
    render_setup()

elif st.session_state.page == "interview":
    render_interview()

elif st.session_state.page == "results":
    render_results()
