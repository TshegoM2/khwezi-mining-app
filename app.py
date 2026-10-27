import streamlit as st # Import the streamlit web framework
import pandas as pd # Import pandas for dataframes and tables
import plotly.express as px # Import plotly for interactive charts

st.set_page_config(page_title="Khwezi Mining App", page_icon="⛏️", layout="wide") # Setup browser page title and width

try: st.image("sme logo.jpg", width=220) # Try loading the school logo safely
except: pass # Skip image if file is missing to prevent crash

st.title("⛏️ Khwezi Mining Health, Safety & Equipment Monitoring Application") # Main application header text
st.markdown("**School of Mining Engineering | University of the Witwatersrand**") # Institution subheading
st.markdown("*A centralized digital monitoring platform for operational decision-making.*") # Sub-description
st.divider() # Draw a horizontal separator line

if "logged_in" not in st.session_state: st.session_state["logged_in"] = False # Initialize login state tracker
if "username" not in st.session_state: st.session_state["username"] = "" # Initialize empty username storage
if "role" not in st.session_state: st.session_state["role"] = "" # Initialize empty role storage

worker_safety = pd.read_csv("worker_safety.csv") # [Sammie] Load external worker safety dataset
safety_incidents = pd.read_csv("safety_incidents.csv") # [Sammie] Load external safety incident dataset

equipment = pd.DataFrame({ # [Thembi] Create equipment tracking database structure
    "Equipment_ID": ["TRK-001", "TRK-002", "DRL-001"], # Unique equipment identifiers
    "Equipment_Type": ["Haul Truck", "Haul Truck", "Drill"], # Classification of mining machinery
    "Operating_Hours": [1250, 1680, 2300], # Total operational hours logged
    "Temperature_C": [72, 85, 108], # Current engine temperature readings
    "Vibration_mm_s": [3.2, 5.7, 8.7], # Current mechanical vibration metrics
    "Downtime_Hours": [25, 45, 140], # Total breakdown or repair hours
    "Maintenance_Status": ["Operational", "Due", "Overdue"] # Current service status tracker
})

def check_temperature(val): # [Thembi] Function to evaluate temperature limits
    if val < 80: return "NORMAL" # Below normal threshold
    elif val <= 100: return "WARNING" # Approaching critical limit
    else: return "CRITICAL" # Exceeds safe operational limit

def check_vibration(val): # [Thembi] Function to evaluate vibration limits
    if val < 5: return "NORMAL" # Safe vibration range
    elif val <= 8: return "WARNING" # Elevated vibration warning
    else: return "CRITICAL" # Dangerous vibration level

def calculate_availability(op, down): # [Thembi] Function for fleet availability math
    total = op + down # Combine operating and downtime hours
    return 0.0 if total == 0 else round(op / total * 100, 2) # Calculate percentage

def overall_condition(row): # [Thembi] Function to combine machine health statuses
    stats = [row["Temperature_Status"], row["Vibration_Status"]] # Gather sensor statuses
    return "CRITICAL" if "CRITICAL" in stats else ("WARNING" if "WARNING" in stats else "NORMAL") # Return worst status

equipment["Temperature_Status"] = equipment["Temperature_C"].apply(check_temperature) # Apply temperature check rule
equipment["Vibration_Status"] = equipment["Vibration_mm_s"].apply(check_vibration) # Apply vibration check rule
equipment["Overall_Condition"] = equipment.apply(overall_condition, axis=1) # Compute combined asset condition
equipment["Availability_Percent"] = equipment.apply(lambda r: calculate_availability(r["Operating_Hours"], r["Downtime_Hours"]), axis=1) # Compute availability %

if not st.session_state["logged_in"]: # [Tshego] Check if user has authenticated yet
    st.subheader("🔒 User Access Control Portal") # Header for login screen
    st.write("Please authenticate your credentials and select your operational role.") # Prompt text
    
    with st.form("login_form"): # [Tshego] Create secure input form container
        input_user = st.text_input("Username / Personnel ID") # Text input box for user ID
        input_role = st.selectbox("Select System Role:", ["Administrator", "Safety Officer", "Mining Engineer", "Maintenance Engineer", "Manager"]) # Role picker dropdown matching Table 1
        login_button = st.form_submit_button("Authenticate & Enter") # Submit trigger button
        
        if login_button: # Triggered when login button is pressed
            if not input_user or input_user.strip() == "": st.error("⚠️ Error Prevention: Username cannot be empty.") # [Tshego] Error prevention check for blank inputs
            else: st.session_state["logged_in"] = True; st.session_state["username"] = input_user.strip(); st.session_state["role"] = input_role; st.rerun() # Save credentials and refresh view

