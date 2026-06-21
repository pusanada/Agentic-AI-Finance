import streamlit as st
import requests
import os
import json
import pandas as pd

# Set page config with standard page title and favicon
st.set_page_config(
    page_title="ThaiESG Tax Calculator & OCR Agent",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend API configuration
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

# Premium Custom CSS Styling for a stunning financial dark-theme dashboard
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Main Background and Layout */
    .stApp {
        background: radial-gradient(circle at top right, #1e1b4b 0%, #0f172a 100%);
        color: #f8fafc;
    }
    
    /* Custom Card Style */
    .premium-card {
        background: rgba(30, 41, 59, 0.45);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(8px);
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .premium-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 12px 40px 0 rgba(99, 102, 241, 0.1);
    }
    
    /* Metrics Layout */
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #94a3b8;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Progress Bar */
    .progress-container {
        width: 100%;
        background-color: #334155;
        border-radius: 8px;
        height: 16px;
        overflow: hidden;
        margin-top: 10px;
    }
    .progress-bar-fill {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
        height: 100%;
        border-radius: 8px;
        transition: width 0.5s ease-in-out;
    }
    
    /* Buttons Custom Style */
    div.stButton > button {
        background: linear-gradient(90deg, #6366f1 0%, #4f46e5 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 24px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #4f46e5 0%, #4338ca 100%);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
        transform: translateY(-1px);
    }
    
    /* Chat bubbles styling */
    .chat-bubble {
        padding: 14px 18px;
        border-radius: 16px;
        margin-bottom: 12px;
        line-height: 1.5;
        font-size: 0.95rem;
    }
    .chat-user {
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-bottom-right-radius: 2px;
        text-align: right;
        margin-left: 20%;
    }
    .chat-agent {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-bottom-left-radius: 2px;
        margin-right: 20%;
    }
    .chat-source {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 4px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Main Banner / Title
st.markdown("""
<div style='text-align: center; margin-bottom: 30px; padding: 20px 0;'>
    <h1 style='font-size: 2.8rem; font-weight: 800; background: linear-gradient(90deg, #6366f1 0%, #ec4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        ThaiESG Personal Tax & OCR Agent
    </h1>
    <p style='color: #94a3b8; font-size: 1.15rem; max-width: 700px; margin: 10px auto 0;'>
        Scan your 50 Tawi tax documents, calculate your optimal ThaiESG investment quota, and query Thai tax regulations in real-time.
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar with settings and info
with st.sidebar:
    st.markdown("### ⚙️ System Settings")
    backend_status = "🔴 Offline"
    try:
        r = requests.get(BACKEND_URL)
        if r.status_code == 200:
            backend_status = "🟢 Connected"
    except Exception:
        pass
    
    st.markdown(f"**Backend Status:** {backend_status}")
    
    st.markdown("---")
    st.markdown("### 📜 ThaiESG Quota Rules (Tax Year 2569)")
    st.markdown("""
    - **Limit:** Up to **30%** of assessable income.
    - **Cap:** Maximum **300,000 THB** per year.
    - **Holding Period:** **5 years** minimum (day-to-day).
    - **Retirement Pool:** **Not shared** with RMF/SSF (separate limit of 300,000 THB).
    """)
    
    st.markdown("---")
    st.markdown("### 💡 Document Tips (50 Tawi)")
    st.markdown("""
    Upload a clear photo or PDF scan of your 50 Tawi document. The system will look for:
    1. **Total Assessable Income** (เงินได้สะสม / เงินได้พึงประเมิน)
    2. **Withholding Tax** (ภาษีหัก ณ ที่จ่าย)
    """)

# Session State Initializations
if "assessable_income" not in st.session_state:
    st.session_state.assessable_income = 0.0
if "withholding_tax" not in st.session_state:
    st.session_state.withholding_tax = 0.0
if "existing_deductions" not in st.session_state:
    st.session_state.existing_deductions = 0.0
if "document_type" not in st.session_state:
    st.session_state.document_type = "Not uploaded"
if "already_purchased" not in st.session_state:
    st.session_state.already_purchased = 0.0
if "calculation_results" not in st.session_state:
    st.session_state.calculation_results = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Tabs
tab1, tab2 = st.tabs(["💰 OCR & Quota Dashboard", "💬 Tax Q&A Assistant"])

# ==========================================
# TAB 1: OCR & QUOTA DASHBOARD
# ==========================================
with tab1:
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("### 1. Document Upload & Extraction")
        st.markdown("Upload your 50 Tawi tax document here:")
        
        uploaded_file = st.file_uploader(
            "Choose a 50 Tawi document (Image or PDF)...",
            type=["png", "jpg", "jpeg", "webp", "pdf"],
            label_visibility="collapsed"
        )
        
        st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.85rem; margin: 10px 0;'>— OR —</p>", unsafe_allow_html=True)
        
        # Scan e:\AI-Finance\.test_pdf directory for extra files if present
        demo_files = ["None"]
        test_pdf_dir = "e:\\AI-Finance\\.test_pdf"
        if os.path.exists(test_pdf_dir):
            try:
                extra_files = sorted([os.path.join(".test_pdf", f) for f in os.listdir(test_pdf_dir) if f.endswith(".pdf")])
                demo_files.extend(extra_files)
            except Exception as e:
                pass

        demo_option = st.selectbox(
            "Select a pre-loaded Demo PDF:",
            options=demo_files,
            index=0
        )
        
        selected_file_name = None
        selected_file_bytes = None
        selected_file_type = None
        
        if uploaded_file is not None:
            selected_file_name = uploaded_file.name
            selected_file_bytes = uploaded_file.getvalue()
            selected_file_type = uploaded_file.type
            
            # Show preview based on file type
            if selected_file_name.lower().endswith('.pdf'):
                st.info(f"📄 PDF Document Uploaded: **{selected_file_name}** ({uploaded_file.size / 1024:.1f} KB)")
            else:
                st.image(uploaded_file, caption="Uploaded Document Preview", use_column_width=True)
        elif demo_option != "None":
            # Load demo file from workspace
            demo_path = os.path.join("e:\\AI-Finance", demo_option)
            if os.path.exists(demo_path):
                with open(demo_path, "rb") as f:
                    selected_file_bytes = f.read()
                selected_file_name = demo_option
                selected_file_type = "application/pdf"
                st.info(f"📄 Pre-loaded Demo PDF Selected: **{selected_file_name}** ({len(selected_file_bytes) / 1024:.1f} KB)")
            else:
                st.error(f"Demo file not found at {demo_path}")
        
        if selected_file_bytes is not None:
            # Button to trigger OCR
            if st.button("Extract Data using Typhoon OCR"):
                with st.spinner("Analyzing document with Typhoon2-Vision..."):
                    try:
                        # Prepare payload
                        files = {"file": (selected_file_name, selected_file_bytes, selected_file_type)}
                        response = requests.post(f"{BACKEND_URL}/api/v1/tax/ocr", files=files)
                        
                        if response.status_code == 200:
                            res_data = response.json()
                            st.session_state.assessable_income = res_data["assessable_income"]
                            st.session_state.withholding_tax = res_data["withholding_tax"]
                            st.session_state.existing_deductions = res_data["existing_deductions"]
                            st.session_state.already_purchased = res_data.get("already_purchased", 0.0)
                            st.session_state.document_type = res_data["document_type"]
                            
                            st.success("Extraction completed successfully!")
                            if res_data.get("is_mock"):
                                st.warning("Notice: System fell back to a mock response for preview/demo purposes (Mock OCR).")
                        else:
                            st.error(f"OCR Request failed: {response.text}")
                    except Exception as e:
                        st.error(f"Could not connect to backend: {str(e)}")
        
        # Human-in-the-Loop verification form
        st.markdown("---")
        st.markdown("### 2. Verify Extracted Values (Human-in-the-Loop)")
        st.info("Check and correct any details extracted from the document:")
        
        with st.form("hitl_form"):
            # Render inputs initialized with session state
            income_input = st.number_input(
                "Total Assessable Income (เงินได้พึงประเมิน) (THB)",
                min_value=0.0,
                value=float(st.session_state.assessable_income),
                step=1000.0
            )
            tax_input = st.number_input(
                "Withholding Tax (ภาษีหัก ณ ที่จ่าย) (THB)",
                min_value=0.0,
                value=float(st.session_state.withholding_tax),
                step=500.0
            )
            already_purchased_input = st.number_input(
                "ThaiESG Amount Already Invested This Year (THB)",
                min_value=0.0,
                value=float(st.session_state.already_purchased),
                step=1000.0
            )
            
            submit_btn = st.form_submit_button("Calculate ThaiESG Quota")
            if submit_btn:
                # Update session states
                st.session_state.assessable_income = income_input
                st.session_state.withholding_tax = tax_input
                st.session_state.already_purchased = already_purchased_input
                
                # Call backend calculate endpoint
                with st.spinner("Calculating tax saving quota..."):
                    try:
                        payload = {
                            "assessable_income": income_input,
                            "already_purchased": already_purchased_input
                        }
                        response = requests.post(f"{BACKEND_URL}/api/v1/tax/calculate", json=payload)
                        if response.status_code == 200:
                            st.session_state.calculation_results = response.json()
                            st.success("Calculated successfully!")
                        else:
                            st.error(f"Calculation API failed: {response.text}")
                    except Exception as e:
                        st.error(f"Could not connect to backend: {str(e)}")

    with col2:
        st.markdown("### 3. Investment Quota Dashboard")
        
        if st.session_state.calculation_results is None:
            # Default helper message if no calculation has run
            st.markdown("""
            <div class='premium-card' style='text-align: center; padding: 50px 20px;'>
                <h4 style='color: #64748b;'>No calculation run yet</h4>
                <p style='color: #475569; font-size: 0.95rem;'>
                    Upload a 50 Tawi document or enter your income manually, then click "Calculate ThaiESG Quota" to view your dashboard.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            res = st.session_state.calculation_results
            max_quota = res["max_quota"]
            remaining_quota = res["remaining_quota"]
            purchased = res["already_purchased"]
            income = res["assessable_income"]
            
            # Progress bar maths
            progress_pct = 0.0
            if max_quota > 0:
                progress_pct = min(100.0, (purchased / max_quota) * 100)

            # Display UI metrics in gorgeous cards
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.markdown(f"""
                <div class='premium-card'>
                    <div class='metric-label'>Assessable Income</div>
                    <div class='metric-value'>฿{income:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class='premium-card'>
                    <div class='metric-label'>Already Purchased</div>
                    <div class='metric-value' style='background: linear-gradient(90deg, #10b981 0%, #34d399 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                        ฿{purchased:,.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_m2:
                st.markdown(f"""
                <div class='premium-card'>
                    <div class='metric-label'>Max ThaiESG Limit (30% Cap)</div>
                    <div class='metric-value'>฿{max_quota:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class='premium-card'>
                    <div class='metric-label'>Remaining Quota Room</div>
                    <div class='metric-value' style='background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                        ฿{remaining_quota:,.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # High-impact progress visualization card
            st.markdown(f"""
            <div class='premium-card'>
                <h4>Quota Usage Tracker</h4>
                <p style='color: #94a3b8; font-size: 0.9rem;'>
                    You have utilized <strong>{progress_pct:.1f}%</strong> of your ฿{max_quota:,.2f} maximum ThaiESG quota.
                </p>
                <div class='progress-container'>
                    <div class='progress-bar-fill' style='width: {progress_pct}%;'></div>
                </div>
                <div style='display: flex; justify-content: space-between; margin-top: 8px; font-size: 0.8rem; color: #64748b;'>
                    <span>฿{purchased:,.0f} invested</span>
                    <span>฿{remaining_quota:,.0f} remaining room</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Recommendations card
            st.markdown("### 4. Smart Recommendations")
            if remaining_quota > 0:
                st.markdown(f"""
                <div class='premium-card' style='border-left: 5px solid #6366f1;'>
                    <h5 style='color: #a5b4fc; margin-bottom: 8px;'>💡 Recommended Investment Plan</h5>
                    <p style='font-size: 0.95rem; margin-bottom: 0;'>
                        To maximize your tax benefits for this tax year, consider investing another <strong>฿{remaining_quota:,.2f}</strong> in ThaiESG funds. 
                        Since these units must be held for <strong>5 years</strong>, this investment will be redeemable in <strong>{res.get('holding_period_years', 5)} years</strong>.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='premium-card' style='border-left: 5px solid #10b981;'>
                    <h5 style='color: #6ee7b7; margin-bottom: 8px;'>🎉 Maximum Savings Achieved</h5>
                    <p style='font-size: 0.95rem; margin-bottom: 0;'>
                        Outstanding! You have fully utilized your ThaiESG investment quota for this tax year. No further ThaiESG investments are needed to claim the maximum tax deduction.
                    </p>
                </div>
                """, unsafe_allow_html=True)

# ==========================================
# TAB 2: TAX Q&A ASSISTANT
# ==========================================
with tab2:
    st.markdown("### 💬 Chat with the Tax Saving Agent")
    st.markdown("Ask anything about ThaiESG regulations, RMF/SSF limits, or document rules:")
    
    # Preset quick-click questions
    presets = [
        "What is the holding period for ThaiESG?",
        "Is the ThaiESG quota shared with RMF?",
        "What happens if I sell ThaiESG before 5 years?",
        "How is the max ThaiESG limit calculated?"
    ]
    
    preset_cols = st.columns(len(presets))
    clicked_preset = None
    for idx, preset_text in enumerate(presets):
        with preset_cols[idx]:
            if st.button(preset_text, key=f"preset_{idx}"):
                clicked_preset = preset_text

    # Show past chat history
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.markdown(f"""
            <div class='chat-bubble chat-user'>
                {chat["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            # Display retrieved source documents if available
            sources_html = ""
            if chat.get("sources"):
                sources_html = "<div class='chat-source'><strong>Retrieved Regulatory Sources:</strong><br>"
                for source in chat["sources"]:
                    sources_html += f"• {source['content']} (Relevance: {source['relevance_score'] * 100:.0f}%)<br>"
                sources_html += "</div>"
                
            st.markdown(f"""
            <div class='chat-bubble chat-agent'>
                {chat["content"]}
                {sources_html}
            </div>
            """, unsafe_allow_html=True)

    # Input chat text
    chat_query = st.chat_input("Enter your tax question...")
    
    # Override query if preset clicked
    if clicked_preset:
        chat_query = clicked_preset

    if chat_query:
        # Append user message
        st.session_state.chat_history.append({"role": "user", "content": chat_query})
        
        # Display user message immediately
        st.markdown(f"<div class='chat-bubble chat-user'>{chat_query}</div>", unsafe_allow_html=True)
        
        # Query backend
        with st.spinner("Agent is searching regulations..."):
            try:
                payload = {"query": chat_query}
                response = requests.post(f"{BACKEND_URL}/api/v1/tax/query", json=payload)
                if response.status_code == 200:
                    res_data = response.json()
                    answer = res_data["answer"]
                    sources = res_data["retrieved_contexts"]
                    
                    # Append response
                    st.session_state.chat_history.append({
                        "role": "agent",
                        "content": answer,
                        "sources": sources
                    })
                    
                    # Refresh page to show updated messages
                    st.rerun()
                else:
                    st.error(f"Query API failed: {response.text}")
            except Exception as e:
                st.error(f"Could not connect to backend: {str(e)}")
