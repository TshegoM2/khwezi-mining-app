import streamlit as st
import pandas as pd
import plotly.express as px

# --- PHASE 1: APP FRAMEWORK & LAYOUT SETUP ---
st.set_page_config(
    page_title="Khwezi Mining Monitoring Application",
    page_icon="⛏️",
    layout="wide"
)

# --- ULTIMATE COLORFUL MODERN THEME ---
st.markdown("""
    <style>
    /* Vibrant colorful page background gradient */
    .stApp {
        background: linear-gradient(135deg, #f0f4ff 0%, #fef2f2 50%, #f0fdf4 100%);
        color: #0f172a;
    }
    
    /* Sleek Deep Blue-Purple Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%);
        color: white;
    }
    section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] .stSelectbox span {
        color: #e0e7ff !important;
    }

    /* Vibrant Gradient Buttons (Blue to Purple) */
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        border-radius: 10px;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #2563eb 100%, #7c3aed 100%);
        box-shadow: 0 6px 15px rgba(139, 92, 246, 0.5);
    }

    /* Vibrant Form Submit Button */
    .stFormSubmitButton>button {
        background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        width: 100%;
        border: none;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
    .stFormSubmitButton>button:hover {
        background: linear-gradient(135deg, #059669 0%, #0891b2 100%);
    }

    /* Gorgeous Pop-out White Cards for KPIs & Dataframes */
    div[data-testid="stMetric"], div.stDataFrame, div.stTabs {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 14px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
    }
    
    /* Metric Accent Left Border */
    div[data-testid="stMetric"] {
        border-left: 6px solid #8b5cf6;
    }
    </style>
""", unsafe_allow_html=True)
# --- SME LOGO & HEADER BRANDING ---
# Tip: Save your red-and-white SME logo image in your GitHub repo as 'sme_logo.png'
# If the image file isn't uploaded yet, Streamlit will gracefully skip it without crashing.
try:
    st.image("sme logo.jpg", width=220)
except:
    pass

st.title("⛏️ Khwezi Mining Health, Safety & Equipment Monitoring Application")
st.markdown("**School of Mining Engineering | University of the Witwatersrand**")
st.markdown("*A centralized digital monitoring platform for operational decision-making.*")
st.divider()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["role"] = ""

# --- WORKER SAFETY AND INCIDENT DATABASES ---
worker_safety = pd.read_csv("worker_safety.csv")
safety_incidents = pd.read_csv("safety_incidents.csv")

# --- THEMBI'S BACK-END LOGIC: EQUIPMENT DATABASE & MONITORING ---
equipment = pd.DataFrame({
    "Equipment_ID": ["TRK-001", "TRK-002", "DRL-001"],
    "Equipment_Type": ["Haul Truck", "Haul Truck", "Drill"],
    "Operating_Hours": [1250, 1680, 2300],
    "Temperature_C": [72, 85, 108],
    "Vibration_mm_s": [3.2, 5.7, 8.7],
    "Downtime_Hours": [25, 45, 140],
    "Maintenance_Status": ["Operational", "Due", "Overdue"]
})

def check_temperature(value):
    if value < 80: return "NORMAL"
    elif value <= 100: return "WARNING"
    else: return "CRITICAL"

def check_vibration(value):
    if value < 5: return "NORMAL"
    elif value <= 8: return "WARNING"
    else: return "CRITICAL"

def calculate_availability(operating_hours, downtime_hours):
    total = operating_hours + downtime_hours
    if total == 0: return 0.0
    return round(operating_hours / total * 100, 2)

def overall_condition(row):
    statuses = [row["Temperature_Status"], row["Vibration_Status"]]
    if "CRITICAL" in statuses: return "CRITICAL"
    elif "WARNING" in statuses: return "WARNING"
    return "NORMAL"

equipment["Temperature_Status"] = equipment["Temperature_C"].apply(check_temperature)
equipment["Vibration_Status"] = equipment["Vibration_mm_s"].apply(check_vibration)
equipment["Overall_Condition"] = equipment.apply(overall_condition, axis=1)
equipment["Availability_Percent"] = equipment.apply(
    lambda row: calculate_availability(row["Operating_Hours"], row["Downtime_Hours"]), axis=1
)

