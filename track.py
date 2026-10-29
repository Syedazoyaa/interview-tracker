import streamlit as st
from io import BytesIO
from urllib.request import urlopen
import pandas as pd
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
    page_title="Interview Portal",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# CSS
# =====================================================

st.markdown("""
<style>

/* Hide Streamlit stuff */
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

[data-testid="stToolbar"]{
    display:none;
}

/* Reduce top spacing */
.block-container{
    padding-top:0.5rem !important;
    padding-bottom:0rem !important;
    padding-left:1.5rem !important;
    padding-right:1.5rem !important;
    max-width:100% !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{
    gap:10px;
}

.stTabs [data-baseweb="tab"]{
    height:50px;
    border-radius:8px;
    padding-left:20px;
    padding-right:20px;
    font-weight:600;
}

/* Buttons */
.stButton button,
.stDownloadButton button{
    background:#00ABB2;
    color:white;
    border:none;
    border-radius:10px;
    height:48px;
    font-weight:600;
    width:100%;
}

.stButton button:hover,
.stDownloadButton button:hover{
    background:#00939A;
    color:white;
}

/* Remove excess margins */
h1,h2,h3{
    margin-top:0 !important;
}

/* Radio spacing */
div[role="radiogroup"]{
    gap:15px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# GOOGLE SHEET
# =====================================================

GOOGLE_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1cGGZbxaqICQYL3swSLlU56qRDFCnRpaUIoUIkbKygcI/edit?usp=sharing"
)

# CSV export endpoint of the candidate tracker sheet page (used for the live table)
SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1cGGZbxaqICQYL3swSLlU56qRDFCnRpaUIoUIkbKygcI/export?format=csv&gid=0"
)

@st.cache_data(ttl=300)  # refresh sheet data every 5 minutes
def load_sheet_data():
    with urlopen(SHEET_CSV_URL, timeout=30) as response:
        csv_bytes = response.read()
    df = pd.read_csv(BytesIO(csv_bytes))

    # Clean up empty rows/stray whitespace and drop trailing empty columns
    df = df.dropna(how="all")
    df = df.drop(columns=[c for c in df.columns if str(c).startswith("Unnamed")])
    df.columns = [str(c).strip() for c in df.columns]
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip().replace({"nan": ""})

    return df

def show_sheet_page():
    st.markdown("### 📊 Candidate Sheet Data")
    st.caption(f"Live view of the tracker sheet — auto-refreshes every 5 minutes. "
               f"[Open the full sheet in Google Sheets]({GOOGLE_SHEET_URL})")

    try:
        df = load_sheet_data()
    except Exception as e:
        st.error(f"Could not load the sheet: {e}")
        st.link_button("🔗 Open Google Sheet", GOOGLE_SHEET_URL)
        return

    # Quick summary metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Candidates", len(df))
    with m2:
        done = df["Status"].str.contains("done", case=False, na=False).sum()
        st.metric("Done", int(done))
    with m3:
        ghosted = df["Status"].str.contains("ghost", case=False, na=False).sum()
        st.metric("Ghosted", int(ghosted))
    with m4:
        pending = df["Status"].isna().sum() + (df["Status"] == "").sum()
        st.metric("Pending", int(pending))

    st.markdown("")

    search = st.text_input("🔎 Search candidate, status or comment")
    if search:
        mask = df.apply(
            lambda row: row.astype(str).str.contains(search, case=False).any(),
            axis=1,
        )
        df = df[mask]

    st.dataframe(
        df,
        use_container_width=True,
        height=620,
        column_config={
            "Meet Link": st.column_config.LinkColumn("Meet Link"),
            "Status": st.column_config.TextColumn("Status"),
        },
    )

# =====================================================
# PDF FUNCTION
# =====================================================

def generate_pdf(data):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    content = []

    content.append(
        Paragraph(
            "Candidate Interview Assessment Report",
            styles["Title"]
        )
    )

    content.append(Spacer(1, 15))

    candidate_table = Table([
        ["Candidate Name", data["candidate_name"]],
        ["Role", data["position"]],
        ["Interview Date", data["date"]],
        ["Recommendation", data["recommendation"]],
    ])

    candidate_table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),1,colors.black),
        ("BACKGROUND",(0,0),(0,-1),colors.lightgrey)
    ]))

    content.append(candidate_table)

    content.append(Spacer(1,15))

    score_table = Table([
        ["Criteria","Score"],
        ["Communication", data["communication"]],
        ["Technical Skills", data["technical"]],
        ["Problem Solving", data["problem_solving"]],
        ["Confidence", data["confidence"]],
        ["Learning Ability", data["learning"]],
        ["Team Fit", data["team_fit"]],
    ])

    score_table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),1,colors.black),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey)
    ]))

    content.append(score_table)

    content.append(Spacer(1,15))

    content.append(
        Paragraph(
            f"<b>Strengths:</b><br/>{data['strengths']}",
            styles["BodyText"]
        )
    )

    content.append(Spacer(1,10))

    content.append(
        Paragraph(
            f"<b>Areas of Improvement:</b><br/>{data['improvements']}",
            styles["BodyText"]
        )
    )

    content.append(Spacer(1,10))

    content.append(
        Paragraph(
            f"<b>Interview Summary:</b><br/>{data['summary']}",
            styles["BodyText"]
        )
    )

    doc.build(content)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf

# =====================================================
# TABS
# =====================================================

tab1, tab2, tab3 = st.tabs([
    "📋 Candidate Tracker",
    "📊 Candidate Sheet Data",
    "📝 Interview Report"
])

# =====================================================
# TAB 1
# =====================================================

with tab1:

    st.components.v1.iframe(
        GOOGLE_SHEET_URL,
        height=950,
        scrolling=True
    )

# =====================================================
# TAB 2
# =====================================================

with tab2:

    c1, c2, c3 = st.columns(3)

    with c1:
        candidate_name = st.text_input("Candidate")

    with c2:
        position = st.text_input("Role")

    with c3:
        interview_date = st.date_input("Date")

    st.markdown("### Evaluation")

    r1, r2, r3 = st.columns(3)

    with r1:
        communication = st.slider("Communication",1,10,5)
        confidence = st.slider("Confidence",1,10,5)

    with r2:
        technical = st.slider("Technical",1,10,5)
        learning = st.slider("Learning",1,10,5)

    with r3:
        problem_solving = st.slider("Problem Solving",1,10,5)
        team_fit = st.slider("Team Fit",1,10,5)

    f1, f2 = st.columns(2)

    with f1:
        strengths = st.text_area(
            "Strengths",
            height=120
        )

    with f2:
        improvements = st.text_area(
            "Areas for Improvement",
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

    if st.button("📄 Generate Interview Report"):

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

        filename = (
            candidate_name.replace(" ", "_")
            if candidate_name
            else "Candidate"
        )

        st.download_button(
            "⬇ Download PDF",
            pdf_file,
            file_name=f"{filename}_Interview_Report.pdf",
            mime="application/pdf"
        )

# =====================================================
# TAB 3 — GOOGLE SHEET LIVE TABLE
# =====================================================

with tab3:
    show_sheet_page()