else: # Run once authentication passes
    user = st.session_state["username"] # Fetch active session username
    role = st.session_state["role"] # Fetch active session user role
    
    st.sidebar.title("Navigation Menu") # [Tshego] Sidebar panel title
    st.sidebar.write(f"**User:** {user}") # Display logged-in user name
    st.sidebar.write(f"**Role:** {role}") # Display active security role
    st.sidebar.divider() # Sidebar separator line
    
    allowed_pages = ["View Dashboard"] # Base page accessible to all roles
    if role in ["Administrator", "Safety Officer", "Mining Engineer", "Manager"]: allowed_pages.extend(["Worker Safety Data", "Safety Incidents", "Risk Assessment"]) # [Tshego] Assign safety permissions per Table 1
    if role in ["Administrator", "Mining Engineer", "Maintenance Engineer", "Manager"]: allowed_pages.extend(["Equipment Data", "Maintenance Data"]) # [Tshego] Assign equipment permissions per Table 1
        
    allowed_pages.append("Generate Reports") # Add report generation page access
    if role == "Administrator": allowed_pages.append("Manage Users") # Restrict user management strictly to Administrator per Table 1
        
    selected_page = st.sidebar.selectbox("Select Function", allowed_pages) # Render dynamic navigation selector
    
    st.sidebar.divider() # Divider before logout control
    if st.sidebar.button("Log Out"): st.session_state["logged_in"] = False; st.rerun() # Clear session state and return to login

    if selected_page == "View Dashboard": # [Tshego] Render main summary dashboard
        st.subheader("📊 Central Monitoring Dashboard") # Dashboard section title
        
        k1, k2, k3, k4 = st.columns(4) # Create four columns for key performance metrics
        k1.metric("Total Workers", len(worker_safety), "Active") # Metric card for total workforce count
        k2.metric("Safety Incidents", len(safety_incidents), "Logged") # Metric card for total recorded incidents
        k3.metric("Equipment Availability", f"{equipment['Availability_Percent'].mean():.1f}%") # Metric card for average fleet uptime
        k4.metric("Critical Alerts", (equipment["Overall_Condition"] == "CRITICAL").sum(), "Action Required", delta_color="inverse") # Metric card for active critical machinery warnings
        
        st.info("💡 Use the sidebar navigation menu to access specific system modules.") # Helpful UI instruction banner
        
        st.subheader("🚜 Equipment Monitoring Analysis") # Section header for equipment chart
        fig3 = px.bar(equipment, x="Equipment_ID", y="Availability_Percent", color="Equipment_ID", title="Equipment Availability (%)") # [Lungile] Generate bar chart for machine availability
        st.plotly_chart(fig3, use_container_width=True) # Render equipment chart onto dashboard view
        
        st.subheader("👷 Worker Safety and Incident Analysis") # Section header for safety charts
        col1, col2 = st.columns(2) # Create two split columns for visual analytics
        with col1: # Left column context
            ppe_counts = worker_safety["PPE_Status"].value_counts().reset_index(); ppe_counts.columns = ["PPE_Status", "Count"] # Aggregate PPE compliance tallies
            fig_safety = px.pie(ppe_counts, names="PPE_Status", values="Count", title="Worker PPE Compliance") # [Lungile] Generate PPE distribution pie chart
            st.plotly_chart(fig_safety, use_container_width=True) # Render safety pie chart
        with col2: # Right column context
            severity_counts = safety_incidents["Severity"].value_counts().reset_index(); severity_counts.columns = ["Severity", "Count"] # Aggregate incident severity tallies
            fig_incidents = px.bar(severity_counts, x="Severity", y="Count", color="Severity", title="Safety Incidents by Severity") # [Lungile] Generate incident severity bar chart
            st.plotly_chart(fig_incidents, use_container_width=True) # Render incident chart

    elif selected_page == "Worker Safety Data": # [Sammie] Render worker health and safety module
        st.subheader("👷 Worker Health and Safety Monitoring") # Module header text
        st.write("### Worker Safety Database") # Sub-heading for dataframe
        st.dataframe(worker_safety, use_container_width=True) # Display complete worker safety records table

        total_workers = len(worker_safety); compliant_workers = (worker_safety["Compliance_Status"] == "Compliant").sum(); action_required = (worker_safety["Compliance_Status"] == "Action Required").sum(); ppe_non_compliant = (worker_safety["PPE_Status"] == "Non-Compliant").sum() # Calculate safety summary metrics

        c1, c2, c3, c4 = st.columns(4) # Create four metric display columns
        c1.metric("Total Workers", total_workers); c2.metric("Compliant Workers", compliant_workers); c3.metric("Action Required", action_required); c4.metric("PPE Non-Compliant", ppe_non_compliant) # Render safety KPIs

        st.write("### Select Worker") # Section prompt for individual inspection
        selected_worker = st.selectbox("Worker ID", worker_safety["Worker_ID"].tolist()) # Dropdown filter to choose specific worker ID
        worker = worker_safety[worker_safety["Worker_ID"] == selected_worker].iloc[0] # Filter dataframe for selected worker details

        st.write(f"Role: {worker['Role']}"); st.write(f"Section: {worker['Section']}"); st.write(f"Shift: {worker['Shift']}"); st.write(f"PPE Status: {worker['PPE_Status']}"); st.write(f"Safety Training: {worker['Safety_Training_Status']}"); st.write(f"Safety Induction: {worker['Safety_Induction_Status']}"); st.write(f"Hazards Reported: {worker['Hazards_Reported']}") # Output individual attributes

        if worker["PPE_Status"] == "Non-Compliant": st.error("PPE ALERT: Worker is not PPE compliant.") # Trigger visual error alert if PPE fails
        if worker["Safety_Training_Status"] == "Expired": st.warning("TRAINING ALERT: Safety training has expired.") # Trigger warning if training lapsed
        if worker["Safety_Induction_Status"] == "Pending": st.warning("INDUCTION ALERT: Safety induction is pending.") # Trigger warning for pending induction
        if worker["Compliance_Status"] == "Action Required": st.error("Overall Safety Status: Action Required") # Flag total non-compliance
        else: st.success("Overall Safety Status: Compliant") # Confirm overall worker safety clearance

    elif selected_page == "Safety Incidents": # [Sammie] Render safety incident repository module
        st.subheader("🚨 Safety Incident Database") # Module title header
        st.write("### Recorded Safety Incidents") # Sub-heading for dataset view
        st.dataframe(safety_incidents, use_container_width=True) # Display complete incident records table

        total_incidents = len(safety_incidents); critical_incidents = (safety_incidents["Severity"] == "Critical").sum(); open_incidents = (safety_incidents["Investigation_Status"] != "Closed").sum(); total_days_lost = safety_incidents["Days_Lost"].sum() # Calculate core incident statistics

        c1, c2, c3, c4 = st.columns(4) # Create four layout columns for metrics
        c1.metric("Total Incidents", total_incidents); c2.metric("Critical Incidents", critical_incidents); c3.metric("Unresolved Investigations", open_incidents); c4.metric("Total Days Lost", total_days_lost) # Render incident performance indicators

        st.write("### Select Incident") # Prompt for individual incident review
        selected_incident = st.selectbox("Incident ID", safety_incidents["Incident_ID"].tolist()) # Dropdown selector for specific incident
        incident = safety_incidents[safety_incidents["Incident_ID"] == selected_incident].iloc[0] # Extract selected incident row

        st.write(f"Date: {incident['Incident_Date']}"); st.write(f"Worker ID: {incident['Worker_ID']}"); st.write(f"Section: {incident['Section']}"); st.write(f"Incident Type: {incident['Incident_Type']}"); st.write(f"Severity: {incident['Severity']}"); st.write(f"Days Lost: {incident['Days_Lost']}"); st.write(f"Reported to DMRE: {incident['Reported_To_DMRE']}"); st.write(f"Investigation Status: {incident['Investigation_Status']}"); st.write(f"Corrective Action: {incident['Corrective_Action']}") # Display individual incident parameters

        if incident["Severity"] == "Critical": st.error("CRITICAL INCIDENT: Immediate safety attention required.") # Error alert for high severity
        elif incident["Severity"] == "High": st.warning("HIGH SEVERITY: Incident requires priority attention.") # Warning alert for high severity
        elif incident["Severity"] == "Medium": st.warning("MEDIUM SEVERITY: Review corrective actions.") # Notice alert for medium severity
        else: st.info("LOW SEVERITY: Follow standard safety procedures.") # Info prompt for low severity

        if incident["Investigation_Status"] != "Closed": st.warning("Investigation has not been closed.") # Alert if case is still open
        else: st.success("Investigation closed.") # Confirmation if investigation is finalized
        
    elif selected_page == "Risk Assessment": # [Sammie] Render basic risk evaluation module
        st.subheader("⚠️ Risk Assessment Matrix (Likelihood × Consequence)") # Module title header
        l_val = st.slider("Likelihood (1-5)", 1, 5, 2) # Slider for likelihood score (1 to 5)
        c_val = st.slider("Consequence (1-5)", 1, 5, 3) # Slider for consequence score (1 to 5)
        r_score = l_val * c_val # Calculate total mathematical risk score
        st.write(f"Calculated Risk Score: **{r_score}**") # Display computed risk score value
        if r_score <= 4: st.success("Low Risk") # Classification banner for low risk
        elif r_score <= 9: st.warning("Medium Risk") # Classification banner for medium risk
        elif r_score <= 16: st.error("High Risk - Warning Triggered!") # Classification banner for high risk
        else: st.error("CRITICAL RISK - Immediate Action Required!") # Classification banner for critical risk

    elif selected_page == "Equipment Data": # [Thembi] Render equipment database module
        st.subheader("🚜 Equipment Database & Condition Monitoring") # Module header text
        st.dataframe(equipment, use_container_width=True) # Display equipment telemetry table

        c1, c2, c3 = st.columns(3) # Create three layout columns for summary metrics
        c1.metric("Total Equipment", len(equipment)); c2.metric("Critical Equipment", (equipment["Overall_Condition"] == "CRITICAL").sum()); c3.metric("Average Availability", f"{equipment['Availability_Percent'].mean():.1f}%") # Render equipment health indicators

        selected_id = st.selectbox("Select Equipment to Monitor", equipment["Equipment_ID"].tolist()) # Dropdown filter to choose specific machine ID
        selected = equipment[equipment["Equipment_ID"] == selected_id].iloc[0] # Extract chosen machine data row

        st.write(f"Temperature: {selected['Temperature_C']} °C — {selected['Temperature_Status']}"); st.write(f"Vibration: {selected['Vibration_mm_s']} mm/s — {selected['Vibration_Status']}") # Output current operational sensor states

        if selected["Overall_Condition"] == "CRITICAL": st.error("CRITICAL: Equipment requires immediate attention!") # Trigger critical machine alert
        elif selected["Overall_Condition"] == "WARNING": st.warning("WARNING: Equipment condition requires monitoring.") # Trigger warning machine alert
        else: st.success("Equipment operating within normal limits.") # Confirm normal machine status

    elif selected_page == "Maintenance Data": # [Thembi] Render maintenance monitoring module
        st.subheader("🔧 Equipment Maintenance Monitoring") # Module header text
        st.dataframe(equipment[["Equipment_ID", "Operating_Hours", "Downtime_Hours", "Availability_Percent", "Maintenance_Status"]], use_container_width=True) # Display filtered maintenance table

        for _, item in equipment.iterrows(): # Loop through each asset row to evaluate service status
            equipment_id = item["Equipment_ID"]; status = item["Maintenance_Status"]; availability = item["Availability_Percent"]; downtime = item["Downtime_Hours"] # Extract row variables

            if status in ["Overdue", "Under Maintenance"]: st.error(f"{equipment_id}: Maintenance status is {status}.") # Trigger error for overdue upkeep
            elif status == "Due": st.warning(f"{equipment_id}: Maintenance is due.") # Trigger warning for upcoming service
            if availability < 90: st.warning(f"{equipment_id}: Low availability ({availability}%).") # Alert if availability drops below target
            if downtime > 100: st.warning(f"{equipment_id}: Excessive downtime ({downtime} hours).") # Alert for excessive downtime hours

    elif selected_page == "Generate Reports": # [Tshego] Render executive report generator module
        st.subheader("📄 Generate Operational Reports") # Module title header
        if st.button("Generate Summary Report"): st.success("Report compiled successfully.") # Action trigger button to compile data view

    elif selected_page == "Manage Users": # [Tshego] Render administrative user management portal
        st.subheader("⚙️ User Management Portal (Administrator Only)") # Module security header
        st.text_input("New User ID") # Text input box to add new personnel ID
        st.button("Grant Access") # Action button to confirm user creation
        
    elif selected_page == "Interactive Data Analysis": # [Lungile] Render Appendix A data analysis module
        st.subheader("📈 Interactive Data Analysis & Business Intelligence") # Module title header
        st.write("Answering key mining engineering questions from Appendix A.") # Descriptive intro text
       
        tab1, tab2 = st.tabs(["Health & Safety Analytics", "Equipment Analytics"]) # Split analytical views into clean tabs
       
        with tab1: # Context for safety analytics tab
            st.write("### 1. Which department has the highest number of incidents?") # Business question 1 label
            dept_counts = safety_incidents["Section"].value_counts().reset_index(); dept_counts.columns = ["Department", "Incident Count"] # Group incidents by department section
            fig_dept = px.bar(dept_counts, x="Department", y="Incident Count", color="Department", title="Safety Incidents by Department") # [Lungile] Create department incident bar chart
            st.plotly_chart(fig_dept, use_container_width=True) # Render department graph
           
            st.write("### 2. How many incidents are classified as high or critical?") # Business question 2 label
            sev_counts = safety_incidents["Severity"].value_counts().reset_index(); sev_counts.columns = ["Severity", "Count"] # Group incidents by severity level
            fig_sev = px.pie(sev_counts, names="Severity", values="Count", title="Incident Severity Breakdown", color="Severity", color_discrete_map={"Critical":"red", "High":"orange", "Medium":"yellow", "Low":"green"}) # [Lungile] Create severity pie chart
            st.plotly_chart(fig_sev, use_container_width=True) # Render severity graph
           
        with tab2: # Context for equipment analytics tab
            st.write("### 3. What is the average equipment availability?") # Business question 3 label
            fig_avail = px.bar(equipment, x="Equipment_ID", y="Availability_Percent", color="Equipment_Type", title="Equipment Availability (%)", text="Availability_Percent") # [Lungile] Create equipment availability bar chart
            fig_avail.update_traces(texttemplate='%{text:.2f}%', textposition='outside'); fig_avail.add_hline(y=90, line_dash="dash", line_color="red", annotation_text="90% Target") # Format labels and benchmark line
            st.plotly_chart(fig_avail, use_container_width=True) # Render availability graph
           
            st.write("### 4. Which equipment has the highest operating temperature?") # Business question 4 label
            fig_temp = px.bar(equipment, x="Equipment_ID", y="Temperature_C", color="Overall_Condition", title="Operating Temperatures (°C) vs Thresholds", color_discrete_map={"CRITICAL":"red", "WARNING":"orange", "NORMAL":"green"}) # [Lungile] Create temperature bar chart
            fig_temp.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Critical Limit (100°C)") # Add critical safety limit reference line
            st.plotly_chart(fig_temp, use_container_width=True) # Render temperature graph