# --- LOGIN PORTAL & RBAC (Section 3a & Table 1) ---
if not st.session_state["logged_in"]:
    st.subheader("🔒 User Access Control Portal")
    st.write("Please authenticate your credentials and select your operational role.")
    
    with st.form("login_form"):
        input_user = st.text_input("Username / Personnel ID")
        input_role = st.selectbox(
            "Select System Role:",
            ["Administrator", "Safety Officer", "Mining Engineer", "Maintenance Engineer", "Manager"]
        )
        login_button = st.form_submit_button("Authenticate & Enter")
        
        if login_button:
            if not input_user or input_user.strip() == "":
                st.error("⚠️ Error Prevention: Username cannot be empty.")
            else:
                st.session_state["logged_in"] = True
                st.session_state["username"] = input_user.strip()
                st.session_state["role"] = input_role
                st.rerun()

else:
    user = st.session_state["username"]
    role = st.session_state["role"]
    
    # --- SIDEBAR NAVIGATION & TABLE 1 PERMISSIONS ---
    st.sidebar.title("Navigation Menu")
    st.sidebar.write(f"**User:** {user}")
    st.sidebar.write(f"**Role:** {role}")
    st.sidebar.divider()
    
    allowed_pages = ["View Dashboard"]
    if role in ["Administrator", "Safety Officer", "Mining Engineer", "Manager"]:
        allowed_pages.extend(["Worker Safety Data", "Safety Incidents", "Risk Assessment"])
    if role in ["Administrator", "Mining Engineer", "Maintenance Engineer", "Manager"]:
        allowed_pages.extend(["Equipment Data", "Maintenance Data"])
        
    allowed_pages.append("Generate Reports")
    if role == "Administrator":
        allowed_pages.append("Manage Users")
        
    selected_page = st.sidebar.selectbox("Select Function", allowed_pages)
    
    st.sidebar.divider()
    if st.sidebar.button("Log Out"):
        st.session_state["logged_in"] = False
        st.rerun()

    # --- CENTRAL DASHBOARD ---
    if selected_page == "View Dashboard":
        st.subheader("📊 Central Monitoring Dashboard")
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Total Workers", "142", "Active")
        k2.metric("Safety Incidents", "3", "-1 today", delta_color="inverse")
        k3.metric("Equipment Availability", f"{equipment['Availability_Percent'].mean():.1f}%")
        k4.metric("Critical Alerts", (equipment["Overall_Condition"] == "CRITICAL").sum(), "Action Required", delta_color="inverse")
        k5.metric("Near Misses", near_miss_count, "Monitored")
        st.info("💡 Use the sidebar navigation menu to access specific system modules.")
        
        st.subheader("🚜 Equipment Monitoring Analysis")
        fig3 = px.bar(
            equipment,
            x="Equipment_ID",
            y="Availability_Percent",
            color="Equipment_ID",
            title="Equipment Availability (%)"
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        st.subheader("👷 Worker Safety and Incident Analysis")
        col1, col2 = st.columns(2)
        with col1:
            ppe_counts = worker_safety["PPE_Status"].value_counts().reset_index()
            ppe_counts.columns = ["PPE_Status", "Count"]
            fig_safety = px.pie(ppe_counts, names="PPE_Status", values="Count", title="Worker PPE Compliance")
            st.plotly_chart(fig_safety, use_container_width=True)
        with col2:
            severity_counts = safety_incidents["Severity"].value_counts().reset_index()
            severity_counts.columns = ["Severity", "Count"]
            fig_incidents = px.bar(severity_counts, x="Severity", y="Count", color="Severity", title="Safety Incidents by Severity")
            st.plotly_chart(fig_incidents, use_container_width=True)

    # --- SAMMIE'S PLACEHOLDERS / MODULES ---
    elif selected_page == "Worker Safety Data":
        st.subheader("👷 Worker Health and Safety Monitoring")
        st.write("### Worker Safety Database")
        st.dataframe(worker_safety, use_container_width=True)

        total_workers = len(worker_safety)
        compliant_workers = (worker_safety["Compliance_Status"] == "Compliant").sum()
        action_required = (worker_safety["Compliance_Status"] == "Action Required").sum()
        ppe_non_compliant = (worker_safety["PPE_Status"] == "Non-Compliant").sum()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Workers", total_workers)
        c2.metric("Compliant Workers", compliant_workers)
        c3.metric("Action Required", action_required)
        c4.metric("PPE Non-Compliant", ppe_non_compliant)

        st.write("### Select Worker")
        selected_worker = st.selectbox("Worker ID", worker_safety["Worker_ID"].tolist())
        worker = worker_safety[worker_safety["Worker_ID"] == selected_worker].iloc[0]

        st.write(f"Role: {worker['Role']}")
        st.write(f"Section: {worker['Section']}")
        st.write(f"Shift: {worker['Shift']}")
        st.write(f"PPE Status: {worker['PPE_Status']}")
        st.write(f"Safety Training: {worker['Safety_Training_Status']}")
        st.write(f"Safety Induction: {worker['Safety_Induction_Status']}")
        st.write(f"Hazards Reported: {worker['Hazards_Reported']}")

        if worker["PPE_Status"] == "Non-Compliant": st.error("PPE ALERT: Worker is not PPE compliant.")
        if worker["Safety_Training_Status"] == "Expired": st.warning("TRAINING ALERT: Safety training has expired.")
        if worker["Safety_Induction_Status"] == "Pending": st.warning("INDUCTION ALERT: Safety induction is pending.")
        if worker["Compliance_Status"] == "Action Required": st.error("Overall Safety Status: Action Required")
        else: st.success("Overall Safety Status: Compliant")

    elif selected_page == "Safety Incidents":
        st.subheader("🚨 Safety Incident Database")
        st.write("### Recorded Safety Incidents")
        st.dataframe(safety_incidents, use_container_width=True)

        total_incidents = len(safety_incidents)
        critical_incidents = (safety_incidents["Severity"] == "Critical").sum()
        open_incidents = (safety_incidents["Investigation_Status"] != "Closed").sum()
        total_days_lost = safety_incidents["Days_Lost"].sum()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Incidents", total_incidents)
        c2.metric("Critical Incidents", critical_incidents)
        c3.metric("Unresolved Investigations", open_incidents)
        c4.metric("Total Days Lost", total_days_lost)

        st.write("### Select Incident")
        selected_incident = st.selectbox("Incident ID", safety_incidents["Incident_ID"].tolist())
        incident = safety_incidents[safety_incidents["Incident_ID"] == selected_incident].iloc[0]

        st.write(f"Date: {incident['Incident_Date']}")
        st.write(f"Worker ID: {incident['Worker_ID']}")
        st.write(f"Section: {incident['Section']}")
        st.write(f"Incident Type: {incident['Incident_Type']}")
        st.write(f"Severity: {incident['Severity']}")
        st.write(f"Days Lost: {incident['Days_Lost']}")
        st.write(f"Reported to DMRE: {incident['Reported_To_DMRE']}")
        st.write(f"Investigation Status: {incident['Investigation_Status']}")
        st.write(f"Corrective Action: {incident['Corrective_Action']}")

        if incident["Severity"] == "Critical": st.error("CRITICAL INCIDENT: Immediate safety attention required.")
        elif incident["Severity"] == "High": st.warning("HIGH SEVERITY: Incident requires priority attention.")
        elif incident["Severity"] == "Medium": st.warning("MEDIUM SEVERITY: Review corrective actions.")
        else: st.info("LOW SEVERITY: Follow standard safety procedures.")

        if incident["Investigation_Status"] != "Closed": st.warning("Investigation has not been closed.")
        else: st.success("Investigation closed.")
        
    elif selected_page == "Risk Assessment":
        st.subheader("⚠️ Risk Assessment Matrix (Likelihood × Consequence)")
        l_val = st.slider("Likelihood (1-5)", 1, 5, 2)
        c_val = st.slider("Consequence (1-5)", 1, 5, 3)
        r_score = l_val * c_val
        st.write(f"Calculated Risk Score: **{r_score}**")
        if r_score <= 4: st.success("Low Risk")
        elif r_score <= 9: st.warning("Medium Risk")
        elif r_score <= 16: st.error("High Risk - Warning Triggered!")
        else: st.error("CRITICAL RISK - Immediate Action Required!")

    # --- THEMBI'S INTEGRATED MODULES ---
    elif selected_page == "Equipment Data":
        st.subheader("🚜 Equipment Database & Condition Monitoring")
        st.dataframe(equipment, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Equipment", len(equipment))
        c2.metric("Critical Equipment", (equipment["Overall_Condition"] == "CRITICAL").sum())
        c3.metric("Average Availability", f"{equipment['Availability_Percent'].mean():.1f}%")

        selected_id = st.selectbox("Select Equipment to Monitor", equipment["Equipment_ID"].tolist())
        selected = equipment[equipment["Equipment_ID"] == selected_id].iloc[0]

        st.write(f"Temperature: {selected['Temperature_C']} °C — {selected['Temperature_Status']}")
        st.write(f"Vibration: {selected['Vibration_mm_s']} mm/s — {selected['Vibration_Status']}")

        if selected["Overall_Condition"] == "CRITICAL": st.error("CRITICAL: Equipment requires immediate attention!")
        elif selected["Overall_Condition"] == "WARNING": st.warning("WARNING: Equipment condition requires monitoring.")
        else: st.success("Equipment operating within normal limits.")

    elif selected_page == "Maintenance Data":
        st.subheader("🔧 Equipment Maintenance Monitoring")
        st.dataframe(
            equipment[["Equipment_ID", "Operating_Hours", "Downtime_Hours", "Availability_Percent", "Maintenance_Status"]],
            use_container_width=True
        )

        for _, item in equipment.iterrows():
            equipment_id = item["Equipment_ID"]
            status = item["Maintenance_Status"]
            availability = item["Availability_Percent"]
            downtime = item["Downtime_Hours"]

            if status in ["Overdue", "Under Maintenance"]: st.error(f"{equipment_id}: Maintenance status is {status}.")
            elif status == "Due": st.warning(f"{equipment_id}: Maintenance is due.")
            if availability < 90: st.warning(f"{equipment_id}: Low availability ({availability}%).")
            if downtime > 100: st.warning(f"{equipment_id}: Excessive downtime ({downtime} hours).")

    # --- ADMIN / REPORTS ---
    elif selected_page == "Generate Reports":
        st.subheader("📄 Generate Operational Reports")
        if st.button("Generate Summary Report"): st.success("Report compiled successfully.")

    elif selected_page == "Manage Users":
        st.subheader("⚙️ User Management Portal (Administrator Only)")
        st.text_input("New User ID")
        st.button("Grant Access")
        
    # --- LUNGHI'S SECTION: DATA ANALYTICS (Appendix A) ---
    elif selected_page == "Interactive Data Analysis":
        st.subheader("📈 Interactive Data Analysis & Business Intelligence")
        st.write("Answering key mining engineering questions from Appendix A.")
       
        tab1, tab2 = st.tabs(["Health & Safety Analytics", "Equipment Analytics"])
       
        with tab1:
            st.write("### 1. Which department has the highest number of incidents?")
            dept_counts = safety_incidents["Section"].value_counts().reset_index()
            dept_counts.columns = ["Department", "Incident Count"]
            fig_dept = px.bar(dept_counts, x="Department", y="Incident Count", color="Department", title="Safety Incidents by Department")
            st.plotly_chart(fig_dept, use_container_width=True)
           
            st.write("### 2. How many incidents are classified as high or critical?")
            sev_counts = safety_incidents["Severity"].value_counts().reset_index()
            sev_counts.columns = ["Severity", "Count"]
            fig_sev = px.pie(sev_counts, names="Severity", values="Count", title="Incident Severity Breakdown", color="Severity",
                             color_discrete_map={"Critical":"red", "High":"orange", "Medium":"yellow", "Low":"green"})
            st.plotly_chart(fig_sev, use_container_width=True)
           
        with tab2:
            st.write("### 3. What is the average equipment availability?")
            fig_avail = px.bar(equipment, x="Equipment_ID", y="Availability_Percent", color="Equipment_Type",
                               title="Equipment Availability (%)", text="Availability_Percent")
            fig_avail.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
            fig_avail.add_hline(y=90, line_dash="dash", line_color="red", annotation_text="90% Target")
            st.plotly_chart(fig_avail, use_container_width=True)
           
            st.write("### 4. Which equipment has the highest operating temperature?")
            fig_temp = px.bar(equipment, x="Equipment_ID", y="Temperature_C", color="Overall_Condition",
                              title="Operating Temperatures (°C) vs Thresholds",
                              color_discrete_map={"CRITICAL":"red", "WARNING":"orange", "NORMAL":"green"})
            fig_temp.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Critical Limit (100°C)")
            st.plotly_chart(fig_temp, use_container_width=True)
