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
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Interview Management Portal",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

/* Hide Streamlit UI */
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

.block-container{
    padding-top:1rem;
    padding-bottom:1rem;
    max-width:1400px;
}

/* Buttons */
.stButton button{
    background-color:#00ABB2;
    color:white;
    border:none;
    border-radius:10px;
    height:3rem;
    font-weight:600;
}

.stButton button:hover{
    background-color:#00929a;
    color:white;
}

/* Download Button */
.stDownloadButton button{
    background-color:#00ABB2;
    color:white;
    border:none;
    border-radius:10px;
    height:3rem;
    font-weight:600;
}

/* Radio Buttons */
div[role="radiogroup"]{
    gap:20px;
}

/* Section Cards */
.card{
    background:white;
    padding:20px;
    border-radius:15px;
    border:1px solid #E5E7EB;
    box-shadow:0 2px 8px rgba(0,0,0,0.05);
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# GOOGLE SHEET
# =====================================================

GOOGLE_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1cGGZbxaqICQYL3swSLlU56qRDFCnRpaUIoUIkbKygcI/edit?rm=minimal"
)

# =====================================================
# PDF GENERATOR
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
            ["Role", data["position"]],
            ["Interview Date", data["date"]],
            ["Recommendation", data["recommendation"]],
        ],
        colWidths=[180, 300],
    )

    candidate_table.setStyle(
        TableStyle([
            ("GRID", (0,0), (-1,-1), 1, colors.black),
            ("BACKGROUND", (0,0), (0,-1), colors.lightgrey),
        ])
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
        TableStyle([
            ("GRID", (0,0), (-1,-1), 1, colors.black),
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ])
    )

    content.append(score_table)
    content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            f"<b>Strengths</b><br/>{data['strengths']}",
            styles["BodyText"]
        )
    )

    content.append(Spacer(1, 10))

    content.append(
        Paragraph(
            f"<b>Areas of Improvement</b><br/>{data['improvements']}",
            styles["BodyText"]
        )
    )

    content.append(Spacer(1, 10))

    content.append(
        Paragraph(
            f"<b>Interview Summary</b><br/>{data['summary']}",
            styles["BodyText"]
        )
    )

    content.append(Spacer(1, 10))

    content.append(
        Paragraph(
            f"<b>Final Recommendation:</b> {data['recommendation']}",
            styles["BodyText"]
        )
    )

    doc.build(content)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf

# =====================================================
# HEADER
# =====================================================

st.markdown("""
<h1 style='text-align:center;color:#00ABB2;margin-bottom:0;'>
Interview Management Portal
</h1>

<p style='text-align:center;color:gray;margin-top:0;'>
Candidate Tracking & Interview Assessment
</p>
""", unsafe_allow_html=True)

st.divider()

# =====================================================
# NAVIGATION
# =====================================================

page = st.radio(
    "",
    ["📋 Candidate Tracker", "📝 Interview Report"],
    horizontal=True
)

# =====================================================
# TRACKER PAGE
# =====================================================

if page == "📋 Candidate Tracker":

    st.markdown("### Candidate Tracker")

    st.caption(
        "Manage candidates directly through the shared Google Sheet."
    )

    st.components.v1.iframe(
        GOOGLE_SHEET_URL,
        height=700,
        scrolling=True
    )

# =====================================================
# PDF PAGE
# =====================================================

if page == "📝 Interview Report":

    st.markdown("### Interview Assessment Form")

    # Candidate Info

    c1, c2, c3 = st.columns(3)

    with c1:
        candidate_name = st.text_input("Candidate Name")

    with c2:
        position = st.text_input("Role")

    with c3:
        interview_date = st.date_input("Interview Date")

    st.divider()

    st.markdown("### Evaluation Scores")

    # Ratings Grid

    col1, col2, col3 = st.columns(3)

    with col1:
        communication = st.slider(
            "Communication", 1, 10, 5
        )

        confidence = st.slider(
            "Confidence", 1, 10, 5
        )

    with col2:
        technical = st.slider(
            "Technical Skills", 1, 10, 5
        )

        learning = st.slider(
            "Learning Ability", 1, 10, 5
        )

    with col3:
        problem_solving = st.slider(
            "Problem Solving", 1, 10, 5
        )

        team_fit = st.slider(
            "Team Fit", 1, 10, 5
        )

    st.divider()

    feedback1, feedback2 = st.columns(2)

    with feedback1:
        strengths = st.text_area(
            "Strengths",
            height=120
        )

    with feedback2:
        improvements = st.text_area(
            "Areas of Improvement",
            height=120
        )

    summary = st.text_area(
        "Interview Summary",
        height=100
    )

    recommendation = st.radio(
        "Recommendation",
        ["Strong Hire", "Hire", "Hold", "Reject"],
        horizontal=True
    )

    st.divider()

    generate = st.button(
        "📄 Generate Interview Report",
        use_container_width=True
    )

    if generate:

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
            "Interview report generated successfully."
        )

        filename = (
            candidate_name.strip().replace(" ", "_")
            if candidate_name
            else "Candidate"
        )

        st.download_button(
            label="⬇ Download PDF",
            data=pdf_file,
            file_name=f"{filename}_Interview_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )