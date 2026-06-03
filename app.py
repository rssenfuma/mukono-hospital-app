import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import joblib

# ==============================================================================
# 1. GLOBAL PAGE ARCHITECTURE & PROFESSIONAL STYLING
# ==============================================================================
st.set_page_config(
    page_title="MGH-Neonates",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Institutional CSS Injection for an attractive, professional medical theme
st.markdown("""
    <style>
    /* Main Background & Fonts */
    .stApp { background-color: #FAFAFA; }
    body, p, div { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    
    /* ENFORCE ABSOLUTE SOLID BLACK FOR ALL INTERFACE MARKDOWN FIELDS */
    label, p, span, h1, h2, h3, h4, h5, h6, .stMarkdown, div[data-testid="stMarkdownContainer"] p {
        color: #000000 !important;
    }
    
    /* Header Banners */
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
    
    /* Section Containers */
    .section-card {
        background-color: #FFFFFF;
        padding: 22px;
        border-radius: 8px;
        border-left: 5px solid #3B82F6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        margin-bottom: 20px;
    }
    .section-title { font-size: 18px; font-weight: 600; color: #000000 !important; margin-bottom: 15px; }
    
    /* Custom Sidebar Aesthetics */
    .sidebar-title { font-size: 19px; font-weight: 700; color: #1E3A8A !important; border-bottom: 2px solid #E5E7EB; padding-bottom: 8px; }
    
    /* Professional Executive Authorization Canvas Summary */
    .decision-canvas {
        background-color: #F1F5F9;
        border: 2px dashed #94A3B8;
        padding: 24px;
        border-radius: 12px;
        margin-top: 25px;
        margin-bottom: 15px;
    }
    
    /* High-visibility decision banner */
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

# Main Banner Layout
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
# 2. LOCAL DATA STORAGE AND MANAGEMENT SUBSYSTEM
# ==============================================================================
DB_FILE = "saved_predictions.csv"

rf_model = joblib.load("models/rf_model.joblib")
scaler = joblib.load("models/scaler.joblib")
encoders = joblib.load("models/categorical_encoders.joblib")

def save_prediction_to_records(patient_data):
    """Appends evaluated clinical factors and system decisions to a permanent local CSV ledger."""
    df = pd.DataFrame([patient_data])
    if not os.path.exists(DB_FILE):
        df.to_csv(DB_FILE, index=False)
    else:
        df.to_csv(DB_FILE, mode='a', header=False, index=False)

# ==============================================================================
# 3. CLINICAL DATA INPUT PANEL (SIDEBAR) WITH AUTO-GENERATED ID
# ==============================================================================
st.sidebar.markdown('<div class="sidebar-title">📋 Clinical Entry Panel</div>', unsafe_allow_html=True)
st.sidebar.write("")

# Section 3.1: Automatic Unique Patient Tracking Meta
st.sidebar.markdown("<div style='color:#000000; font-weight:bold; margin-bottom:5px;'> Patient Identification</div>", unsafe_allow_html=True)

auto_generated_id = f"IPNO-{datetime.now().strftime('%Y%m%d-%H%M')}"
patient_id = st.sidebar.text_input(
    "Neonatal Register ID / IPNO Number", 
    value=auto_generated_id, 
    label_visibility="collapsed",
    help="Automatically generated based on date and time. Can be manually changed if needed."
)

# Section 3.2: High-Weight Predictors (Top 4 Features Verified in Chapter 6)
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

# Section 3.3: Secondary Clinical Covariates
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
# 4. RANDOM FOREST MACHINE LEARNING PREDICTION ENGINE
# ==============================================================================

try:

    mode_delivery_encoded = encoders['Mode_of_Delivery'].transform(
        [mode_of_delivery]
    )[0]

    sex_encoded = encoders['Sex_of_Neonate'].transform(
        [sex_neonate]
    )[0]

    feeding_encoded = encoders['Feeding_Type_at_Discharge'].transform(
        [feeding_type]
    )[0]

    discharge_encoded = encoders['Discharge_Condition'].transform(
        [discharge_condition]
    )[0]

    input_df = pd.DataFrame([{
        'Maternal_Age': maternal_age,
        'Parity': parity,
        'ANC_Attendance_Visits': anc_visits,
        'Mode_of_Delivery': mode_delivery_encoded,
        'Sex_of_Neonate': sex_encoded,
        'Birth_Weight_kg': birth_weight,
        'Gestational_Age_Weeks': gestational_age,
        'Apgar_5min': apgar_score,
        'Feeding_Type_at_Discharge': feeding_encoded,
        'Duration_of_Initial_Stay_Days': length_of_stay,
        'Discharge_Condition': discharge_encoded
    }])

    input_scaled = scaler.transform(input_df)

    readmission_probability = float(
        rf_model.predict_proba(input_scaled)[0][1]
    )

except Exception as e:

    st.error(f"Model Prediction Error: {e}")

    readmission_probability = 0.50

# Resolve precise guidelines text and routing paths based on metrics
if readmission_probability >= 0.70:
    risk_tier, alert_color = "High Risk", "error"
    guidelines = "🚨 CRITICAL INTERVENTION ALGORITHM TRIGGERED (RED TIER): Ward Management: HALT standard discharge workflows immediately. | Clinical Review: Arrange a mandatory priority re-evaluation by a Senior Pediatric Registrar within 12 hours. | Continuity of Care: Establish direct electronic linkage to Community Health Teams (VHTs) for prioritized home follow-up visits within 48 hours."
    final_decision_path = "🔴 MANDATORY PROTOCOL: Absolute Hold on Discharge & Transfer directly to Neonatal Inpatient Unit for Acute Care"
elif readmission_probability >= 0.35:
    risk_tier, alert_color = "Medium Risk", "warning"
    guidelines = "⚠️ MODERATE CAUTION STRATIFICATION REQUIRED (YELLOW TIER): Ward Management: Clear for discharge only after nursing staff double-check maternal breastfeeding mechanics. | Education: Provide direct, face-to-face maternal counseling on neonatal thermal regulation guidelines. | Follow-Up: Automatically place the profile onto the hospital's Day-7 phone-based automated wellness tracking queue."
    final_decision_path = "APPROVED DISCHARGE: Clear for Postnatal Release following successful Nurse-Verified Feeding & Warmth Audits"
else:
    risk_tier, alert_color = "Low Risk", "success"
    guidelines = "✅ ROUTINE OUTPATIENT CARE AUTHORIZED (GREEN TIER): Ward Management: Authorized for standard, timely postnatal ward discharge. | Documentation: Provide standard maternal postpartum wellness literature and print the routine UNEPI immunization tracking schedule."
    final_decision_path = "🟢 ROUTINE POSTNATAL DISCHARGE: Authorize Standard Release with baseline UNEPI Immunization Package"

# ==============================================================================
# 5. REAL-TIME INTERACTION & TRIAGE OUTCOME SCREEN
# ==============================================================================
st.markdown("""
    <div class="section-card">
        <div class="section-title">Real-Time Patient Evaluation Triage Engine</div>
        <p style="color: #000000; font-size: 14px; margin-top:-10px;">Adjust the medical parameters on the left pane and execute the button below to parse patient parameters against the Random Forest classifier matrix.</p>
    </div>
""", unsafe_allow_html=True)

# Maintain panel visibility using session state
if "assessment_triggered" not in st.session_state:
    st.session_state.assessment_triggered = False

if st.button("Execute Clinical Risk Assessment", type="primary"):
    st.session_state.assessment_triggered = True

# Display Real-Time Analysis if triggered
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
            <p style="font-size:13px; color:#000000; margin:0;">Based on the mathematical parameters evaluated above, the system has calculated the following definitive action route for the medical team.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"Authoritative Ward Disposition Route:")
    st.markdown(f"""<div class="final-decision-banner">{final_decision_path}</div>""", unsafe_allow_html=True)

# ==============================================================================
# PERSISTENT AUTHORIZATION & CLINICIAN SIGN-OFF CANVAS (FORCED HTML BLACK LABELS)
# ==============================================================================
st.write("")
st.markdown("<div style='color:#000000; font-size:22px; font-weight:bold; margin-top:20px; border-bottom:2px solid #3B82F6; padding-bottom:5px;'>Case Validation & Verification</div>", unsafe_allow_html=True)
st.write("")

# Forced Black Title Label for Notes Area
st.markdown("<div style='color:#000000; font-size:15px; font-weight:bold; margin-bottom:5px;'>Diagnostic Notes:</div>", unsafe_allow_html=True)
clinician_notes = st.text_area(
    "Clinical Notes Label Hidden",
    placeholder="Type mandatory medical comments here before saving...",
    label_visibility="collapsed"
)

col_sig, col_space = st.columns([2, 2])
with col_sig:
    st.write("")
    # Forced Black Title Label for Doctor Sign-off Input Area
    st.markdown("<div style='color:#000000; font-size:15px; font-weight:bold; margin-bottom:5px;'>Attending Doctor (Full Name & Cadre Code):</div>", unsafe_allow_html=True)
    signature = st.text_input(
        "Attending Doctor", 
        placeholder="e.g., Dr. Ronnie Ssenfuma - Paediatrician",
        label_visibility="collapsed"
    )
    
st.write("")
if st.button("💾 Save Decision to Clinical Ledger"):
    if not signature:
        st.error("Action Blocked: The attending clinician must provide an electronic text signature/code before saving.")
    else:
        patient_record = {
            "Patient Register ID": patient_id,
            "Consultation Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Risk Stratification Tier": risk_tier,
            "Readmission Risk Score (%)": round(readmission_probability * 100, 1),
            "System Directed Care Text": guidelines,
            "Sex of Neonate": sex_neonate,
            "Birth Weight (kg)": birth_weight,
            "Gestational Age (Weeks)": gestational_age,
            "Maternal Age (Years)": maternal_age,
            "Duration of Initial Hospital Stay (Days)": length_of_stay,
            "5-Min Apgar Score": apgar_score,
            "ANC Visits Attended": anc_visits,
            "Maternal Parity": parity,
            "Mode of Delivery": mode_of_delivery,
            "Feeding Protocol": feeding_type,
            "Physical Discharge Condition": discharge_condition,
            "Authoritative Disposition Route Taken": final_decision_path,
            "Clinical Notes": clinician_notes if clinician_notes else "Adhered to calculated baseline parameters.",
            "Attending Clinician": signature
        }
        save_prediction_to_records(patient_record)
        st.success(f"🎉 Success! Profile for {patient_id} recorded safely into the clinical audit trail.")
        st.toast(f"💾 Profile for {patient_id} recorded successfully!", icon="🎉")
        st.session_state.assessment_triggered = False  # Reset panel memory state
        st.button("🔄 Refresh Application View", on_click=st.rerun)

# ==============================================================================
# 6. EXPANDED HISTORICAL AUDIT TRAIL LOG SHEET
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
        
        st.dataframe(
            history_df.sort_values(by="Consultation Timestamp", ascending=False),
            use_container_width=True,
            hide_index=True
        )
        
        csv_data = history_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Export Excel Spreadsheet",
            data=csv_data,
            file_name=f"mgh_cdss_audit_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"Error parsing historical tracking files: {e}")
else:
    st.info("No records are currently logged in the relational database ledger.")
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
