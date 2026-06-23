import streamlit as st
from io import BytesIO
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="Interview Tracker",
    page_icon="📋",
    layout="wide"
)

# YOUR GOOGLE SHEET
GOOGLE_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1cGGZbxaqICQYL3swSLlU56qRDFCnRpaUIoUIkbKygcI/edit?rm=minimal"
)

# =====================================================
# PDF FUNCTION
# =====================================================

def generate_pdf(data):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    content = []

    title = Paragraph(
        "Candidate Interview Assessment Report",
        styles["Title"]
    )

    content.append(title)
    content.append(Spacer(1, 20))

    candidate_table = Table(
        [
            ["Candidate Name", data["candidate_name"]],
            ["Position Applied", data["position"]],
            ["Interview Date", data["date"]],
            ["Recommendation", data["recommendation"]],
        ],
        colWidths=[170, 300],
    )

    candidate_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ]
        )
    )

    content.append(candidate_table)
    content.append(Spacer(1, 20))

    score_table = Table(
        [
            ["Evaluation Area", "Score / 10"],
            ["Communication", data["communication"]],
            ["Technical Skills", data["technical"]],
            ["Problem Solving", data["problem_solving"]],
            ["Confidence", data["confidence"]],
            ["Learning Ability", data["learning"]],
            ["Team Fit", data["team_fit"]],
        ]
    )

    score_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ]
        )
    )

    content.append(score_table)
    content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            f"<b>Strengths</b><br/>{data['strengths']}",
            styles["BodyText"],
        )
    )

    content.append(Spacer(1, 10))

    content.append(
        Paragraph(
            f"<b>Areas of Improvement</b><br/>{data['improvements']}",
            styles["BodyText"],
        )
    )

    content.append(Spacer(1, 10))

    content.append(
        Paragraph(
            f"<b>Interview Summary</b><br/>{data['summary']}",
            styles["BodyText"],
        )
    )

    content.append(Spacer(1, 10))

    content.append(
        Paragraph(
            f"<b>Final Recommendation:</b> {data['recommendation']}",
            styles["BodyText"],
        )
    )

    doc.build(content)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf

# =====================================================
# HEADER
# =====================================================

st.title("📋 Interview Candidate Tracker")

tab1, tab2 = st.tabs(
    [
        "Candidate Tracker",
        "Interview Report PDF",
    ]
)

# =====================================================
# TAB 1
# =====================================================

with tab1:

    st.subheader("Candidate Tracker")

    st.info(
        "Manage candidates directly in the Google Sheet."
    )

    st.components.v1.iframe(
        GOOGLE_SHEET_URL,
        height=900,
        scrolling=True,
    )

# =====================================================
# TAB 2
# =====================================================

with tab2:

    st.subheader("Interview Assessment Form")

    col1, col2 = st.columns(2)

    with col1:
        candidate_name = st.text_input(
            "Candidate Name"
        )

    with col2:
        position = st.text_input(
            "Position Applied"
        )

    interview_date = st.date_input(
        "Interview Date"
    )

    st.markdown("### Evaluation Scores")

    communication = st.slider(
        "Communication",
        1,
        10,
        5,
    )

    technical = st.slider(
        "Technical Skills",
        1,
        10,
        5,
    )

    problem_solving = st.slider(
        "Problem Solving",
        1,
        10,
        5,
    )

    confidence = st.slider(
        "Confidence",
        1,
        10,
        5,
    )

    learning = st.slider(
        "Learning Ability",
        1,
        10,
        5,
    )

    team_fit = st.slider(
        "Team Fit",
        1,
        10,
        5,
    )

    strengths = st.text_area(
        "Strengths",
        height=120,
    )

    improvements = st.text_area(
        "Areas of Improvement",
        height=120,
    )

    summary = st.text_area(
        "Interview Summary",
        height=150,
    )

    recommendation = st.selectbox(
        "Recommendation",
        [
            "Strong Hire",
            "Hire",
            "Hold",
            "Reject",
        ],
    )

    if st.button(
        "Generate Interview PDF",
        use_container_width=True,
    ):

        pdf_data = {
            "candidate_name": candidate_name,
            "position": position,
            "date": str(interview_date),
            "communication": communication,
            "technical": technical,
            "problem_solving": problem_solving,
            "confidence": confidence,
            "learning": learning,
            "team_fit": team_fit,
            "strengths": strengths,
            "improvements": improvements,
            "summary": summary,
            "recommendation": recommendation,
        }

        pdf_file = generate_pdf(pdf_data)

        st.success(
            "PDF generated successfully."
        )

        filename = (
            candidate_name.strip().replace(" ", "_")
            or "Candidate"
        )

        st.download_button(
            label="⬇ Download Interview Report",
            data=pdf_file,
            file_name=f"{filename}_Interview_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )