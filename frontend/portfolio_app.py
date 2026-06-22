import streamlit as st
import requests
import os
import json
import pandas as pd

# Set page config for a premium standalone experience
st.set_page_config(
    page_title="Elite Portfolio Allocator & Risk Guard",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend API configuration
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

# Premium Custom CSS Styling for a state-of-the-art dark theme dashboard
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Main Background and Layout */
    .stApp {
        background: radial-gradient(circle at top right, #1e1b4b 0%, #030712 100%);
        color: #f8fafc;
    }
    
    /* Premium Glassmorphism Card Style */
    .premium-card {
        background: rgba(17, 24, 39, 0.6);
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 30px 0 rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(12px);
        margin-bottom: 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .premium-card:hover {
        border-color: rgba(139, 92, 246, 0.55);
        box-shadow: 0 15px 35px -5px rgba(139, 92, 246, 0.25);
        transform: translateY(-2px);
    }
    
    /* Premium Glowing Metric Style */
    .metric-value {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #a78bfa 0%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    
    /* Progress Bar */
    .progress-container {
        width: 100%;
        background-color: #1f2937;
        border-radius: 9999px;
        height: 12px;
        overflow: hidden;
        margin-top: 10px;
    }
    .progress-bar-fill {
        background: linear-gradient(90deg, #8b5cf6 0%, #ec4899 100%);
        height: 100%;
        border-radius: 9999px;
        transition: width 0.6s ease-in-out;
    }
    
    /* Premium Glowing Button Custom Style */
    div.stButton > button {
        background: linear-gradient(90deg, #8b5cf6 0%, #ec4899 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 10px 28px;
        font-weight: 700;
        font-size: 0.95rem;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.35);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #7c3aed 0%, #db2777 100%);
        box-shadow: 0 8px 30px rgba(139, 92, 246, 0.6);
        transform: translateY(-2px);
    }
    
    /* Chat bubbles styling */
    .chat-bubble {
        padding: 16px 20px;
        border-radius: 18px;
        margin-bottom: 14px;
        line-height: 1.6;
        font-size: 0.95rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    .chat-user {
        background: rgba(139, 92, 246, 0.15);
        border: 1px solid rgba(139, 92, 246, 0.35);
        border-bottom-right-radius: 2px;
        text-align: right;
        margin-left: 20%;
    }
    .chat-agent {
        background: rgba(17, 24, 39, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-bottom-left-radius: 2px;
        margin-right: 20%;
    }
    .chat-source {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 8px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        padding-top: 6px;
    }
    
    /* Custom Headers */
    .glowing-title {
        font-size: 3.2rem;
        font-weight: 900;
        background: linear-gradient(90deg, #a78bfa 0%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 10px;
    }
    
    /* AUQ Supervisor Status Badge styles */
    @keyframes pulse-yellow {
        0% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(245, 158, 11, 0); }
        100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }
    }
    @keyframes flash-red {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.5); border-color: rgba(239, 68, 68, 0.7); }
        50% { box-shadow: 0 0 0 12px rgba(239, 68, 68, 0); border-color: rgba(239, 68, 68, 0.3); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); border-color: rgba(239, 68, 68, 0.7); }
    }
    .status-approved {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid #10b981;
        color: #34d399;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: bold;
        display: inline-block;
    }
    .status-pause {
        background: rgba(245, 158, 11, 0.12);
        border: 1px solid #f59e0b;
        color: #fbbf24;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: bold;
        display: inline-block;
        animation: pulse-yellow 2s infinite;
    }
    .status-escalated {
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid #ef4444;
        color: #fca5a5;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: bold;
        display: inline-block;
        animation: flash-red 1.5s infinite;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Main Banner / Title
st.markdown("""
<div style='text-align: center; margin-bottom: 30px; padding: 20px 0;'>
    <h1 class='glowing-title'>💎 Elite Portfolio Allocator</h1>
    <p style='color: #94a3b8; font-size: 1.2rem; max-width: 800px; margin: 10px auto 0;'>
        Optimize your assets, enforce real-time regulatory and suitability safeguards, and construct a premium investment strategy.
    </p>
</div>
""", unsafe_allow_html=True)

# Initialize Session States
if "allocation_results" not in st.session_state:
    st.session_state.allocation_results = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "execution_confirmed" not in st.session_state:
    st.session_state.execution_confirmed = False

# Sidebar with configuration settings
with st.sidebar:
    st.markdown("### ⚙️ System Status")
    backend_status = "🔴 Offline"
    try:
        r = requests.get(BACKEND_URL)
        if r.status_code == 200:
            backend_status = "🟢 Connected"
    except Exception:
        pass
    st.markdown(f"**Backend API Status:** {backend_status}")
    st.markdown("---")
    
    st.markdown("### 🛠️ Allocation Settings")
    
    investment_budget = st.number_input(
        "Direct Investment Capital (THB):",
        min_value=0.0,
        value=150000.0,
        step=5000.0,
        help="The amount you want to allocate across eligible assets."
    )
    
    goal_option = st.selectbox(
        "Financial Strategy:",
        options=["Growth (High Growth Focus)", "Dividend (High Dividend Yield)", "Balanced (Moderate Growth & Income)"]
    )
    
    risk_option = st.selectbox(
        "KYC Suitability Risk Level:",
        options=["Conservative (Low Risk Limit)", "Moderate (Medium Risk Limit)", "Aggressive (High Risk Allowed)"],
        index=1  # Default Moderate
    )
    
    custom_instructions = st.text_area(
        "Custom Allocation Instructions (Optional):",
        placeholder="e.g. 'avoid K-THAIESG-A' or 'exclude SCBTHAIESG'",
        help="Directives will be matched against fund codes by the Allocator Agent."
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Process allocation on click
    if st.button("Generate & Validate Portfolio"):
        st.session_state.execution_confirmed = False
        
        # Map inputs to backend parameters
        goal_param = "Growth" if "Growth" in goal_option else ("Dividend" if "Dividend" in goal_option else "Balanced")
        risk_param = "Conservative" if "Conservative" in risk_option else ("Moderate" if "Moderate" in risk_option else "Aggressive")
        
        payload = {
            "investment_budget": investment_budget,
            "financial_goal": goal_param,
            "risk_profile": risk_param,
            "user_instructions": custom_instructions
        }
        
        status_placeholder = st.empty()
        try:
            with status_placeholder.container():
                st.info("🧠 Allocator Agent: Constructing initial asset weights...")
                import time
                time.sleep(0.6)
                st.info("🛡️ Compliance Guard Agent: Running suitability and tax safeguards...")
                time.sleep(0.6)
                st.info("📡 AUQ Supervisor: Fact-checking corporate disclosures & Opportunity Day statements...")
                time.sleep(0.6)
            status_placeholder.empty()
            
            with st.spinner("Finalizing order parameters..."):
                response = requests.post(f"{BACKEND_URL}/api/v1/portfolio/allocate_generic", json=payload)
                if response.status_code == 200:
                    st.session_state.allocation_results = response.json()
                    st.success("Allocation generated successfully!")
                else:
                    st.error(f"Allocation request failed: {response.text}")
        except Exception as e:
            status_placeholder.empty()
            st.error(f"Could not connect to backend: {str(e)}")

# Tabs Layout
tab1, tab2 = st.tabs(["📊 Portfolio Dashboard", "💬 Portfolio Q&A Assistant"])

# ==========================================
# TAB 1: PORTFOLIO DASHBOARD
# ==========================================
with tab1:
    if st.session_state.allocation_results is None:
        st.markdown("""
        <div class='premium-card' style='text-align: center; padding: 60px 20px;'>
            <h4 style='color: #a78bfa; font-weight: 700;'>No portfolio constructed yet</h4>
            <p style='color: #64748b; font-size: 1rem; max-width: 600px; margin: 10px auto 0;'>
                Use the settings panel on the left sidebar to configure your investment budget, strategy, and risk tolerance, then click <strong>"Generate & Validate Portfolio"</strong>.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        data = st.session_state.allocation_results
        portfolio = data["portfolio"]
        compliance = data["compliance"]
        auq = data["auq"]
        trace = data["execution_trace"]
        
        # Metrics Row
        col_m1, col_m2, col_m3 = st.columns(3, gap="medium")
        
        with col_m1:
            st.markdown(f"""
            <div class='premium-card'>
                <div class='metric-label'>Total Allocated Capital</div>
                <div class='metric-value'>฿{portfolio['total_allocated']:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_m2:
            st.markdown(f"""
            <div class='premium-card'>
                <div class='metric-label'>Weighted ESG Rating</div>
                <div class='metric-value' style='background: linear-gradient(90deg, #10b981 0%, #34d399 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                    {portfolio['average_esg_rating']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_m3:
            st.markdown(f"""
            <div class='premium-card'>
                <div class='metric-label'>Portfolio Risk Level</div>
                <div class='metric-value'>{portfolio['average_risk_level']:.1f} / 8.0</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Target Holdings Table
        st.markdown("### 📊 Target Fund Holdings")
        holdings = []
        for item in portfolio["allocations"]:
            holdings.append({
                "Fund Code": item["fund_code"],
                "Fund Name": item["fund_name"],
                "Asset Class": item["asset_class"],
                "ESG Rating": item["esg_rating"],
                "Risk Grade": f"Risk {item['risk_level']}",
                "Weight (%)": f"{item['weight'] * 100:.2f}%",
                "Allocated Amount": f"฿{item['amount']:,.2f}",
                "Estimated Units": f"{item['units']:,.4f}"
            })
            
        st.table(pd.DataFrame(holdings))
        
        # Compliance and AUQ Supervisor Section
        st.markdown("---")
        col_l, col_r = st.columns([1, 1], gap="large")
        
        with col_l:
            st.markdown("### 🛡️ Risk & Suitability Guard")
            
            # Compliance Status Badge
            if compliance["is_compliant"]:
                st.markdown("""
                <div style='background: rgba(16, 185, 129, 0.12); border: 1px solid #10b981; border-radius: 12px; padding: 16px; margin-bottom: 20px;'>
                    <span style='color: #34d399; font-weight: 800; font-size: 1.1rem;'>🟢 SUITABILITY: COMPLIANT</span><br>
                    <span style='color: #a7f3d0; font-size: 0.95rem;'>All asset risk distributions match your KYC profile and statutory list guidelines.</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                violations_html = "".join([f"<li style='margin-bottom: 6px;'>{v}</li>" for v in compliance["violations"]])
                st.markdown(f"""
                <div style='background: rgba(239, 68, 68, 0.12); border: 1px solid #ef4444; border-radius: 12px; padding: 16px; margin-bottom: 20px;'>
                    <span style='color: #fca5a5; font-weight: 800; font-size: 1.1rem;'>🔴 SUITABILITY: NON-COMPLIANT VIOLATIONS</span><br>
                    <ul style='color: #fee2e2; font-size: 0.95rem; margin-top: 10px; margin-bottom: 0;'>
                        {violations_html}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
            # Warnings
            if compliance.get("warnings"):
                warnings_html = "".join([f"<li style='margin-bottom: 4px;'>{w}</li>" for w in compliance["warnings"]])
                st.markdown(f"""
                <div style='background: rgba(245, 158, 11, 0.12); border: 1px solid #f59e0b; border-radius: 12px; padding: 16px; margin-bottom: 20px;'>
                    <span style='color: #fcd34d; font-weight: 700; font-size: 1rem;'>⚠️ Compliance Warnings:</span><br>
                    <ul style='color: #fef3c7; font-size: 0.9rem; margin-top: 8px; margin-bottom: 0;'>
                        {warnings_html}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
            with st.expander("🛠️ View Self-Healing Audit Trail (Compliance Execution Log)"):
                for step in trace:
                    st.markdown(f"`{step}`")
                    
        with col_r:
            st.markdown("### 📡 AUQ Supervisor Oversight")
            
            # Status badge
            status = auq.get("status", "APPROVED")
            if status == "APPROVED":
                status_html = "<div class='status-approved' style='margin-bottom: 15px; width: 100%; text-align: center;'>🟢 STATUS: APPROVED FOR DIRECT EXECUTION</div>"
            elif status == "TEMPORARY_PAUSE":
                status_html = "<div class='status-pause' style='margin-bottom: 15px; width: 100%; text-align: center;'>⚠️ STATUS: TEMPORARY PAUSE (RESOLVING AMBIGUITY)</div>"
            else:
                status_html = "<div class='status-escalated' style='margin-bottom: 15px; width: 100%; text-align: center;'>🚨 STATUS: ESCALATED TO CFA/FUND MANAGER</div>"
                
            st.markdown(status_html, unsafe_allow_html=True)
            
            auq_color = "#34d399" if auq["uncertainty_rating"] == "LOW" else ("#fbbf24" if auq["uncertainty_rating"] == "MEDIUM" else "#f87171")
            
            # Confidence Panel
            st.markdown(f"""
            <div class='premium-card' style='display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; margin-bottom: 15px;'>
                <div class='metric-label' style='text-align: center;'>Confidence Index</div>
                <div style='font-size: 3rem; font-weight: 900; color: {auq_color}; margin: 8px 0;'>{auq['confidence_score']}%</div>
                <div style='font-size: 0.95rem; font-weight: 700; color: {auq_color}; text-transform: uppercase;'>{auq['uncertainty_rating']} UNCERTAINTY</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Uncertainty Splits
            st.markdown(f"""
            <div style='display: flex; gap: 10px; margin-bottom: 15px;'>
                <div class='premium-card' style='flex: 1; text-align: center; padding: 12px; margin-bottom: 0;'>
                    <div class='metric-label' style='font-size: 0.7rem;'>Epistemic Penalty</div>
                    <div style='font-size: 1.3rem; font-weight: 800; color: #f87171;'>-{auq.get('epistemic_uncertainty_score', 0.0):.1f}%</div>
                </div>
                <div class='premium-card' style='flex: 1; text-align: center; padding: 12px; margin-bottom: 0;'>
                    <div class='metric-label' style='font-size: 0.7rem;'>Aleatoric Penalty</div>
                    <div style='font-size: 1.3rem; font-weight: 800; color: #fbbf24;'>-{auq.get('aleatoric_uncertainty_score', 0.0):.1f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"**Audit Recommendation:** {auq['recommendation']}")
            st.markdown("**Confidence Factors Checked:**")
            for reason in auq["reasons"]:
                st.markdown(f"• {reason}")
                
            # Explainable AI (XAI) Justifications
            xai_list = auq.get("xai_justifications", [])
            if xai_list:
                st.markdown("<br>##### ⚠️ Explainable AI (XAI) Risk Disclosures", unsafe_allow_html=True)
                for justification in xai_list:
                    formatted_just = justification.replace('\n', '<br>')
                    st.markdown(f"""
                    <div style='border-left: 4px solid #ef4444; background: rgba(239, 68, 68, 0.08); padding: 14px; margin-bottom: 10px; border-radius: 4px; font-size: 0.9rem; line-height: 1.5;'>
                        {formatted_just}
                    </div>
                    """, unsafe_allow_html=True)
                    
            # Structured Reasoning Trace Expander
            trace_list = auq.get("structured_reasoning_trace", [])
            if trace_list:
                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander("🧠 View Agentic Brain (Structured Reasoning Trace)"):
                    for step in trace_list:
                        st.code(step, language="bash")
                
            # Execution Control / Manual Override Switch
            st.markdown("---")
            requires_override = auq["requires_override"]
            
            if requires_override:
                st.warning("🛑 High uncertainty / Warning flags are present. An override is required to purchase.")
                override_approved = st.checkbox("Approve Manual Decision Override (HITL Registry Override)")
                
                # Execute purchase
                if st.button("Execute Portfolio Purchase", disabled=not override_approved):
                    st.session_state.execution_confirmed = True
            else:
                if st.button("Execute Portfolio Purchase"):
                    st.session_state.execution_confirmed = True
                    
            if st.session_state.execution_confirmed:
                st.success("🎉 Trade orders generated and dispatched to the brokerage API!")
                st.markdown(f"""
                <div class='premium-card' style='border-left: 5px solid #10b981; background: rgba(16, 185, 129, 0.05); padding: 18px;'>
                    <strong>Executed Trade Orders:</strong><br>
                    • Capital Amount Routed: ฿{portfolio['total_allocated']:,.2f}<br>
                    • Risk Profile Locked: {portfolio['risk_profile']}<br>
                    • Order ID: PORT-GEN-{hash(portfolio['total_allocated']) % 1000000}
                </div>
                """, unsafe_allow_html=True)

# ==========================================
# TAB 2: PORTFOLIO Q&A ASSISTANT
# ==========================================
with tab2:
    st.markdown("### 💬 Chat with the Portfolio Construction Agent")
    st.markdown("Ask questions about approved funds, ESG parameters, and custom strategy limitations:")
    
    # Preset quick-click queries
    presets = [
        "What are the ESG ratings of the available funds?",
        "Which fund has the lowest risk level?",
        "Can I customize allocations to exclude certain funds?",
        "What is the difference between Growth and Balanced strategy?"
    ]
    
    preset_cols = st.columns(len(presets))
    clicked_preset = None
    for idx, preset_text in enumerate(presets):
        with preset_cols[idx]:
            if st.button(preset_text, key=f"preset_{idx}"):
                clicked_preset = preset_text
                
    st.markdown("---")
    
    # Display Chat History
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.markdown(f"""
            <div class='chat-bubble chat-user'>
                {chat["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
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
            
    # Chat Input
    chat_query = st.chat_input("Ask a portfolio or screening question...")
    
    if clicked_preset:
        chat_query = clicked_preset
        
    if chat_query:
        # Append User input
        st.session_state.chat_history.append({"role": "user", "content": chat_query})
        st.markdown(f"<div class='chat-bubble chat-user'>{chat_query}</div>", unsafe_allow_html=True)
        
        # Query API
        with st.spinner("Searching regulatory documents..."):
            try:
                payload = {"query": chat_query}
                response = requests.post(f"{BACKEND_URL}/api/v1/tax/query", json=payload)
                if response.status_code == 200:
                    res_data = response.json()
                    answer = res_data["answer"]
                    sources = res_data["retrieved_contexts"]
                    
                    st.session_state.chat_history.append({
                        "role": "agent",
                        "content": answer,
                        "sources": sources
                    })
                    
                    st.rerun()
                else:
                    st.error(f"Query API failed: {response.text}")
            except Exception as e:
                st.error(f"Could not connect to backend: {str(e)}")
