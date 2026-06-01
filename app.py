import streamlit as st
import pandas as pd
import numpy as np
import os
import time
from datetime import datetime

# ==============================================================================
# 1. GLOBAL PAGE ARCHITECTURE & PROFESSIONAL STYLING
# ==============================================================================
st.set_page_config(
    page_title="MGH-Neonates",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp { background-color: #FAFAFA; }
    body, p, div { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    label, p, span, h1, h2, h3, h4, h5, h6, .stMarkdown, div[data-testid="stMarkdownContainer"] p {
        color: #000000 !important;
    }
    .hospital-header { 
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%); 
        padding: 20px; 
        border-radius: 10px; 
        color: white !important; 
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .hospital-title { font-size: 30px; font-weight: 700; margin: 0; letter-spacing: 0.5px; color: white !important; }
    .hospital-subtitle { font-size: 15px; color: #E0E7FF !important; margin: 5px 0 0 0; opacity: 0.9; }
    .section-card {
        background-color: #FFFFFF;
        padding: 22px;
        border-radius: 8px;
        border-left: 5px solid #3B82F6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        margin-bottom: 20px;
    }
    .section-title { font-size: 18px; font-weight: 600; color: #000000 !important; margin-bottom: 15px; }
    .sidebar-title { font-size: 19px; font-weight: 700; color: #1E3A8A !important; border-bottom: 2px solid #E5E7EB; padding-bottom: 8px; }
    .decision-canvas {
        background-color: #F1F5F9;
        border: 2px dashed #94A3B8;
        padding: 24px;
        border-radius: 12px;
        margin-top: 25px;
        margin-bottom: 15px;
    }
    .final-decision-banner {
        background-color: #FFFFFF;
        padding: 16px;
        border-radius: 8px;
        border: 1.5px solid #CBD5E1;
        font-size: 16px;
        color: #000000 !important;
        font-weight: 600;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="hospital-header">
        <div class="hospital-title">🏥 MUKONO GENERAL HOSPITAL</div>
        <div class="hospital-subtitle">Point-of-Care Neonatal 28-Day Readmission Risk Triage Platform — Health Informatics Prototype</div>
    </div>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. USER SECURITY STORAGE & DATABASE SUBSYSTEM
# ==============================================================================
USERS_FILE = "system_users.csv"

def load_system_users():
    defaults = {
        "admin": {"password": "mgh2026", "role": "admin"},
        "ronnie": {"password": "informatics25", "role": "user"},
        "doctor": {"password": "mukonohospital", "role": "user"}
    }
    if not os.path.exists(USERS_FILE):
        rows = []
        for username, info in defaults.items():
            rows.append({"username": username, "password": info["password"], "role": info["role"]})
        pd.DataFrame(rows).to_csv(USERS_FILE, index=False)
        return defaults
    else:
        try:
            df = pd.read_csv(USERS_FILE)
            user_dict = {}
            for _, row in df.iterrows():
                u_name = str(row['username']).strip().lower()
                user_dict[u_name] = {
                    "password": str(row['password']).strip(),
                    "role": str(row['role']).strip().lower()
                }
            return user_dict
        except:
            return defaults

def save_new_user_to_system(username, password, role):
    cleaned_user = str(username).strip().lower()
    cleaned_pass = str(password).strip()
    cleaned_role = str(role).strip().lower()
    
    if os.path.exists(USERS_FILE):
        try:
            df = pd.read_csv(USERS_FILE)
            df['username'] = df['username'].astype(str).str.strip().str.lower()
        except:
            df = pd.DataFrame(columns=["username", "password", "role"])
    else:
        df = pd.DataFrame(columns=["username", "password", "role"])
    
    df = df[df['username'] != cleaned_user]
    new_row = pd.DataFrame([{"username": cleaned_user, "password": cleaned_pass, "role": cleaned_role}])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(USERS_FILE, index=False)

USER_CREDENTIALS = load_system_users()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# ==============================================================================
# 3. CLINICAL GATEWAY LOGIN TERMINAL
# ==============================================================================
if not st.session_state.authenticated:
    st.markdown("""
        <div class="section-card" style="border-left: 5px solid #EF4444;">
            <div class="section-title" style="color: #DC2626 !important;">🔒 Secure Clinical Gateway Access Authorization Required</div>
            <p style="color: #000000; font-size: 14px; margin-top:-10px;">This platform contains clinical evaluation algorithms and audited registry data streams. Please authenticate using authorized staff credentials.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        st.markdown("<div style='color:#000000; font-size:14px; font-weight:bold; margin-bottom:5px;'>User ID / System Username:</div>", unsafe_allow_html=True)
        input_username = st.text_input("Username Input Area", placeholder="Enter official username...", label_visibility="collapsed")
    with col_l2:
        st.markdown("<div style='color:#000000; font-size:14px; font-weight:bold; margin-bottom:5px;'>Security Passcode / Password:</div>", unsafe_allow_html=True)
        input_password = st.text_input("Password Input Area", type="password", placeholder="Enter secure password...", label_visibility="collapsed")
        
    st.write("")
    if st.button("Authorize Session Identity", type="primary"):
        target_user = input_username.strip().lower()
        if target_user in USER_CREDENTIALS and USER_CREDENTIALS[target_user]["password"] == input_password.strip():
            st.session_state.authenticated = True
            st.session_state.current_user = target_user
            st.success(f"Authorization Confirmed. Welcome back, {target_user}")
            st.rerun()
        else:
            st.error("Authentication Refused: The credentials provided do not match any authorized keys.")
    st.stop()

if st.sidebar.button("🔒 Terminate Session (Logout)"):
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.assessment_triggered = False
    st.rerun()

st.sidebar.markdown(f"<div style='color: #1E3A8A; font-size:12px; font-weight:bold;'>Active User: {st.session_state.current_user.upper()}</div>", unsafe_allow_html=True)
active_role = USER_CREDENTIALS[st.session_state.current_user]["role"]

# ==============================================================================
# 4. DATA LOGGING SUBSYSTEM (FIXED DYNAMIC COLUMNS MATCHING)
# ==============================================================================
DB_FILE = "saved_predictions.csv"

def save_prediction_to_records(patient_data):
    df = pd.DataFrame([patient_data])
    if not os.path.exists(DB_FILE) or os.path.getsize(DB_FILE) == 0:
        df.to_csv(DB_FILE, index=False)
    else:
        try:
            # Read existing schema to keep old tracking columns aligned if they exist
            existing_df = pd.read_csv(DB_FILE)
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df.to_csv(DB_FILE, index=False)
        except:
            df.to_csv(DB_FILE, index=False)

# ==============================================================================
# 5. CLINICAL DATA INPUT PANEL (SIDEBAR)
# ==============================================================================
st.sidebar.markdown('<div class="sidebar-title">📋 Clinical Entry Panel</div>', unsafe_allow_html=True)
st.sidebar.write("")

st.sidebar.markdown("<div style='color:#000000; font-weight:bold; margin-bottom:5px;'>📌 Patient Identification</div>", unsafe_allow_html=True)
auto_generated_id = f"IPNO-{datetime.now().strftime('%Y%m%d-%H%M')}"
patient_id = st.sidebar.text_input("Neonatal Register ID / IPNO Number", value=auto_generated_id, label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown("<div style='color:#000000; font-weight:bold;'>Core Mathematical Predictors</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='color:#000000; font-size:14px; margin-top:5px;'>Birth Weight (kg)</div>", unsafe_allow_html=True)
birth_weight = st.sidebar.slider("Birth Weight (kg)", min_value=0.5, max_value=5.5, value=2.9, step=0.1, label_visibility="collapsed")

st.sidebar.markdown("<div style='color:#000000; font-size:14px; margin-top:5px;'>Maternal Age (Years)</div>", unsafe_allow_html=True)
maternal_age = st.sidebar.slider("Maternal Age (Years)", min_value=12, max_value=45, value=30, step=1, label_visibility="collapsed")

st.sidebar.markdown("<div style='color:#000000; font-size:14px; margin-top:5px;'>Duration of Initial Hospital Stay (Days)</div>", unsafe_allow_html=True)
length_of_stay = st.sidebar.slider("Duration of Initial Hospital Stay (Days)", min_value=1, max_value=30, value=3, step=1, label_visibility="collapsed")

st.sidebar.markdown("<div style='color:#000000; font-size:14px; margin-top:5px;'>Gestational Age (Weeks)</div>", unsafe_allow_html=True)
gestational_age = st.sidebar.slider("Gestational Age (Weeks)", min_value=20, max_value=42, value=35, step=1, label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown("<div style='color:#000000; font-weight:bold;'>📊 Supplementary Clinical Metrics</div>", unsafe_allow_html=True)

st.sidebar.markdown("<div style='color:#000000; font-size:14px; margin-top:5px;'>5-Minute Apgar Vitality Score</div>", unsafe_allow_html=True)
apgar_score = st.sidebar.slider("5-Minute Apgar Vitality Score", min_value=0, max_value=10, value=7, step=1, label_visibility="collapsed")

st.sidebar.markdown("<div style='color:#000000; font-size:14px; margin-top:5px;'>Antenatal Care (ANC) Attendance</div>", unsafe_allow_html=True)
anc_visits = st.sidebar.slider("Antenatal Care (ANC) Attendance", min_value=0, max_value=12, value=4, step=1, label_visibility="collapsed")

st.sidebar.markdown("<div style='color:#000000; font-size:14px; margin-top:5px;'>Maternal Parity (Total Deliveries)</div>", unsafe_allow_html=True)
parity = st.sidebar.number_input("Maternal Parity (Total Deliveries)", min_value=1, max_value=15, value=2, step=1, label_visibility="collapsed")

st.sidebar.markdown("<div style='color:#000000; font-size:14px; margin-top:5px;'>Mode of Delivery</div>", unsafe_allow_html=True)
mode_of_delivery = st.sidebar.selectbox("Mode of Delivery", ["Normal Vaginal Delivery", "Caesarean Section", "Assisted Vaginal Delivery"], label_visibility="collapsed")

st.sidebar.markdown("<div style='color:#000000; font-size:14px; margin-top:5px;'>Sex of Neonate</div>", unsafe_allow_html=True)
sex_neonate = st.sidebar.radio("Sex of Neonate", ["Male", "Female"], horizontal=True, label_visibility="collapsed")

st.sidebar.markdown("<div style='color:#000000; font-size:14px; margin-top:5px;'>Feeding Type at Discharge</div>", unsafe_allow_html=True)
feeding_type = st.sidebar.selectbox("Feeding Type at Discharge", ["Exclusive Breastfeeding", "Mixed Feeding", "Formula Only"], label_visibility="collapsed")

st.sidebar.markdown("<div style='color:#000000; font-size:14px; margin-top:5px;'>Discharge Physical Condition</div>", unsafe_allow_html=True)
discharge_condition = st.sidebar.selectbox("Discharge Physical Condition", ["Stable", "Improved", "Critical"], label_visibility="collapsed")

# ==============================================================================
# 6. RANDOM FOREST PREDICTIVE SIMULATION PATTERN
# ==============================================================================
base_score = 0.50
if birth_weight < 2.5: base_score += 0.15      
if birth_weight >= 3.5: base_score -= 0.05
if maternal_age < 18 or maternal_age > 38: base_score += 0.12 
if length_of_stay > 5: base_score += 0.14      
if gestational_age < 37: base_score += 0.12    
if apgar_score < 6: base_score += 0.10          

readmission_probability = float(np.clip(base_score, 0.15, 0.95))

if readmission_probability >= 0.70:
    risk_tier, alert_color = "High Risk", "error"
    guidelines = "🚨 CRITICAL INTERVENTION ALGORITHM TRIGGERED (RED TIER): HALT standard discharge workflows immediately. Arrange immediate senior pediatric registrar review."
    final_decision_path = "🔴 MANDATORY PROTOCOL: Absolute Hold on Discharge & Transfer to Neonatal Inpatient Unit"
elif readmission_probability >= 0.35:
    risk_tier, alert_color = "Medium Risk", "warning"
    guidelines = "⚠️ MODERATE CAUTION REQUIRED (YELLOW TIER): Verify breastfeeding mechanics. Queue profile for Day-7 follow-up."
    final_decision_path = "🟡 APPROVED DISCHARGE: Release after successful Nurse-Verified Feeding Audits"
else:
    risk_tier, alert_color = "Low Risk", "success"
    guidelines = "✅ ROUTINE OUTPATIENT CARE AUTHORIZED (GREEN TIER): Authorized for standard ward discharge. Provide standard postnatal counseling."
    final_decision_path = "🟢 ROUTINE POSTNATAL DISCHARGE: Authorize Standard Release"

# ==============================================================================
# 7. REAL-TIME INTERACTION & TRIAGE OUTCOME SCREEN
# ==============================================================================
st.markdown("""
    <div class="section-card">
        <div class="section-title">Real-Time Patient Evaluation Triage Engine</div>
        <p style="color: #000000; font-size: 14px; margin-top:-10px;">Adjust parameters on the left pane and execute assessment below.</p>
    </div>
""", unsafe_allow_html=True)

if "assessment_triggered" not in st.session_state:
    st.session_state.assessment_triggered = False

if st.button("Execute Clinical Risk Assessment", type="primary"):
    st.session_state.assessment_triggered = True

if st.session_state.assessment_triggered:
    st.write("")
    st.markdown(f"Diagnostic Breakdown for: {patient_id}")
    status_text = f"Classification Status: {risk_tier.upper()} | Calculated Risk Ratio: {readmission_probability*100:.1f}%"
    
    if alert_color == "error":
        st.markdown(f"""<div style="background-color: #FEE2E2; border-left: 6px solid #DC2626; padding: 15px; border-radius: 4px; margin-bottom: 15px;"><strong style="color: #991B1B; font-size: 16px;">{status_text}</strong></div>""", unsafe_allow_html=True)
    elif alert_color == "warning":
        st.markdown(f"""<div style="background-color: #FEF3C7; border-left: 6px solid #D97706; padding: 15px; border-radius: 4px; margin-bottom: 15px;"><strong style="color: #92400E; font-size: 16px;">{status_text}</strong></div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div style="background-color: #D1FAE5; border-left: 6px solid #059669; padding: 15px; border-radius: 4px; margin-bottom: 15px;"><strong style="color: #065F46; font-size: 16px;">{status_text}</strong></div>""", unsafe_allow_html=True)
        
    st.info(guidelines)
    
    st.markdown("""
        <div class="decision-canvas">
            <h4 style="color:#000000; margin:0 0 5px 0;">CLINICAL DIRECTIVE</h4>
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""<div class="final-decision-banner">{final_decision_path}</div>""", unsafe_allow_html=True)

# ==============================================================================
# 8. CASE VALIDATION & VERIFICATION (PRECISE COMPREHENSIVE DICTIONARY MAPPING)
# ==============================================================================
st.write("")
st.markdown("<div style='color:#000000; font-size:22px; font-weight:bold; margin-top:20px; border-bottom:2px solid #3B82F6; padding-bottom:5px;'>Case Validation & Verification</div>", unsafe_allow_html=True)
st.write("")

st.markdown("<div style='color:#000000; font-size:15px; font-weight:bold; margin-bottom:5px;'>Diagnostic Notes:</div>", unsafe_allow_html=True)
clinician_notes = st.text_area("Clinical Notes Label Hidden", placeholder="Type mandatory comments...", label_visibility="collapsed")

col_sig, col_space = st.columns([2, 2])
with col_sig:
    st.write("")
    st.markdown("<div style='color:#000000; font-size:15px; font-weight:bold; margin-bottom:5px;'>Attending Doctor (Full Name & Cadre Code):</div>", unsafe_allow_html=True)
    signature = st.text_input("Attending Doctor", placeholder="e.g., Dr. Ronnie Ssenfuma", label_visibility="collapsed")
    
st.write("")

if st.button("💾 Save Decision to Clinical Ledger"):
    if not signature:
        st.error("Action Blocked: Clinician signature required.")
    else:
        # EXACTLY MAPPED LABELS BASED ON THE STEP-BY-STEP USER LAYOUT REQUEST
        patient_record = {
            "📌 Patient Identification": patient_id,
            "Consultation Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            
            # Core Mathematical Predictors
            "Core Mathematical Predictors: Birth Weight (kg)": birth_weight,
            "Core Mathematical Predictors: Maternal Age (Years)": maternal_age,
            "Core Mathematical Predictors: Duration of Initial Hospital Stay (Days)": length_of_stay,
            "Core Mathematical Predictors: Gestational Age (Weeks)": gestational_age,
            
            # 📊 Supplementary Clinical Metrics
            "📊 Supplementary Clinical Metrics: 5-Minute Apgar Vitality Score": apgar_score,
            "📊 Supplementary Clinical Metrics: Antenatal Care (ANC) Attendance": anc_visits,
            "📊 Supplementary Clinical Metrics: Maternal Parity (Total Deliveries)": parity,
            "📊 Supplementary Clinical Metrics: Mode of Delivery": mode_of_delivery,
            "📊 Supplementary Clinical Metrics: Sex of Neonate": sex_neonate,
            "📊 Supplementary Clinical Metrics: Feeding Type at Discharge": feeding_type,
            "📊 Supplementary Clinical Metrics: Discharge Physical Condition": discharge_condition,
            
            # Diagnostic Breakdown & Analysis Outputs
            "Diagnostic Breakdown: Classification Status": risk_tier.upper(),
            "Diagnostic Breakdown: Calculated Risk Ratio": f"{readmission_probability*100:.1f}%",
            "Diagnostic Breakdown: Context Guidelines": guidelines,
            
            # Decision Outcomes & Signature Details
            "CLINICAL DIRECTIVE / Final Decision Approved": final_decision_path,
            "Diagnostic Notes": clinician_notes,
            "Attending Doctor": signature
        }
        
        save_prediction_to_records(patient_record)
        st.success(f"🎉 Success! Comprehensive entry profile completely parsed and recorded.")
        st.session_state.assessment_triggered = False
        time.sleep(0.5)
        st.rerun()

# ==============================================================================
# 9. CLINICAL AUDIT LEDGER (DISPLAYS DYNAMIC DATAFRAME IN INTERFACE)
# ==============================================================================
st.write("")
st.write("")
st.markdown("""
    <div class="section-card">
        <div class="section-title">Clinical Audit Ledger</div>
        <p style="color: #000000; font-size: 14px; margin-top:-10px;">Retrospective data matrix capturing complete baseline details, demographics, infant sex, and triage choices for future administrative audits and clinical research.</p>
    </div>
""", unsafe_allow_html=True)

if os.path.exists(DB_FILE) and os.path.getsize(DB_FILE) > 0:
    try:
        history_df = pd.read_csv(DB_FILE)
        st.metric(label="Total System Logged Consultations", value=len(history_df))
        
        # Displays all loaded metrics sequentially on screen in sorted matrix views
        st.dataframe(
            history_df.sort_values(by="Consultation Timestamp", ascending=False),
            use_container_width=True,
            hide_index=True
        )
        
        if active_role == "admin":
            csv_data = history_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Export Excel Spreadsheet",
                data=csv_data,
                file_name=f"mgh_cdss_audit_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
        else:
            st.info("ℹ️ Excel sheet data export options are locked for your user level.")
            
    except Exception as e:
        st.error(f"Error parsing database file matrix: {e}")
else:
    st.info("No comprehensive records are currently logged in the local tracking files.")

# ==============================================================================
# 10. ADMINISTRATIVE USER MANAGEMENT HUBS
# ==============================================================================
if active_role == "admin":
    st.write("")
    st.write("")
    st.markdown("""
        <div class="section-card" style="border-left: 5px solid #10B981;">
            <div class="section-title" style="color: #047857 !important;">👥 Administrative Management Console: System User Accounts</div>
            <p style="color: #000000; font-size: 14px; margin-top:-10px;">Register new clinician accounts or change user authorizations here. This panel is hidden from standard users.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_u1, col_u2, col_u3 = st.columns(3)
    with col_u1:
        st.markdown("<div style='color:#000000; font-size:14px; font-weight:bold; margin-bottom:5px;'>New Account Username:</div>", unsafe_allow_html=True)
        new_user = st.text_input("New Username Input", placeholder="e.g., nurse_mary", label_visibility="collapsed")
    with col_u2:
        st.markdown("<div style='color:#000000; font-size:14px; font-weight:bold; margin-bottom:5px;'>Account Access Password:</div>", unsafe_allow_html=True)
        new_pass = st.text_input("New Password Input", type="password", placeholder="Set a secure password...", label_visibility="collapsed")
    with col_u3:
        st.markdown("<div style='color:#000000; font-size:14px; font-weight:bold; margin-bottom:5px;'>Assign Permissions Level:</div>", unsafe_allow_html=True)
        new_role = st.selectbox("New Role Selection", ["user", "admin"], label_visibility="collapsed")
        
    st.write("")
    if st.button("➕ Add & Register Account", type="secondary"):
        cleaned_new_user = new_user.strip().lower()
        cleaned_new_pass = new_pass.strip()
        
        if not cleaned_new_user or not cleaned_new_pass:
            st.error("Registration Blocked: Username and Password fields cannot be empty.")
        else:
            save_new_user_to_system(cleaned_new_user, cleaned_new_pass, new_role)
            st.success(f"🎉 Success! Account '{cleaned_new_user}' registered permanently.")
            time.sleep(0.5)
            st.rerun()
