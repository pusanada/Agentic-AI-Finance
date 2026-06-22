import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# Page Config
st.set_page_config(
    page_title="ESG Analyst Agent Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling
st.markdown("""
<style>
    /* Dark Mode harmony & fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Noto+Sans+Thai:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', 'Noto Sans Thai', sans-serif;
    }
    
    /* Title and header formatting */
    .title-text {
        font-weight: 800;
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        margin-bottom: 0.5rem;
    }
    
    .subtitle-text {
        color: #9CA3AF;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Style all bordered containers as premium metric cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(17, 24, 39, 0.7) !important;
        border: 1px solid rgba(16, 185, 129, 0.2) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
        transition: transform 0.2s, border-color 0.2s !important;
        margin-bottom: 1rem !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-2px) !important;
        border-color: rgba(16, 185, 129, 0.5) !important;
    }
    
    /* Custom badges */
    .badge {
        display: inline-block;
        padding: 0.25em 0.6em;
        font-size: 75%;
        font-weight: 700;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 0.375rem;
    }
    .badge-success {
        background-color: rgba(16, 185, 129, 0.2);
        color: #10B981;
        border: 1px solid #10B981;
    }
    .badge-warning {
        background-color: rgba(245, 158, 11, 0.2);
        color: #F59E0B;
        border: 1px solid #F59E0B;
    }
    .badge-danger {
        background-color: rgba(239, 68, 68, 0.2);
        color: #EF4444;
        border: 1px solid #EF4444;
    }
</style>
""", unsafe_allow_html=True)


# API Endpoint URL
BACKEND_URL = "http://127.0.0.1:8000/api/v1"

# Sidebar Configuration
st.sidebar.markdown("<div style='text-align: center; padding: 1rem 0;'><span style='font-size: 3rem;'>🌱</span></div>", unsafe_allow_html=True)
st.sidebar.title("ESG Analyst Agent Config")
st.sidebar.info("""
**เอเจนต์ผู้รับผิดชอบ**: JUMP+ & ESG Analyst Agent
**เป้าหมาย**: คัดกรองและประเมินมูลค่าหุ้นยั่งยืนด้วยคะแนน CGR, ประวัติ ก.ล.ต., แผนเพิ่มมูลค่าบริษัท (CVUP) และน้ำเสียงผู้บริหารจาก Opp Day
""")

# Backend Connection Check
health_ok = False
try:
    health_resp = requests.get(f"{BACKEND_URL}/health", timeout=2)
    if health_resp.status_code == 200:
        health_data = health_resp.json()
        health_ok = True
        st.sidebar.success(f"🟢 Backend Connected\n\nClaude API: {'Connected' if health_data['claude_configured'] else 'Mock Mode'}\n\nTyphoon API: {'Connected' if health_data['typhoon_configured'] else 'Mock Mode'}")
except Exception:
    st.sidebar.error("🔴 Backend Connection Offline. Please start the FastAPI backend server first.")

# Main Page Header
st.markdown("<div class='title-text'>🌱 JUMP+ & ESG Analyst Agent Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle-text'>ระบบคัดกรองและตรวจสอบความโปร่งใสของหุ้นยั่งยืน (Supply-side ESG Auditing)</div>", unsafe_allow_html=True)

if not health_ok:
    st.warning("⚠️ ไม่พบเซิร์ฟเวอร์ Backend กรุณารันเซิร์ฟเวอร์ก่อนโดยใช้คำสั่งในโฟลเดอร์โครงการ: `python backend/app/main.py` หรือดูคำแนะนำด้านล่าง")
    st.stop()

# Define Tabs
tab1, tab2 = st.tabs(["📊 ด่านแรก: การคัดกรองหุ้นยั่งยืน (Screening)", "🔍 เจาะลึก: ตรวจสอบความโปร่งใส (ESG Audit)"])

with tab1:
    st.header("ดึงข้อมูลและคัดกรองตามเกณฑ์ขั้นต่ำ")
    st.markdown("""
    **เกณฑ์การผ่านด่านแรก (Screening Criteria):**
    1. เข้าร่วมโครงการเพิ่มพูนมูลค่าบริษัทของ ตลท. (**JUMP+**)
    2. คะแนนบรรษัทภิบาล (**CGR Score >= 90**) (ระดับดีเลิศ / 5 ดาว)
    3. **ไม่มีประวัติการฟ้องร้อง** คดีแพ่งหรืออาญาจาก สำนักงาน ก.ล.ต. ในรอบ 5 ปี
    """)
    
    if "screen_data" not in st.session_state:
        st.session_state.screen_data = None

    if st.button("เริ่มการคัดกรองด่านแรก (Run First-Stage Screening)"):
        with st.spinner("กำลังดึงข้อมูลและกรองรายชื่อหุ้นจาก ตลท. และ ก.ล.ต. ..."):
            try:
                resp = requests.get(f"{BACKEND_URL}/screen")
                if resp.status_code == 200:
                    st.session_state.screen_data = resp.json()
                else:
                    st.error("ไม่สามารถเชื่อมต่อดึงข้อมูลการกรองได้")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {str(e)}")

    if st.session_state.screen_data:
        screen_data = st.session_state.screen_data
        st.success(f"การคัดกรองเสร็จสมบูรณ์! พบหุ้นผ่านเกณฑ์ {screen_data['passed_count']} ตัว และไม่ผ่านเกณฑ์ {screen_data['failed_count']} ตัว")
        
        # Display Data Source Info
        source_label = "🌐 ดึงข้อมูลสดจากเว็บไซต์ (Scraped from Web)" if screen_data.get("data_source") == "scraped" else "📦 ดึงข้อมูลจำลองในระบบ (Mock Database)"
        st.info(f"**แหล่งที่มาของข้อมูล (Data Source):** {source_label}")
        
        # Columns for showing Passed and Failed lists
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✅ หุ้นที่ผ่านเกณฑ์ด่านแรก (Screening Passed)")
            passed_list = []
            for stock in screen_data["passed"]:
                passed_list.append({
                    "Ticker": stock["ticker"],
                    "Company Name": stock["company_name"],
                    "CGR Score": stock["first_stage_checks"]["cgr_score"],
                    "JUMP+ Status": "เข้าร่วม" if stock["first_stage_checks"]["jump_plus"] else "ไม่เข้าร่วม",
                    "SEC Clear (5Y)": "ไม่มีคดีความ" if stock["first_stage_checks"]["sec_clean"] else "มีประวัติ"
                })
            if passed_list:
                st.dataframe(
                    pd.DataFrame(passed_list),
                    use_container_width=True,
                    column_config={
                        "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                        "Company Name": st.column_config.TextColumn("Company Name", width="medium"),
                        "CGR Score": st.column_config.NumberColumn("CGR Score", format="%d", width="small"),
                        "JUMP+ Status": st.column_config.TextColumn("JUMP+ Status", width="small"),
                        "SEC Clear (5Y)": st.column_config.TextColumn("SEC Clear (5Y)", width="small")
                    }
                )
            else:
                st.info("ไม่มีหุ้นผ่านเกณฑ์")
                
        with col2:
            st.subheader("❌ หุ้นที่ไม่ผ่านเกณฑ์ (Screening Failed)")
            failed_list = []
            for stock in screen_data["failed"]:
                failed_list.append({
                    "Ticker": stock["ticker"],
                    "Company Name": stock["company_name"],
                    "Failure Reason": stock["message"]
                })
            if failed_list:
                st.dataframe(
                    pd.DataFrame(failed_list),
                    use_container_width=True,
                    column_config={
                        "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                        "Company Name": st.column_config.TextColumn("Company Name", width="medium"),
                        "Failure Reason": st.column_config.TextColumn("Failure Reason", width="large")
                    }
                )
            else:
                st.info("ไม่มีหุ้นไม่ผ่านเกณฑ์")


with tab2:
    st.header("การตรวจสอบเชิงลึกและการประเมินความน่าเชื่อถือของผู้บริหาร")
    st.markdown("""
    เลือกหุ้นที่ผ่านการคัดกรองด่านแรก เพื่อประเมินเชิงลึก โดยการอัปโหลดไฟล์แผนเพิ่มมูลค่า (**CVUP**), รายงานประจำปี (**Form 56-1 One Report**), และเสียงการประชุม (**Opportunity Day**)
    """)
    
    # Selection of tickers (dynamically updated from screening results if available)
    passed_tickers = []
    if st.session_state.get("screen_data"):
        passed_tickers = [stock["ticker"] for stock in st.session_state.screen_data["passed"]]
    
    # Fallback to default list if screening hasn't been run yet
    if not passed_tickers:
        passed_tickers = ["PTT", "CPALL", "ADVANC", "SCC", "KBANK", "BDMS", "TRUE"]
        
    selected_ticker = st.selectbox("เลือกหุ้นที่ต้องการประเมิน (Select Ticker):", passed_tickers)

    
    # Form Layout
    col_files, col_audit = st.columns([1, 2])
    
    with col_files:
        st.subheader("📁 อัปโหลดเอกสารหลักฐาน")
        cvup_file = st.file_uploader("1. แผนเพิ่มพูนมูลค่าบริษัท (CVUP PDF):", type=["pdf"])
        onereport_file = st.file_uploader("2. รายงาน Form 56-1 One Report (PDF):", type=["pdf"])
        audio_file = st.file_uploader("3. เสียงการประชุม Opp Day (MP3/WAV):", type=["mp3", "wav"])
        
        run_audit = st.button("เริ่มการเจาะลึกและตรวจสอบ (Run Transparency Audit)")
        
    with col_audit:
        # Initialize session state for audit logging if not already present
        if "audit_log" not in st.session_state:
            st.session_state.audit_log = []
        if "signed_tickers" not in st.session_state:
            st.session_state.signed_tickers = {}
        if run_audit or f"report_{selected_ticker}" not in st.session_state:
            with st.spinner("กำลังแกะโครงสร้างเอกสาร วิเคราะห์ความสอดคล้อง และถอดความวิเคราะห์น้ำเสียงของผู้บริหารด้วย AI ..."):
                try:
                    # Prepare upload files
                    files = {}
                    if cvup_file:
                        files["cvup_file"] = (cvup_file.name, cvup_file.getvalue(), "application/pdf")
                    if onereport_file:
                        files["onereport_file"] = (onereport_file.name, onereport_file.getvalue(), "application/pdf")
                    if audio_file:
                        files["audio_file"] = (audio_file.name, audio_file.getvalue(), "audio/mpeg")
                        
                    # Request analysis from API
                    if files:
                        resp = requests.post(f"{BACKEND_URL}/analyze/{selected_ticker}", files=files)
                    else:
                        resp = requests.get(f"{BACKEND_URL}/report/{selected_ticker}")
                        
                    if resp.status_code == 200:
                        st.session_state[f"report_{selected_ticker}"] = resp.json()
                    else:
                        st.error(f"การวิเคราะห์ล้มเหลว: {resp.text}")
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการประเมิน: {str(e)}")
                    
        # Render Report Details
        if f"report_{selected_ticker}" in st.session_state:
            report = st.session_state[f"report_{selected_ticker}"]
            
            if report.get("status") == "REJECTED_STAGE_1":
                st.error(f"หุ้นนี้ไม่ผ่านการคัดกรองด่านแรก: {report['message']}")
            else:
                st.markdown(f"### ผลการตรวจสอบหุ้น **{report['ticker']}** ({report['company_name']})")
                
                # Visual Gauge for Overall Score
                score = report["overall_score"]
                
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = score,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "ESG & Credibility Score (คะแนนรวมความยั่งยืนและความน่าเชื่อถือ)", 'font': {'size': 18}},
                    gauge = {
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                        'bar': {'color': "#10B981"},
                        'bgcolor': "rgba(17, 24, 39, 0.7)",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.1)'},
                            {'range': [50, 75], 'color': 'rgba(245, 158, 11, 0.1)'},
                            {'range': [75, 100], 'color': 'rgba(16, 185, 129, 0.1)'}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': "#F9FAFB", 'family': "Outfit"},
                    height=200,
                    margin=dict(l=30, r=30, t=50, b=10)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Grid details
                c1, c2 = st.columns(2)
                
                with c1:
                    with st.container(border=True):
                        st.subheader("📑 การตรวจสอบแผนงาน (Document Audit: CVUP vs One Report)")
                        rating = report["document_audit"]["alignment_rating"]
                        badge_class = "badge-success" if rating == "High" else ("badge-warning" if rating == "Medium" else "badge-danger")
                        st.markdown(f"ระดับความสอดคล้องของเป้าหมาย: <span class='badge {badge_class}'>{rating} Alignment</span>", unsafe_allow_html=True)
                        
                        st.markdown("**เป้าหมายสัญญาในแผนเพิ่มพูนมูลค่าบริษัท (CVUP Commitments):**")
                        for c in report["document_audit"]["commitments_found"]:
                            st.markdown(f"- {c}")
                            
                        st.markdown("**หลักฐานและการพิสูจน์ใน One Report ของจริง:**")
                        for e in report["document_audit"]["one_report_evidence"]:
                            st.markdown(f"- {e}")
                            
                        if report["document_audit"]["gaps_or_delays"]:
                            st.markdown("**ช่องว่างหรือเป้าหมายที่ล่าช้า (Gaps/Delays found):**")
                            for g in report["document_audit"]["gaps_or_delays"]:
                                st.markdown(f"- <span style='color:#EF4444;'>{g}</span>", unsafe_allow_html=True)
                                
                        st.info(f"**เหตุผลการประเมินความสอดคล้อง:** {report['document_audit']['rationale']}")
                    
                with c2:
                    with st.container(border=True):
                        st.subheader("🎙️ ตรวจสอบการสื่อสารผู้บริหาร (Opportunity Day Voice Sentiment)")
                        st.markdown("วิเคราะห์ด้วยเทคโนโลยีถอดรหัสเสียง **Typhoon2-Audio**")
                        
                        # Horizontal bar chart for audio metrics
                        audio_metrics = {
                            "ดัชนีชี้วัด (Metrics)": ["ความเชื่อมั่น (Confidence)", "ความจริงใจ/ไม่บิดเบือน (Sincerity)", "การหลบเลี่ยงคำถาม (Evasion)"],
                            "คะแนน (Scores)": [
                                report["audio_credibility"]["confidence_score"],
                                report["audio_credibility"]["sincerity_score"],
                                report["audio_credibility"]["evasion_score"]
                            ]
                        }
                        df_audio = pd.DataFrame(audio_metrics)
                        fig_audio = px.bar(
                            df_audio,
                            x="คะแนน (Scores)",
                            y="ดัชนีชี้วัด (Metrics)",
                            orientation='h',
                            color="ดัชนีชี้วัด (Metrics)",
                            color_discrete_map={
                                "ความเชื่อมั่น (Confidence)": "#10B981",
                                "ความจริงใจ/ไม่บิดเบือน (Sincerity)": "#3B82F6",
                                "การหลบเลี่ยงคำถาม (Evasion)": "#EF4444"
                            }
                        )
                        fig_audio.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font={'color': "#F9FAFB"},
                            height=180,
                            showlegend=False,
                            xaxis={'range': [0, 100]},
                            margin=dict(l=10, r=10, t=10, b=10)
                        )
                        st.plotly_chart(fig_audio, use_container_width=True)
                        
                        st.markdown("**เครื่องหมายและดัชนีโทนเสียงการพูด (Vocal Cues & Markers):**")
                        for marker in report["audio_credibility"]["findings"]:
                            st.markdown(f"- {marker}")
                        st.markdown(f"**ข้อสรุปน้ำเสียง:** {report['audio_credibility']['conclusion']}")
                    
                # Full Executive Summary
                st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
                with st.container(border=True):
                    st.subheader("📝 บทสรุปความโปร่งใสและคำแนะนำการลงทุน (Executive Summary)")
                    
                    col_sum1, col_sum2 = st.columns([2, 1])
                    with col_sum1:
                        st.markdown(f"**สรุปผลการวิเคราะห์ระดับองค์กร (Thai):**\n\n{report['executive_summary_th']}")
                        st.markdown(f"**คำแนะนำการส่งต่อไปยัง Portfolio Allocator Agent:**\n\n{report['investment_recommendation']}")
                    with col_sum2:
                        st.markdown("**จุดเด่นที่สำคัญ (Key Strengths):**")
                        for strength in report["key_strengths"]:
                            st.markdown(f"🟩 {strength}")
                        st.markdown("**ความเสี่ยงและข้อสังเกต (Risks & Warnings):**")
                        for risk in report["risks_and_warnings"]:
                            st.markdown(f"🟧 {risk}")
                    
                    # Hand-off button
                    st.markdown("---")
                    if st.button("🚀 ส่งออกผลการประเมินไปยัง Portfolio Allocator Agent (Hand-off)"):
                        export_payload = {
                            "ticker": report["ticker"],
                            "company_name": report["company_name"],
                            "overall_score": report["overall_score"],
                            "cgr_score": report["first_stage_checks"]["cgr_score"],
                            "sec_clean": report["first_stage_checks"]["sec_clean"],
                            "document_alignment": report["document_audit"]["alignment_rating"],
                            "vocal_credibility_score": report["audio_credibility"]["sincerity_score"]
                        }
                        st.balloons()
                        st.success("ส่งออกสำเร็จ! ข้อมูลหุ้นได้รับการส่งไปยังคิวข้อมูลของเอเจนต์จัดพอร์ตโฟลิโอเรียบร้อยแล้ว")
                        st.json(export_payload)