# ULTIMATE COLORFUL MODERN THEME 
st.markdown("""
    <style>
    /* Vibrant colorful page background gradient */
    .stApp { background: linear-gradient(135deg, #f0f4ff 0%, #fef2f2 50%, #f0fdf4 100%); color: #0f172a; }
    /* Sleek Deep Blue-Purple Sidebar */
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%); color: white; }
    section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] .stSelectbox span { color: #e0e7ff !important; }
    /* Vibrant Gradient Buttons */
    .stButton>button { background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); color: white; border-radius: 10px; font-weight: bold; border: none; box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3); transition: 0.3s ease; }
    .stButton>button:hover { background: linear-gradient(135deg, #2563eb 100%, #7c3aed 100%); box-shadow: 0 6px 15px rgba(139, 92, 246, 0.5); }
    /* Vibrant Form Submit Button */
    .stFormSubmitButton>button { background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%); color: white; font-weight: bold; border-radius: 10px; width: 100%; border: none; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); }
    .stFormSubmitButton>button:hover { background: linear-gradient(135deg, #059669 0%, #0891b2 100%); }
    /* Gorgeous Pop-out White Cards */
    div[data-testid="stMetric"], div.stDataFrame, div.stTabs { background-color: #ffffff; padding: 18px; border-radius: 14px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0; }
    div[data-testid="stMetric"] { border-left: 6px solid #8b5cf6; }
    </style>
""", unsafe_allow_html=True)
