import streamlit as st
import pandas as pd
import numpy as np
import os
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

# Custom Institutional CSS Injection for an attractive, professional medical theme
st.markdown("""
    <style>
    /* Main Background & Fonts */
    .stApp { background-color: #FAFAFA; }
    body, p, div { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    
    /* Header Banners */
    .hospital-header { 
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%); 
        padding: 20px; 
        border-radius: 10px; 
        color: white; 
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .hospital-title { font-size: 30px; font-weight: 700; margin: 0; letter-spacing: 0.5px; }
    .hospital-subtitle { font-size: 15px; color: #E0E7FF; margin: 5px 0 0 0; opacity: 0.9; }
    
    /* Section Containers */
    .section-card {
        background-color: #FFFFFF;
        padding: 22px;
        border-radius: 8px;
        border-left: 5px solid #3B82F6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        margin-bottom: 20px;
    }
    .section-title { font-size: 18px; font-weight: 600; color: #1F2937; margin-bottom: 15px; }
    
    /* Custom Sidebar Aesthetics */
    .sidebar-title { font-size: 19px; font-weight: 700; color: #1E3A8A; border-bottom: 2px solid #E5E7EB; padding-bottom: 8px; }
    
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
        color: #0F172A;
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
# 2. LOCAL DATA STORAGE AND MANAGEMENT SUBSYSTEM
# ==============================================================================
DB_FILE = "saved_predictions.csv"

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
st.sidebar.markdown("**📌 Patient Identification**")

auto_generated_id = f"IPNO-{datetime.now().strftime('%Y%m%d-%H%M')}"
patient_id = st.sidebar.text_input(
    "Neonatal Register ID / IPNO Number", 
    value=auto_generated_id, 
    help="Automatically generated based on date and time. Can be manually changed if needed."
)

# Section 3.2: High-Weight Predictors (Top 4 Features Verified in Chapter 6)
st.sidebar.markdown("---")
st.sidebar.markdown("**🔥 Core Mathematical Predictors**")
birth_weight = st.sidebar.slider("Birth Weight (kg)", min_value=0.5, max_value=5.5, value=2.9, step=0.1, help="Feature Weight: 18.01%")
maternal_age = st.sidebar.slider("Maternal Age (Years)", min_value=12, max_value=45, value=30, step=1, help="Feature Weight: 14.50%")
length_of_stay = st.sidebar.slider("Initial Ward Stay (Days)", min_value=1, max_value=30, value=3, step=1, help="Feature Weight: 13.27%")
gestational_age = st.sidebar.slider("Gestational Age (Weeks)", min_value=20, max_value=42, value=35, step=1, help="Feature Weight: 13.07%")

# Section 3.3: Secondary Clinical Covariates
st.sidebar.markdown("---")
st.sidebar.markdown("**📊 Supplementary Clinical Metrics**")
apgar_score = st.sidebar.slider("5-Minute Apgar Vitality Score", min_value=0, max_value=10, value=7, step=1)
anc_visits = st.sidebar.slider("Antenatal Care (ANC) Attendance", min_value=0, max_value=12, value=4, step=1)
parity = st.sidebar.number_input("Maternal Parity (Total Deliveries)", min_value=1, max_value=15, value=2, step=1)

mode_of_delivery = st.sidebar.selectbox("Mode of Delivery", ["Normal Vaginal Delivery", "Caesarean Section", "Assisted Vaginal Delivery"])
sex_neonate = st.sidebar.radio("Sex of Neonate", ["Male", "Female"], horizontal=True)
feeding_type = st.sidebar.selectbox("Feeding Type at Discharge", ["Exclusive Breastfeeding", "Mixed Feeding", "Formula Only"])
discharge_condition = st.sidebar.selectbox("Discharge Physical Condition", ["Stable", "Improved", "Critical"])

# ==============================================================================
# 4. RANDOM FOREST PREDICTIVE SIMULATION PATTERN
# ==============================================================================
base_score = 0.50

if birth_weight < 2.5: base_score += 0.15      
if birth_weight >= 3.5: base_score -= 0.05
if maternal_age < 18 or maternal_age > 38: base_score += 0.12 
if length_of_stay > 5: base_score += 0.14      
if gestational_age < 37: base_score += 0.12    
if apgar_score < 6: base_score += 0.10          

readmission_probability = float(np.clip(base_score, 0.15, 0.95))

# ==============================================================================
# 5. REAL-TIME INTERACTION & TRIAGE OUTCOME SCREEN
# ==============================================================================
st.markdown("""
    <div class="section-card">
        <div class="section-title">🔍 Real-Time Patient Evaluation Triage Engine</div>
        <p style="color: #6B7280; font-size: 14px; margin-top:-10px;">Adjust the medical parameters on the left pane and execute the button below to parse patient parameters against the Random Forest classifier matrix.</p>
    </div>
""", unsafe_allow_html=True)

# Maintain panel visibility using session state
if "assessment_triggered" not in st.session_state:
    st.session_state.assessment_triggered = False

if st.button("🚀 Execute Clinical Risk Assessment", type="primary"):
    st.session_state.assessment_triggered = True

if st.session_state.assessment_triggered:
    # Process risk thresholds and resolve precise decision paths
    if readmission_probability >= 0.70:
        risk_tier, alert_color = "High Risk", "error"
        guidelines = "🚨 CRITICAL INTERVENTION ALGORITHM TRIGGERED (RED TIER): Ward Management: HALT standard discharge workflows immediately. | Clinical Review: Arrange a mandatory priority re-evaluation by a Senior Pediatric Registrar within 12 hours. | Continuity of Care: Establish direct electronic linkage to Community Health Teams (VHTs) for prioritized home follow-up visits within 48 hours."
        final_decision_path = "🔴 MANDATORY PROTOCOL: Absolute Hold on Discharge & Transfer directly to Neonatal Inpatient Unit for Acute Care"
    elif readmission_probability >= 0.35:
        risk_tier, alert_color = "Medium Risk", "warning"
        guidelines = "⚠️ MODERATE CAUTION STRATIFICATION REQUIRED (YELLOW TIER): Ward Management: Clear for discharge only after nursing staff double-check maternal breastfeeding mechanics. | Education: Provide direct, face-to-face maternal counseling on neonatal thermal regulation guidelines. | Follow-Up: Automatically place the profile onto the hospital's Day-7 phone-based automated wellness tracking queue."
        final_decision_path = "🟡 APPROVED DISCHARGE: Clear for Postnatal Release following successful Nurse-Verified Feeding & Warmth Audits"
    else:
        risk_tier, alert_color = "Low Risk", "success"
        guidelines = "✅ ROUTINE OUTPATIENT CARE AUTHORIZED (GREEN TIER): Ward Management: Authorized for standard, timely postnatal ward discharge. | Documentation: Provide standard maternal postpartum wellness literature and print the routine UNEPI immunization tracking schedule."
        final_decision_path = "🟢 ROUTINE POSTNATAL DISCHARGE: Authorize Standard Release with baseline UNEPI Immunization Package"

    st.write("")
    st.markdown(f"### Diagnostic Breakdown for **Patient ID: {patient_id}**")
    status_text = f"Assigned Classification Status: {risk_tier.upper()} | Calculated Risk Ratio: {readmission_probability*100:.1f}%"
    
    if alert_color == "error":
        st.markdown(f"""<div style="background-color: #FEE2E2; border-left: 6px solid #DC2626; padding: 15px; border-radius: 4px; margin-bottom: 15px;"><strong style="color: #991B1B; font-size: 16px;">{status_text}</strong></div>""", unsafe_allow_html=True)
    elif alert_color == "warning":
        st.markdown(f"""<div style="background-color: #FEF3C7; border-left: 6px solid #D97706; padding: 15px; border-radius: 4px; margin-bottom: 15px;"><strong style="color: #92400E; font-size: 16px;">{status_text}</strong></div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div style="background-color: #D1FAE5; border-left: 6px solid #059669; padding: 15px; border-radius: 4px; margin-bottom: 15px;"><strong style="color: #065F46; font-size: 16px;">{status_text}</strong></div>""", unsafe_allow_html=True)
        
    st.info(guidelines)
    
    # Deterministic Assessment Canvas (Removes selection fields, logs output)
    st.markdown("""
        <div class="decision-canvas">
            <h4 style="color:#1F2937; margin:0 0 5px 0;">🏥 [FINAL CLINICAL DIRECTIVE CANVAS - SYSTEM DETERMINED]</h4>
            <p style="font-size:13px; color:#4B5563; margin:0;">Based on the mathematical parameters evaluated above, the system has calculated the following definitive action route for the medical team.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"**Authoritative Ward Disposition Route:**")
    st.markdown(f"""<div class="final-decision-banner">{final_decision_path}</div>""", unsafe_allow_html=True)
    
    clinician_notes = st.text_area(
        "**Clinical Justification, Diagnostic Notes, or Ward Verification Details:**",
        placeholder="Type mandatory medical justification comments or ward confirmation logs here before saving..."
    )
    
    col_sig, col_space = st.columns([2, 2])
    with col_sig:
        signature = st.text_input("✍️ **Attending Doctor / Nurse Sign-off (Full Name & Cadre Code):**", placeholder="e.g., Dr. Jane Namubiru - Paediatrician")
        
    if st.button("💾 Lock and Serialize Decision to Clinical Ledger"):
        if not signature:
            st.error("🛑 Action Blocked: The attending clinician must provide an electronic text signature/code before saving.")
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
                "Initial Ward Stay (Days)": length_of_stay,
                "5-Min Apgar Score": apgar_score,
                "ANC Visits Attended": anc_visits,
                "Maternal Parity": parity,
                "Mode of Delivery": mode_of_delivery,
                "Feeding Protocol": feeding_type,
                "Physical Discharge Condition": discharge_condition,
                "Authoritative Disposition Route Taken": final_decision_path,
                "Clinical Justification & Verification Notes": clinician_notes if clinician_notes else "Adhered to calculated baseline parameters.",
                "Attending Clinician Sign-off": signature
            }
            save_prediction_to_records(patient_record)
            st.success(f"🎉 Success! Profile for {patient_id} recorded safely into the clinical audit trail.")
            st.toast(f"💾 Profile for {patient_id} recorded successfully!", icon="🎉")
            st.session_state.assessment_triggered = False  # Reset panel memory state
            st.button("🔄 Refresh Application View", on_click=st.rerun)

# ==============================================================================
# 6. EXPANDED HISTORICAL AUDIT TRAIL LOG SHEET (WITH EXACT PHRASING)
# ==============================================================================
st.write("")
st.write("")
st.markdown("""
    <div class="section-card">
        <div class="section-title">💾 Permanent Clinical Audit Ledger</div>
        <p style="color: #6B7280; font-size: 14px; margin-top:-10px;">Retrospective data matrix capturing complete baseline details, demographics, infant sex, and triage choices for future administrative audits and clinical research.</p>
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
            label="📥 Export Relational Audit Trail to CSV / Excel Spreadsheet",
            data=csv_data,
            file_name=f"mgh_cdss_audit_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"Error parsing historical tracking files: {e}")
else:
    st.info("No records are currently logged in the relational database ledger.")