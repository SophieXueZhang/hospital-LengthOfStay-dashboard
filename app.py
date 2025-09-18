import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import os
from dotenv import load_dotenv
import openai
import asyncio
import json

# Import RAG system
try:
    from rag_system import rag_system
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("RAG system not available - papers database not ready")

# Load environment variables
load_dotenv()

# Nordic color palette
COLORS = {
    'primary': '#2E5266',      # Dark blue-gray
    'secondary': '#6C7B7F',    # Medium gray
    'accent': '#A8B8C2',       # Light blue-gray
    'light': '#F5F7FA',        # Very light gray
    'white': '#FFFFFF',        # Pure white
    'success': '#7FB069',      # Muted green
    'warning': '#E6B85C',      # Muted yellow
    'danger': '#D47A84',       # Muted red
    'text': '#2D3748',         # Dark text
    'text_light': '#718096'    # Light text
}

# Page config
st.set_page_config(
    page_title="Hospital Management Dashboard",
    page_icon="●",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Nordic design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    .main {
        background-color: #FAFBFC;
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #FAFBFC;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #2E5266 0%, #6C7B7F 100%);
        padding: 2rem 1rem;
        margin: 0 0 2rem 0;
        border-radius: 1rem;
        color: white;
        text-align: center;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 300;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .main-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 300;
    }
    
    /* KPI Card styling */
    .kpi-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }
    
    .kpi-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transform: translateY(-1px);
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 600;
        color: #2E5266;
        margin-bottom: 0.25rem;
    }
    
    .kpi-label {
        font-size: 0.9rem;
        color: #718096;
        font-weight: 400;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .kpi-icon {
        font-size: 2rem;
        opacity: 0.7;
        margin-bottom: 0.5rem;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.25rem;
        font-weight: 500;
        color: #2D3748;
        margin: 2rem 0 1rem 0;
        border-bottom: 2px solid #E2E8F0;
        padding-bottom: 0.5rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #F8FAFC;
    }
    
    /* Filter panel styling */
    .filter-panel {
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0;
        margin-bottom: 1rem;
        position: sticky;
        top: 1rem;
    }
    
    .filter-title {
        font-size: 1.1rem;
        font-weight: 500;
        color: #2D3748;
        margin-bottom: 1rem;
        border-bottom: 1px solid #E2E8F0;
        padding-bottom: 0.5rem;
    }
    
    
    /* Custom input styling */
    .stDateInput > div > div > input,
    .stMultiSelect > div > div > div,
    .stSelectbox > div > div > div {
        border-radius: 0.5rem !important;
        border: 1px solid #E2E8F0 !important;
        font-size: 0.9rem !important;
    }
    
    .stDateInput > div > div > input:focus,
    .stMultiSelect > div > div > div:focus,
    .stSelectbox > div > div > div:focus {
        border-color: #2E5266 !important;
        box-shadow: 0 0 0 2px rgba(46, 82, 102, 0.1) !important;
    }
    
    /* Filter labels */
    .stDateInput > label,
    .stMultiSelect > label,
    .stSelectbox > label {
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        color: #4A5568 !important;
        margin-bottom: 0.5rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    
    /* MultiSelect tag styling - change red to Nordic blue */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #2E5266 !important;
        border-color: #2E5266 !important;
    }
    
    .stMultiSelect [data-baseweb="tag"] span {
        color: white !important;
    }
    
    /* Remove button styling */
    .stMultiSelect [data-baseweb="tag"] [data-testid="stSelectboxClearIcon"] {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    .stMultiSelect [data-baseweb="tag"] [data-testid="stSelectboxClearIcon"]:hover {
        color: white !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-radius: 50% !important;
    }
    
    /* Remove default margins */
    .block-container {
        padding-top: 1rem;
    }
    
    /* Metric containers */
    [data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #E2E8F0;
        padding: 1rem;
        border-radius: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    [data-testid="metric-container"]:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transform: translateY(-1px);
        transition: all 0.2s ease;
    }
    
    /* Chat button styling */
    .chat-button {
        position: fixed !important;
        bottom: 2rem !important;
        right: 2rem !important;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #2E5266 0%, #6C7B7F 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 16px rgba(46, 82, 102, 0.3);
        cursor: pointer;
        z-index: 9999 !important;
        transition: all 0.3s ease;
        border: none;
    }
    
    .chat-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(46, 82, 102, 0.4);
    }
    
    .chat-button span {
        color: white;
        font-size: 1.2rem;
        font-weight: 500;
    }
    
    /* Chat modal styling */
    .chat-modal {
        position: fixed !important;
        bottom: 6rem !important;
        right: 2rem !important;
        width: 350px;
        height: 500px;
        background: white;
        border-radius: 1rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
        z-index: 10000 !important;
        display: none;
        flex-direction: column;
        overflow: hidden;
        border: 1px solid #E2E8F0;
    }
    
    .chat-modal.active {
        display: flex;
    }
    
    .chat-header {
        background: linear-gradient(135deg, #2E5266 0%, #6C7B7F 100%);
        color: white;
        padding: 1rem;
        font-weight: 500;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .chat-close {
        background: none;
        border: none;
        color: white;
        font-size: 1.2rem;
        cursor: pointer;
        padding: 0;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .chat-messages {
        flex: 1;
        padding: 1rem;
        overflow-y: auto;
        background: #FAFBFC;
    }
    
    .chat-input-area {
        padding: 1rem;
        border-top: 1px solid #E2E8F0;
        background: white;
    }
    
    .message {
        margin-bottom: 1rem;
        padding: 0.75rem;
        border-radius: 0.75rem;
        max-width: 85%;
        word-wrap: break-word;
    }
    
    .message.user {
        background: #2E5266;
        color: white;
        margin-left: auto;
    }
    
    .message.assistant {
        background: #F1F5F9;
        color: #2D3748;
        margin-right: auto;
    }
    
    .chat-input {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid #E2E8F0;
        border-radius: 0.5rem;
        font-size: 0.9rem;
        resize: none;
        font-family: Inter, sans-serif;
    }
    
    .chat-input:focus {
        outline: none;
        border-color: #2E5266;
        box-shadow: 0 0 0 2px rgba(46, 82, 102, 0.1);
    }
    
    .send-button {
        background: #2E5266;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.4rem;
        font-size: 0.9rem;
        cursor: pointer;
        margin-top: 0.5rem;
        width: 100%;
        font-family: Inter, sans-serif;
    }
    
    .send-button:hover {
        background: #1a3b4a;
    }
    
    .send-button:disabled {
        background: #9CA3AF;
        cursor: not-allowed;
    }
    
    /* Simplified layout - keep default Streamlit layout */
    
    /* Keep responsive design simple */
    @media (max-width: 768px) {
        .main-title {
            font-size: 1.8rem;
        }
        .main-subtitle {
            font-size: 0.9rem;
        }
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess data"""
    df = pd.read_csv("data/LengthOfStay.csv")
    
    # Convert dates
    df['vdate'] = pd.to_datetime(df['vdate'])
    df['discharged'] = pd.to_datetime(df['discharged'])
    df['Date_of_Birth'] = pd.to_datetime(df['Date_of_Birth'])
    
    # Create derived features
    df['month'] = df['vdate'].dt.to_period('M').astype(str)
    df['is_long_stay'] = (df['lengthofstay'] > df['lengthofstay'].quantile(0.75)).astype(int)
    df['readmit_flag'] = (df['rcount'] != '0').astype(int)
    
    # Calculate age at admission
    df['age_at_admission'] = (df['vdate'] - df['Date_of_Birth']).dt.days / 365.25
    df['age_group'] = pd.cut(df['age_at_admission'], 
                            bins=[0, 18, 35, 50, 65, 80, 100], 
                            labels=['0-18', '19-35', '36-50', '51-65', '66-80', '80+'])
    
    # Create full name for patient identification
    df['full_name'] = df['First_Name'] + ' ' + df['Last_Name']
    
    # Create risk level categorization
    df['risk_level'] = 'Standard Risk'
    high_risk_mask = (
        (df['lengthofstay'] > df['lengthofstay'].quantile(0.9)) |
        (df['readmit_flag'] == 1)
    )
    df.loc[high_risk_mask, 'risk_level'] = 'High Risk'
    
    # Disease columns for analysis
    disease_cols = ['dialysisrenalendstage', 'asthma', 'irondef', 'pneum', 
                   'substancedependence', 'psychologicaldisordermajor', 
                   'depress', 'psychother', 'fibrosisandother', 'malnutrition']
    
    return df, disease_cols

def create_chart_template():
    """Create a consistent chart template with Nordic styling"""
    template = {
        'layout': {
            'font': {'family': 'Inter, sans-serif', 'size': 12, 'color': COLORS['text']},
            'paper_bgcolor': 'white',
            'plot_bgcolor': 'white',
            'margin': {'l': 50, 'r': 50, 't': 60, 'b': 50},
            'xaxis': {
                'gridcolor': '#F1F5F9',
                'linecolor': '#E2E8F0',
                'tickcolor': '#E2E8F0',
                'tickfont': {'color': COLORS['text_light']}
            },
            'yaxis': {
                'gridcolor': '#F1F5F9',
                'linecolor': '#E2E8F0',
                'tickcolor': '#E2E8F0',
                'tickfont': {'color': COLORS['text_light']}
            },
            'title': {
                'font': {'size': 16, 'color': COLORS['text']},
                'x': 0.02,
                'xanchor': 'left'
            }
        }
    }
    return template

def generate_patient_response(patient, user_question):
    """Generate AI response using RAG system or fallback to basic OpenAI API"""
    
    try:
        # Try RAG system first if available
        if RAG_AVAILABLE:
            rag_response, relevant_papers, diagnostic_info = rag_system.get_rag_response_for_patient(patient, user_question)
            if rag_response:
                return rag_response
        
        # Fallback to basic OpenAI response
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Extract comprehensive patient information
        patient_data = {
            'name': patient['full_name'],
            'id': patient['eid'],
            'age_group': patient['age_group'],
            'gender': patient['gender'],
            'department': patient['facid'],
            'length_of_stay': patient['lengthofstay'],
            'risk_level': patient['risk_level'],
            'glucose': patient['glucose'],
            'creatinine': patient['creatinine'],
            'hematocrit': patient['hematocrit'],
            'pulse': patient['pulse'],
            'respiration': patient['respiration'],
            'bmi': patient['bmi'],
            'sodium': patient['sodium'],
            'neutrophils': patient['neutrophils'],
            'blood_urea_nitrogen': patient['bloodureanitro']
        }
        
        # Create detailed system prompt
        system_prompt = f"""You are an AI medical assistant helping healthcare professionals analyze patient data. 
        
Patient Information:
- Name: {patient_data['name']}
- ID: {patient_data['id']}
- Age Group: {patient_data['age_group']}
- Gender: {patient_data['gender']}
- Department: {patient_data['department']}
- Length of Stay: {patient_data['length_of_stay']} days
- Risk Level: {patient_data['risk_level']}

Current Lab Values & Vitals:
- Glucose: {patient_data['glucose']:.1f} mg/dL (normal: 70-140)
- Creatinine: {patient_data['creatinine']:.3f} mg/dL (normal: 0.6-1.2)
- Hematocrit: {patient_data['hematocrit']:.1f} g/dL (normal: 12-16)
- Pulse: {patient_data['pulse']} bpm (normal: 60-100)
- Respiration: {patient_data['respiration']} /min (normal: 12-20)
- BMI: {patient_data['bmi']:.1f}
- Sodium: {patient_data['sodium']:.1f} mEq/L
- Neutrophils: {patient_data['neutrophils']:.1f}%
- Blood Urea Nitrogen: {patient_data['blood_urea_nitrogen']:.1f} mg/dL

Guidelines:
1. Provide concise, clinical responses (2-3 sentences max)
2. Focus on actionable medical insights
3. Reference specific lab values when relevant
4. Use medical terminology appropriately
5. Suggest next steps when appropriate
6. If values are abnormal, explain the clinical significance"""

        # Make API call to OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        # Fallback to rule-based response if API fails
        st.error(f"API Error: {str(e)}")
        
        # Simplified fallback response
        name = patient['full_name']
        glucose = patient['glucose']
        creatinine = patient['creatinine']
        risk_level = patient['risk_level']
        
        if 'risk' in user_question.lower():
            return f"Patient has {risk_level} classification with {patient['rcount']} risk factors. Length of stay: {patient['lengthofstay']} days."
        elif 'glucose' in user_question.lower() or 'blood sugar' in user_question.lower():
            if glucose > 140:
                return f"Glucose level is elevated at {glucose:.1f} mg/dL (normal: 70-140). Consider glucose management."
            else:
                return f"Glucose level is {glucose:.1f} mg/dL - within normal range."
        elif 'kidney' in user_question.lower() or 'creatinine' in user_question.lower():
            if creatinine > 1.2:
                return f"Creatinine is elevated at {creatinine:.3f} mg/dL (normal: 0.6-1.2). Monitor kidney function."
            else:
                return f"Creatinine is {creatinine:.3f} mg/dL - within normal range."
        elif 'discharge' in user_question.lower():
            days = patient['lengthofstay']
            if days > 7:
                return f"Extended stay ({days} days). Review case for discharge readiness and potential barriers."
            else:
                return "Monitor for 24-48 hours. If stable, consider discharge planning."
        else:
            return f"I can help you analyze {name}'s case. Ask about risk factors, lab values, or treatment plans."

def show_patient_detail(patient_id, df):
    """Show detailed patient information with sidebar chat and comprehensive layout"""
    patient = df[df['eid'] == patient_id].iloc[0]
    
    # Sidebar with patient-specific chat
    with st.sidebar:
        st.markdown("### 💬 AI Medical Assistant")
        st.markdown(f"**Patient:** {patient['full_name']}")
        
        # RAG system status indicator
        if RAG_AVAILABLE:
            st.success("📚 Paper-based insights enabled")
        else:
            st.warning("⏳ Loading medical papers database...")
        
        st.markdown("---")
        
        # Initialize chat for this patient
        chat_key = f"chat_history_{patient['eid']}"
        if chat_key not in st.session_state:
            st.session_state[chat_key] = [
                {"role": "assistant", "content": f"Hello! I'm here to help with {patient['full_name']}'s case. What would you like to know?"}
            ]
        
        # Display chat history
        for message in st.session_state[chat_key]:
            if message["role"] == "user":
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**AI:** {message['content']}")
        
        # Chat input with form for Enter key submission
        with st.form(key=f"chat_form_{patient['eid']}", clear_on_submit=True):
            user_input = st.text_input("Ask about this patient...", key=f"chat_input_{patient['eid']}")
            submitted = st.form_submit_button("Send")
        
        if submitted and user_input:
            # Add user message
            st.session_state[chat_key].append({"role": "user", "content": user_input})
            
            # Generate AI response using OpenAI API
            ai_response = generate_patient_response(patient, user_input)
            st.session_state[chat_key].append({"role": "assistant", "content": ai_response})
            st.rerun()
        
        # Quick action buttons
        st.markdown("---")
        st.markdown("**Quick Actions:**")
        
        if st.button("🔍 Risk Assessment", key=f"risk_btn_{patient['eid']}"):
            risk_msg = f"Please provide a comprehensive risk assessment for {patient['full_name']} based on current lab values and clinical data."
            st.session_state[chat_key].append({"role": "user", "content": risk_msg})
            ai_response = generate_patient_response(patient, risk_msg)
            st.session_state[chat_key].append({"role": "assistant", "content": ai_response})
            st.rerun()
        
        if st.button("💊 Treatment Plan", key=f"treatment_btn_{patient['eid']}"):
            treatment_msg = f"What treatment recommendations and interventions would you suggest for {patient['full_name']} based on their current condition?"
            st.session_state[chat_key].append({"role": "user", "content": treatment_msg})
            ai_response = generate_patient_response(patient, treatment_msg)
            st.session_state[chat_key].append({"role": "assistant", "content": ai_response})
            st.rerun()
        
        if st.button("🏠 Discharge Planning", key=f"discharge_btn_{patient['eid']}"):
            discharge_msg = f"Evaluate {patient['full_name']}'s readiness for discharge and provide discharge planning recommendations."
            st.session_state[chat_key].append({"role": "user", "content": discharge_msg})
            ai_response = generate_patient_response(patient, discharge_msg)
            st.session_state[chat_key].append({"role": "assistant", "content": ai_response})
            st.rerun()
    
    # Main content area
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.current_page = "dashboard"
        st.session_state.selected_patient = None
        st.rerun()
    
    # Patient header
    st.markdown(f"""
    <div class="main-header">
        <div class="main-title">Patient Details: {patient['full_name']}</div>
        <div class="main-subtitle">Comprehensive Medical Record</div>
    </div>
    """, unsafe_allow_html=True)
    
    # AI-Based Clinical Summary Section - Only show if patient has identifiable conditions
    if RAG_AVAILABLE:
        # Check if patient has detectable symptoms/conditions
        detected_symptoms, diagnostic_info = rag_system.extract_symptoms_from_patient(patient)
        
        # Only show if we detect specific medical conditions (not just generic terms)
        specific_conditions = [s for s in detected_symptoms if s not in ['length of stay', 'hospital admission', 'medical care']]
        
        if specific_conditions:
            with st.expander("🔬 AI Clinical Summary & Evidence-Based Insights", expanded=True):
                # Get RAG analysis for this patient
                try:
                    rag_response, relevant_papers, diagnostic_details = rag_system.get_rag_response_for_patient(patient)
                    
                    if rag_response and relevant_papers:
                        # Display detected conditions with diagnostic reasoning
                        condition_list = ", ".join(specific_conditions).title()
                        st.markdown(f"**Detected Conditions:** {condition_list}")
                        
                        # Display diagnostic basis
                        if diagnostic_details:
                            st.markdown("**Diagnostic Basis:**")
                            for detail in diagnostic_details:
                                st.markdown(f"• {detail}")
                        
                        # Display clinical insights
                        st.markdown("**Clinical Analysis:**")
                        # Remove the reference section from RAG response for cleaner display
                        clean_response = rag_response.split("📚 参考文献:")[0].strip()
                        st.markdown(clean_response)
                        
                        # Display relevant papers separately (remove duplicates)
                        if relevant_papers:
                            st.markdown("**📚 Supporting Evidence:**")
                            unique_titles = []
                            for paper in relevant_papers[:3]:
                                if paper['title'] not in unique_titles:
                                    unique_titles.append(paper['title'])
                                    st.markdown(f"• {paper['title']}")
                    else:
                        st.info("💡 Ask questions in the chat to get evidence-based insights for this patient.")
                        
                except Exception as e:
                    st.warning("Clinical insights temporarily unavailable.")
    
    # Health Status Overview (Full width, 4 metrics)
    st.markdown("### Health Status Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Age Group", patient['age_group'])
        
    with col2:
        st.metric("Department", patient['facid'])
        
    with col3:
        st.metric("Length of Stay", f"{patient['lengthofstay']} days")
        
    with col4:
        # Determine overall risk status
        st.metric("Risk Status", "")
        if patient['risk_level'] == 'High Risk':
            st.markdown("<span style='color: #D47A84;'>● High Risk</span>", unsafe_allow_html=True)
        else:
            st.markdown("○ Standard Risk")
    
    st.markdown("---")
    
    # Single column layout for detailed information
    # Risk Assessment
    st.markdown("### Risk Assessment")
    risk_factors = []
    
    # Analyze key risk factors
    if patient['lengthofstay'] > df['lengthofstay'].quantile(0.75):
        risk_factors.append("Extended length of stay")
    if patient['readmit_flag'] == 1:
        risk_factors.append("Previous readmission")
    if patient['age_at_admission'] > 65:
        risk_factors.append("Advanced age")
    if patient['creatinine'] > 1.2:
        risk_factors.append("Elevated creatinine")
    if patient['glucose'] > 140:
        risk_factors.append("Elevated glucose")
    if patient['hematocrit'] < 12 or patient['hematocrit'] > 16:
        hematocrit_status = "High hematocrit" if patient['hematocrit'] > 16 else "Low hematocrit"
        risk_factors.append(f"<span style='color: #D47A84;'>{hematocrit_status}</span>")
    
    if risk_factors:
        for factor in risk_factors:
            st.markdown(f"● {factor}", unsafe_allow_html=True)
    else:
        st.write("○ No significant risk factors identified")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Medical Conditions
    st.markdown("### Medical Conditions")
    conditions = []
    condition_names = {
        'dialysisrenalendstage': 'End-stage renal disease',
        'asthma': 'Asthma',
        'irondef': 'Iron deficiency',
        'pneum': 'Pneumonia',
        'substancedependence': 'Substance dependence',
        'psychologicaldisordermajor': 'Major psychological disorder',
        'depress': 'Depression',
        'psychother': 'Requiring psychotherapy',
        'fibrosisandother': 'Fibrosis and related conditions',
        'malnutrition': 'Malnutrition'
    }
    
    medical_cols = ['dialysisrenalendstage', 'asthma', 'irondef', 'pneum', 'substancedependence', 
                   'psychologicaldisordermajor', 'depress', 'psychother', 'fibrosisandother', 'malnutrition']
    
    for col in medical_cols:
        if patient[col] == 1:
            conditions.append(condition_names.get(col, col.replace('_', ' ').title()))
    
    if conditions:
        for condition in conditions:
            st.write(f"● {condition}")
    else:
        st.write("○ No recorded medical conditions")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Vital Signs
    st.markdown("### Vital Signs")
    vital_col1, vital_col2 = st.columns(2)
    
    with vital_col1:
        pulse_normal = 60 <= patient['pulse'] <= 100
        st.metric("Pulse", f"{patient['pulse']} bpm")
        if pulse_normal:
            st.markdown("✓ Normal")
        else:
            pulse_status = "High" if patient['pulse'] > 100 else "Low"
            st.markdown(f"<span style='color: #D47A84;'>● {pulse_status}</span>", unsafe_allow_html=True)
        
    with vital_col2:
        resp_normal = 12 <= patient['respiration'] <= 20
        st.metric("Respiration", f"{patient['respiration']} /min")
        if resp_normal:
            st.markdown("✓ Normal")
        else:
            resp_status = "High" if patient['respiration'] > 20 else "Low"
            st.markdown(f"<span style='color: #D47A84;'>● {resp_status}</span>", unsafe_allow_html=True)
    
    # BMI analysis (moved out of columns for single column layout)
    st.markdown("### BMI Assessment")
    bmi = patient['bmi']
    if bmi < 18.5:
        bmi_status = "Low"
    elif 18.5 <= bmi < 25:
        bmi_status = "Normal"
    elif 25 <= bmi < 30:
        bmi_status = "High"
    else:
        bmi_status = "High"
    
    st.metric("BMI", f"{bmi:.1f}")
    if bmi_status == "Normal":
        st.markdown("✓ Normal")
    else:
        st.markdown(f"<span style='color: #D47A84;'>● {bmi_status}</span>", unsafe_allow_html=True)
    
    # Laboratory Results with interpretations
    st.markdown("### Laboratory Results")
    
    # Hematocrit
    hematocrit = patient['hematocrit']
    hematocrit_normal = 12 <= hematocrit <= 16
    hematocrit_color = "○" if hematocrit_normal else "●"
    st.metric("Hematocrit", f"{hematocrit:.1f} g/dL")
    if hematocrit_normal:
        st.markdown("○ Normal")
    else:
        hematocrit_status = "High" if hematocrit > 16 else "Low"
        st.markdown(f"<span style='color: #D47A84;'>● {hematocrit_status}</span>", unsafe_allow_html=True)
        
    # Creatinine
    creatinine = patient['creatinine']
    creatinine_normal = 0.6 <= creatinine <= 1.2
    creatinine_color = "○" if creatinine_normal else "●"
    st.metric("Creatinine", f"{creatinine:.3f} mg/dL")
    if creatinine_normal:
        st.markdown("○ Normal")
    else:
        creatinine_status = "High" if creatinine > 1.2 else "Low"
        st.markdown(f"<span style='color: #D47A84;'>● {creatinine_status}</span>", unsafe_allow_html=True)
        
    # Glucose
    glucose = patient['glucose']
    glucose_normal = 70 <= glucose <= 140
    glucose_color = "○" if glucose_normal else "●"
    st.metric("Glucose", f"{glucose:.1f} mg/dL")
    if glucose_normal:
        st.markdown("○ Normal")
    else:
        glucose_status = "High" if glucose > 140 else "Low"
        st.markdown(f"<span style='color: #D47A84;'>● {glucose_status}</span>", unsafe_allow_html=True)
        
    # Other lab values
    st.metric("Neutrophils", f"{patient['neutrophils']:.1f}%")
    st.metric("Sodium", f"{patient['sodium']:.1f} mEq/L")
    st.metric("Blood Urea Nitrogen", f"{patient['bloodureanitro']:.1f} mg/dL")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Clinical Decision Support
    st.markdown("### 🎯 Priority Actions")
    
    # Priority system: Critical -> High -> Medium -> Low
    critical_actions = []
    high_priority = []
    medium_priority = []
    low_priority = []
    
    # Critical (immediate action needed)
    if glucose > 300:
        critical_actions.append({
            'issue': 'Severe Hyperglycemia',
            'action': 'Immediate insulin protocol + hourly glucose monitoring',
            'timeline': 'NOW'
        })
    if creatinine > 2.0:
        critical_actions.append({
            'issue': 'Severe Kidney Dysfunction', 
            'action': 'Urgent nephrology consult + fluid balance review',
            'timeline': 'Within 2 hours'
        })
    if patient['pulse'] > 120 or patient['pulse'] < 50:
        critical_actions.append({
            'issue': f"{'High' if patient['pulse'] > 120 else 'Low'} Heart Rate",
            'action': 'ECG + cardiac monitoring + vitals q15min',
            'timeline': 'NOW'
        })
    if hematocrit < 8:
        critical_actions.append({
            'issue': 'Severe Anemia',
            'action': 'Type & cross + consider transfusion',
            'timeline': 'Within 1 hour'
        })
    
    # High Priority (same day)
    if glucose > 180:
        high_priority.append({
            'issue': 'Hyperglycemia',
            'action': 'Adjust insulin regimen + q6h glucose checks',
            'timeline': 'Within 4 hours'
        })
    if creatinine > 1.5:
        high_priority.append({
            'issue': 'Kidney Function Decline',
            'action': 'Review medications + increase monitoring',
            'timeline': 'Today'
        })
    if patient['lengthofstay'] > 10:
        high_priority.append({
            'issue': 'Extended Stay Risk',
            'action': 'Discharge planning meeting + complications review',
            'timeline': 'Today'
        })
    
    # Medium Priority (24-48 hours)
    if hematocrit < 12:
        medium_priority.append({
            'issue': 'Anemia',
            'action': 'Iron studies + nutrition consult',
            'timeline': 'Within 24h'
        })
    if patient['bmi'] < 18.5:
        medium_priority.append({
            'issue': 'Underweight',
            'action': 'Nutrition assessment + calorie count',
            'timeline': 'Within 48h'
        })
    if any(patient[col] == 1 for col in ['depress', 'psychologicaldisordermajor']):
        medium_priority.append({
            'issue': 'Mental Health Needs',
            'action': 'Psychology/psychiatry consult',
            'timeline': 'Within 48h'
        })
    
    # Low Priority (routine care)
    if patient['bmi'] > 25:
        low_priority.append({
            'issue': 'Weight Management',
            'action': 'Dietary counseling + activity plan',
            'timeline': 'Before discharge'
        })
    if patient['readmit_flag'] == 1:
        low_priority.append({
            'issue': 'Readmission Risk',
            'action': 'Enhanced discharge education + follow-up',
            'timeline': 'Before discharge'
        })
    
    # Display priorities
    if critical_actions:
        st.markdown("#### 🚨 **CRITICAL - Immediate Action Required**")
        for action in critical_actions:
            st.markdown(f"""
            <div style="background-color: #FFF5F5; border-left: 4px solid #D47A84; padding: 10px; margin: 5px 0;">
                <strong style="color: #D47A84;">{action['issue']}</strong><br>
                <strong>Action:</strong> {action['action']}<br>
                <strong>Timeline:</strong> {action['timeline']}
            </div>
            """, unsafe_allow_html=True)
    
    if high_priority:
        st.markdown("#### ⚠️ **HIGH PRIORITY - Same Day**")
        for action in high_priority:
            st.markdown(f"""
            <div style="background-color: #FFF8E1; border-left: 4px solid #E6B85C; padding: 10px; margin: 5px 0;">
                <strong style="color: #E6B85C;">{action['issue']}</strong><br>
                <strong>Action:</strong> {action['action']}<br>
                <strong>Timeline:</strong> {action['timeline']}
            </div>
            """, unsafe_allow_html=True)
    
    if medium_priority:
        st.markdown("#### 📋 **MEDIUM PRIORITY - 24-48 Hours**")
        for action in medium_priority:
            st.markdown(f"• **{action['issue']}**: {action['action']} ({action['timeline']})")
    
    if low_priority:
        st.markdown("#### 📝 **ROUTINE CARE**")
        for action in low_priority:
            st.markdown(f"• **{action['issue']}**: {action['action']} ({action['timeline']})")
    
    if not (critical_actions or high_priority or medium_priority or low_priority):
        st.markdown("✅ **No urgent interventions identified - continue routine care**")
    
    st.markdown("---")
    
    # Discharge Readiness Assessment
    st.markdown("### 🏠 Discharge Readiness")
    
    # Calculate discharge readiness score
    discharge_score = 0
    blocking_factors = []
    ready_factors = []
    
    # Medical stability (40% of score)
    if not critical_actions and not high_priority:
        discharge_score += 40
        ready_factors.append("Medical condition stable")
    else:
        blocking_factors.append("Unresolved critical/high priority issues")
    
    # Lab values stability (30% of score)
    stable_labs = 0
    total_labs = 0
    
    if 70 <= glucose <= 180:
        stable_labs += 1
        ready_factors.append("Glucose controlled")
    elif glucose > 180:
        blocking_factors.append("Uncontrolled glucose")
    total_labs += 1
    
    if 0.6 <= creatinine <= 1.5:
        stable_labs += 1
        ready_factors.append("Kidney function stable")
    elif creatinine > 1.5:
        blocking_factors.append("Kidney function concerns")
    total_labs += 1
    
    if hematocrit >= 10:
        stable_labs += 1
        ready_factors.append("Adequate blood levels")
    else:
        blocking_factors.append("Severe anemia needs treatment")
    total_labs += 1
    
    discharge_score += int(30 * stable_labs / total_labs)
    
    # Length of stay consideration (20% of score)
    if patient['lengthofstay'] <= 7:
        discharge_score += 20
        ready_factors.append("Appropriate length of stay")
    elif patient['lengthofstay'] > 14:
        blocking_factors.append("Extended stay - investigate barriers")
    else:
        discharge_score += 10
    
    # Social factors (10% of score)
    if patient['malnutrition'] == 0:
        discharge_score += 5
        ready_factors.append("Nutrition adequate")
    else:
        blocking_factors.append("Nutrition concerns need addressing")
    
    if not any(patient[col] == 1 for col in ['depress', 'psychologicaldisordermajor']):
        discharge_score += 5
        ready_factors.append("Mental health stable")
    else:
        blocking_factors.append("Mental health needs ongoing care")
    
    # Display discharge readiness
    if discharge_score >= 80:
        status_color = "#7FB069"
        status_text = "READY FOR DISCHARGE"
        status_icon = "✅"
    elif discharge_score >= 60:
        status_color = "#E6B85C"
        status_text = "DISCHARGE PLANNING NEEDED"
        status_icon = "⚠️"
    else:
        status_color = "#D47A84"
        status_text = "NOT READY - REQUIRES INTERVENTION"
        status_icon = "🚨"
    
    st.markdown(f"""
    <div style="background-color: #F8F9FA; border: 2px solid {status_color}; border-radius: 8px; padding: 15px; margin: 10px 0;">
        <h4 style="color: {status_color}; margin: 0;">{status_icon} {status_text}</h4>
        <p style="font-size: 18px; margin: 5px 0;"><strong>Discharge Readiness Score: {discharge_score}/100</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if ready_factors:
            st.markdown("**✅ Ready Indicators:**")
            for factor in ready_factors:
                st.markdown(f"• {factor}")
    
    with col2:
        if blocking_factors:
            st.markdown("**🚫 Blocking Factors:**")
            for factor in blocking_factors:
                st.markdown(f"• <span style='color: #D47A84;'>{factor}</span>", unsafe_allow_html=True)
    
    # Estimated discharge timeline
    if discharge_score >= 80:
        timeline = "Today - within 24 hours"
    elif discharge_score >= 60:
        timeline = "24-48 hours (after addressing issues)"
    else:
        timeline = "48+ hours (significant interventions needed)"
    
    st.markdown(f"**📅 Estimated Discharge Timeline:** {timeline}")
    
    # Bottom full width sections
    st.markdown("---")
    
    # Three-column layout for bottom sections
    bottom_col1, bottom_col2, bottom_col3 = st.columns(3)
    
    with bottom_col1:
        # Follow-up Schedule
        st.markdown("### Follow-up Schedule")
        import datetime
        admit_date = patient['vdate']
        discharge_date = patient['discharged']
        
        # Calculate follow-up dates based on risk level
        if patient['risk_level'] == 'High Risk':
            followup_days = 7
        else:
            followup_days = 30
            
        followup_date = discharge_date + pd.Timedelta(days=followup_days)
        st.write(f"**Next appointment:** {followup_date.strftime('%Y-%m-%d')}")
        st.write(f"**Appointment type:** {'High-priority' if patient['risk_level'] == 'High Risk' else 'Routine'} follow-up")
        
    with bottom_col2:
        # Timeline
        st.markdown("### Care Timeline")
        st.write(f"**Date of Birth:** {patient['Date_of_Birth'].strftime('%Y-%m-%d')}")
        st.write(f"**Age at admission:** {patient['age_at_admission']:.1f} years")
        st.write(f"**Admission:** {patient['vdate'].strftime('%Y-%m-%d')}")
        st.write(f"**Discharge:** {patient['discharged'].strftime('%Y-%m-%d')}")
        st.write(f"**Gender:** {patient['gender']}")
        
    with bottom_col3:
        # Emergency Information
        st.markdown("### Emergency Information")
        
        emergency_indicators = []
        if creatinine > 2.0:
            emergency_indicators.append("Severe kidney dysfunction")
        if glucose > 300:
            emergency_indicators.append("Severe hyperglycemia")
        if patient['pulse'] > 120:
            emergency_indicators.append("High heart rate")
        elif patient['pulse'] < 50:
            emergency_indicators.append("Low heart rate")
        if hematocrit < 8:
            emergency_indicators.append("Severe anemia")
            
        if emergency_indicators:
            st.write("**Alert conditions:**")
            for indicator in emergency_indicators:
                st.write(f"● {indicator}")
        else:
            st.write("○ No immediate emergency indicators")
            
        st.write(f"**Risk count:** {patient['rcount']}")
        st.write(f"**Priority level:** {'High' if patient['risk_level'] == 'High Risk' else 'Standard'}")

def main():
    # Initialize session state
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"
    if "selected_patient" not in st.session_state:
        st.session_state.selected_patient = None
    
    # Load data
    df, disease_cols = load_data()
    
    # Check if we should show patient detail page
    if st.session_state.current_page == "patient_detail" and st.session_state.selected_patient:
        show_patient_detail(st.session_state.selected_patient, df)
        return
    
    # Header
    st.markdown("""
    <div class="main-header">
        <div class="main-title">Hospital Management Dashboard</div>
        <div class="main-subtitle">Analytics & Performance Monitoring</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar filters (moved to sidebar with chat)
    with st.sidebar:
        
        # Date range filter
        date_range = st.date_input(
            "Date Range",
            value=[df['vdate'].min().date(), df['vdate'].max().date()],
            min_value=df['vdate'].min().date(),
            max_value=df['vdate'].max().date()
        )
        
        # Gender filter
        gender_options = st.multiselect(
            "Gender",
            options=['M', 'F'],
            default=['M', 'F']
        )
        
        # Department filter
        dept_options = st.multiselect(
            "Department",
            options=sorted(df['facid'].unique()),
            default=sorted(df['facid'].unique())
        )
        
        # Age group filter
        age_options = st.multiselect(
            "Age Group",
            options=sorted(df['age_group'].dropna().unique()),
            default=sorted(df['age_group'].dropna().unique())
        )
        
        # Risk level filter
        risk_options = st.multiselect(
            "Risk Level",
            options=["Standard Risk", "High Risk"],
            default=["Standard Risk", "High Risk"]
        )
    
    # Handle date range - ensure we have both start and end dates
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range[0], date_range[1]
    else:
        # If only one date is selected, use it as both start and end
        start_date = end_date = date_range if not isinstance(date_range, (list, tuple)) else date_range[0]
    
    # Apply filters with error handling
    try:
        mask = (
            (df['vdate'].dt.date >= start_date) &
            (df['vdate'].dt.date <= end_date)
        )
        
        if gender_options:
            mask = mask & (df['gender'].isin(gender_options))
        if dept_options:
            mask = mask & (df['facid'].isin(dept_options))
        if age_options:
            mask = mask & (df['age_group'].isin(age_options))
        if risk_options:
            mask = mask & (df['risk_level'].isin(risk_options))
            
        filtered_df = df[mask]
        
        if filtered_df.empty:
            st.warning("No data available with current filters. Please adjust your selection.")
            # Show charts with full dataset instead of returning
            filtered_df = df
    except Exception as e:
        st.error(f"Filter error: {e}")
        # Use full dataset if filtering fails
        filtered_df = df
    
    # KPI Section
    st.markdown('<div class="section-header">Key Performance Indicators</div>', unsafe_allow_html=True)
    create_kpi_cards(filtered_df)
    
    # Charts section
    st.markdown('<div class="section-header">Analytics Dashboard</div>', unsafe_allow_html=True)
    
    # Two column layout for charts
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        create_dept_comparison(filtered_df)
        st.markdown("<br>", unsafe_allow_html=True)
        create_lab_scatter(filtered_df)
    
    with col2:
        create_disease_heatmap(filtered_df, disease_cols)
        st.markdown("<br>", unsafe_allow_html=True)
        create_trend_analysis(filtered_df)
    
    # Detailed analysis
    st.markdown('<div class="section-header">Patient Details</div>', unsafe_allow_html=True)
    create_detail_table(filtered_df)
    
    # Add floating chat widget
    add_floating_chat()

def create_kpi_cards(df):
    """Create KPI cards with Nordic styling"""
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    avg_los = df['lengthofstay'].mean()
    long_stay_rate = (df['lengthofstay'] > 7).mean() * 100
    readmit_rate = df['readmit_flag'].mean() * 100
    turnover = 365 / avg_los
    
    with col1:
        st.metric(
            "Average Length of Stay",
            f"{avg_los:.1f} days",
            delta=None
        )
    
    with col2:
        st.metric(
            "Extended Stay Rate",
            f"{long_stay_rate:.1f}%",
            delta=None
        )
    
    with col3:
        st.metric(
            "Readmission Rate",
            f"{readmit_rate:.1f}%",
            delta=None
        )
    
    with col4:
        st.metric(
            "Bed Turnover Rate",
            f"{turnover:.1f}/year",
            delta=None
        )

def create_dept_comparison(df):
    """Create department comparison chart with Nordic styling"""
    dept_stats = df.groupby('facid', observed=False)['lengthofstay'].agg(['mean', 'count']).reset_index()
    dept_stats = dept_stats[dept_stats['count'] >= 10]
    
    fig = px.bar(
        dept_stats.sort_values('mean', ascending=True), 
        x='mean', 
        y='facid',
        orientation='h',
        title="Average Length of Stay by Department",
        labels={'mean': 'Days', 'facid': 'Department'},
        color='mean',
        color_continuous_scale=['#A8B8C2', '#6C7B7F', '#2E5266']
    )
    
    fig.update_layout(create_chart_template()['layout'])
    fig.update_layout(height=400, showlegend=False)
    fig.update_coloraxes(showscale=False)
    
    st.plotly_chart(fig, use_container_width=True)

def create_disease_heatmap(df, disease_cols):
    """Create disease heatmap with Nordic styling"""
    disease_los = []
    disease_names = {
        'dialysisrenalendstage': 'Renal Disease',
        'asthma': 'Asthma',
        'irondef': 'Iron Deficiency',
        'pneum': 'Pneumonia',
        'substancedependence': 'Substance Abuse',
        'psychologicaldisordermajor': 'Psychological Disorder',
        'depress': 'Depression',
        'psychother': 'Psychotherapy',
        'fibrosisandother': 'Fibrosis',
        'malnutrition': 'Malnutrition'
    }
    
    for disease in disease_cols:
        disease_df = df[df[disease] == 1]
        if len(disease_df) >= 5:
            avg_los = disease_df['lengthofstay'].mean()
            disease_los.append({
                'condition': disease_names.get(disease, disease),
                'avg_los': avg_los,
                'count': len(disease_df)
            })
    
    if disease_los:
        disease_df = pd.DataFrame(disease_los).sort_values('avg_los', ascending=True)
        
        fig = px.bar(
            disease_df,
            x='avg_los',
            y='condition',
            orientation='h',
            title="Condition Impact on Length of Stay",
            labels={'avg_los': 'Average Days', 'condition': 'Medical Condition'},
            color='avg_los',
            color_continuous_scale=['#7FB069', '#E6B85C', '#D47A84']
        )
        
        fig.update_layout(create_chart_template()['layout'])
        fig.update_layout(height=400, showlegend=False)
        fig.update_coloraxes(showscale=False)
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Insufficient condition data for visualization")

def create_lab_scatter(df):
    """Create lab bubble chart for risk stratification with Nordic styling"""
    st.markdown("**Laboratory Indicators & Risk Stratification**")
    
    # Lab metric selection
    lab_metrics = st.selectbox(
        "Laboratory Metric",
        ['creatinine', 'glucose', 'hematocrit', 'neutrophils', 'sodium', 'bloodureanitro'],
        key="lab_selector"
    )
    
    # Clean and prepare data
    clean_df = df.dropna(subset=[lab_metrics, 'lengthofstay']).copy()
    
    # Remove outliers for better visualization
    q1 = clean_df[lab_metrics].quantile(0.05)
    q99 = clean_df[lab_metrics].quantile(0.95)
    clean_df = clean_df[(clean_df[lab_metrics] >= q1) & (clean_df[lab_metrics] <= q99)]
    
    # Create value-based bins instead of quantile-based bins
    min_val = clean_df[lab_metrics].min()
    max_val = clean_df[lab_metrics].max()
    
    # Create 8-12 equal-width bins based on value range
    n_bins = min(12, max(8, int((max_val - min_val) / (clean_df[lab_metrics].std() * 0.5))))
    lab_bins = pd.cut(clean_df[lab_metrics], bins=n_bins, include_lowest=True)
    
    # Group data for bubble chart
    bubble_data = []
    for lab_range, group in clean_df.groupby(lab_bins, observed=False):
        if len(group) >= 10:  # Minimum sample size for reliability
            avg_lab_value = group[lab_metrics].mean()
            avg_los = group['lengthofstay'].mean()
            readmit_rate = group['readmit_flag'].mean() * 100
            patient_count = len(group)
            
            # Format the range for better display
            range_str = f"{lab_range.left:.2f} - {lab_range.right:.2f}"
            
            bubble_data.append({
                'lab_value': avg_lab_value,
                'avg_los': avg_los,
                'readmit_rate': readmit_rate,
                'patient_count': patient_count,
                'lab_range': range_str
            })
    
    if not bubble_data:
        st.warning("Insufficient data for bubble chart analysis")
        return
        
    bubble_df = pd.DataFrame(bubble_data)
    
    # Create bubble chart
    fig = px.scatter(
        bubble_df,
        x='lab_value',
        y='avg_los',
        size='patient_count',
        hover_data={
            'patient_count': True,
            'readmit_rate': ':.1f',
            'lab_value': ':.2f',
            'avg_los': ':.1f',
            'lab_range': False
        },
        title=f"Laboratory Values vs Length of Stay: {lab_metrics.title()}",
        labels={
            'lab_value': f'{lab_metrics.title()} Level',
            'avg_los': 'Average Length of Stay (days)',
            'patient_count': 'Patient Count'
        },
        color_discrete_sequence=[COLORS['primary']],
        size_max=50
    )
    
    # Customize bubble chart appearance
    fig.update_layout(create_chart_template()['layout'])
    fig.update_layout(height=450, showlegend=False)
    
    fig.update_traces(
        marker=dict(
            opacity=0.7,
            line=dict(width=1, color='white'),
            color=COLORS['primary']
        )
    )
    
    # Add annotation explaining the chart
    fig.add_annotation(
        text="Bubble size = Patient Count",
        xref="paper", yref="paper",
        x=0.02, y=0.98,
        showarrow=False,
        font=dict(size=10, color=COLORS['text_light']),
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor=COLORS['accent'],
        borderwidth=1
    )
    
    st.plotly_chart(fig, use_container_width=True)
    

def create_trend_analysis(df):
    """Create trend analysis with Nordic styling"""
    monthly_stats = df.groupby('month', observed=False).agg({
        'lengthofstay': 'mean',
        'eid': 'count'
    }).reset_index()
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(
            x=monthly_stats['month'], 
            y=monthly_stats['lengthofstay'],
            name="Avg Length of Stay",
            line=dict(color=COLORS['primary'], width=3),
            mode='lines+markers',
            marker=dict(size=6)
        ),
        secondary_y=False,
    )
    
    fig.add_trace(
        go.Scatter(
            x=monthly_stats['month'], 
            y=monthly_stats['eid'],
            name="Patient Volume",
            line=dict(color=COLORS['success'], width=3),
            mode='lines+markers',
            marker=dict(size=6)
        ),
        secondary_y=True,
    )
    
    fig.update_layout(create_chart_template()['layout'])
    fig.update_layout(
        title="Monthly Trends Analysis",
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.update_xaxes(title_text="Month")
    fig.update_yaxes(title_text="Average Length of Stay (days)", secondary_y=False)
    fig.update_yaxes(title_text="Patient Count", secondary_y=True)
    
    st.plotly_chart(fig, use_container_width=True)

def create_detail_table(df):
    """Create detailed patient table"""
    
    # Full patient list
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Create tabs for better organization
    tab1, tab2 = st.tabs(["Full Patient List", "Search & Filter"])
    
    with tab1:
        if not df.empty:
            # Add search functionality at the top
            st.markdown("**Quick Search**")
            search_col1, search_col2, search_col3 = st.columns([2, 1, 1])
            
            with search_col1:
                quick_search = st.text_input(
                    "Search by name or department:", 
                    key="quick_search_full_list",
                    placeholder="Enter patient name or department..."
                )
            
            with search_col2:
                gender_filter = st.selectbox(
                    "Gender:",
                    options=["All", "M", "F"],
                    key="gender_filter_search"
                )
            
            with search_col3:
                clear_search = st.button("Clear All", key="clear_quick_search")
                if clear_search:
                    st.session_state.quick_search_full_list = ""
                    st.session_state.gender_filter_search = "All"
                    st.rerun()
            
            st.markdown("---")
            
            display_cols = ['full_name', 'risk_level', 'age_group', 'vdate', 'gender', 'facid', 'lengthofstay', 'rcount']
            full_list = df[display_cols].copy()
            full_list['vdate'] = full_list['vdate'].dt.strftime('%Y-%m-%d')
            
            # Apply search filters
            search_applied = False
            
            # Text search filter
            if quick_search:
                search_mask = (
                    df['full_name'].str.contains(quick_search, case=False, na=False) |
                    df['facid'].str.contains(quick_search, case=False, na=False)
                )
                filtered_df_indices = df[search_mask].index
                full_list = full_list.loc[filtered_df_indices]
                search_applied = True
            
            # Gender filter
            if gender_filter != "All":
                if search_applied:
                    # Apply gender filter to already filtered data
                    gender_mask = df.loc[full_list.index, 'gender'] == gender_filter
                    full_list = full_list[gender_mask]
                else:
                    # Apply gender filter to all data
                    gender_mask = df['gender'] == gender_filter
                    filtered_df_indices = df[gender_mask].index
                    full_list = full_list.loc[filtered_df_indices]
                search_applied = True
            
            # Rename columns for better display
            full_list = full_list.rename(columns={
                'full_name': 'Patient Name',
                'risk_level': 'Risk Level',
                'age_group': 'Age Group', 
                'vdate': 'Admission Date',
                'gender': 'Gender',
                'facid': 'Department',
                'lengthofstay': 'Length of Stay',
                'rcount': 'Risk Count'
            })
            
            # Sort by admission date (most recent first)
            full_list = full_list.sort_values('Admission Date', ascending=False)
            
            # Show different titles based on search
            if search_applied:
                search_terms = []
                if quick_search:
                    search_terms.append(f"'{quick_search}'")
                if gender_filter != "All":
                    search_terms.append(f"Gender: {gender_filter}")
                
                if search_terms:
                    st.markdown(f"**Search Results** ({len(full_list)} patients matching {' & '.join(search_terms)})")
                else:
                    st.markdown(f"**Filtered Results** ({len(full_list)} patients)")
            else:
                st.markdown(f"**All Patients** ({len(full_list)} patients)")
            
            # Add pagination for better performance
            items_per_page = 20
            total_pages = (len(full_list) - 1) // items_per_page + 1
            
            col_page1, col_page2, col_page3 = st.columns([1, 2, 1])
            with col_page2:
                current_page = st.selectbox("Page", range(1, total_pages + 1), key="full_list_page")
            
            # Ensure current_page is not None
            if current_page is None:
                current_page = 1
                
            start_idx = (current_page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            page_data = full_list.iloc[start_idx:end_idx]
            
            # Column headers
            header_col1, header_col2, header_col3, header_col4, header_col5, header_col6, header_col7, header_col8 = st.columns([2, 1, 1, 1, 1, 1, 1, 1])
            with header_col1:
                st.write("**Patient Name**")
            with header_col2:
                st.write("**Risk Level**")
            with header_col3:
                st.write("**Age Group**")
            with header_col4:
                st.write("**Admission Date**")
            with header_col5:
                st.write("**Gender**")
            with header_col6:
                st.write("**Department**")
            with header_col7:
                st.write("**Length of Stay**")
            with header_col8:
                st.write("**Risk Count**")
            
            st.divider()
            
            # Display patients with clickable names
            for idx, row in page_data.iterrows():
                col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([2, 1, 1, 1, 1, 1, 1, 1])
                
                with col1:
                    # Get original patient ID for this row
                    patient_id = df.loc[idx, 'eid']
                    if st.button(f"▸ {row['Patient Name']}", key=f"full_list_patient_{patient_id}"):
                        st.session_state.current_page = "patient_detail"
                        st.session_state.selected_patient = patient_id
                        st.rerun()
                
                with col2:
                    # Color code the risk level
                    risk_color = "●" if row['Risk Level'] == "High Risk" else "○"
                    st.write(f"{risk_color} {row['Risk Level']}")
                with col3:
                    st.write(row['Age Group'])
                with col4:
                    st.write(row['Admission Date'])
                with col5:
                    st.write(row['Gender'])
                with col6:
                    st.write(row['Department'])
                with col7:
                    st.write(f"{row['Length of Stay']} days")
                with col8:
                    st.write(row['Risk Count'])
        else:
            st.info("No patients found with current filters")
    
    with tab2:
        st.markdown("**Search Patients**")
        search_term = st.text_input("Search by patient name or department:")
        
        if search_term and not df.empty:
            # Filter data based on search term
            search_mask = (
                df['full_name'].str.contains(search_term, case=False, na=False) |
                df['facid'].str.contains(search_term, case=False, na=False)
            )
            search_results = df[search_mask]
            
            if not search_results.empty:
                display_cols = ['full_name', 'risk_level', 'age_group', 'vdate', 'gender', 'facid', 'lengthofstay', 'rcount']
                search_display = search_results[display_cols].copy()
                search_display['vdate'] = search_display['vdate'].dt.strftime('%Y-%m-%d')
                
                search_display = search_display.rename(columns={
                    'full_name': 'Patient Name',
                    'age_group': 'Age Group',
                    'vdate': 'Admission Date', 
                    'gender': 'Gender',
                    'facid': 'Department',
                    'lengthofstay': 'Length of Stay',
                    'rcount': 'Risk Count'
                })
                
                st.markdown(f"**Search Results** ({len(search_display)} patients)")
                
                # Column headers
                header_col1, header_col2, header_col3, header_col4, header_col5, header_col6, header_col7, header_col8 = st.columns([2, 1, 1, 1, 1, 1, 1, 1])
                with header_col1:
                    st.write("**Patient Name**")
                with header_col2:
                    st.write("**Risk Level**")
                with header_col3:
                    st.write("**Age Group**")
                with header_col4:
                    st.write("**Admission Date**")
                with header_col5:
                    st.write("**Gender**")
                with header_col6:
                    st.write("**Department**")
                with header_col7:
                    st.write("**Length of Stay**")
                with header_col8:
                    st.write("**Risk Count**")
                
                st.divider()
                
                # Display search results with clickable names
                for idx, row in search_display.iterrows():
                    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([2, 1, 1, 1, 1, 1, 1, 1])
                    
                    with col1:
                        # Get original patient ID for this row
                        patient_id = search_results.loc[idx, 'eid']
                        if st.button(f"▸ {row['Patient Name']}", key=f"search_patient_{patient_id}"):
                            st.session_state.current_page = "patient_detail"
                            st.session_state.selected_patient = patient_id
                            st.rerun()
                    
                    with col2:
                        # Color code the risk level
                        risk_color = "●" if row['Risk Level'] == "High Risk" else "○"
                        st.write(f"{risk_color} {row['Risk Level']}")
                    with col3:
                        st.write(row['Age Group'])
                    with col4:
                        st.write(row['Admission Date'])
                    with col5:
                        st.write(row['Gender'])
                    with col6:
                        st.write(row['Department'])
                    with col7:
                        st.write(f"{row['Length of Stay']} days")
                    with col8:
                        st.write(row['Risk Count'])
            else:
                st.info(f"No patients found matching '{search_term}'")

def add_floating_chat():
    """Add floating chat widget to the bottom right corner"""
    # Initialize session state for floating chat
    if 'float_chat_visible' not in st.session_state:
        st.session_state.float_chat_visible = False
    if 'float_chat_messages' not in st.session_state:
        st.session_state.float_chat_messages = []
    
    # CSS and HTML for floating chat
    st.markdown("""
    <style>
    /* Floating chat button */
    .floating-chat-btn {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #2E5266, #4A90A4);
        border-radius: 50%;
        box-shadow: 0 4px 20px rgba(46, 82, 102, 0.3);
        cursor: pointer;
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 24px;
        border: none;
        transition: all 0.3s ease;
    }
    
    .floating-chat-btn:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 30px rgba(46, 82, 102, 0.4);
    }
    
    /* Floating chat window */
    .floating-chat-window {
        position: fixed;
        bottom: 100px;
        right: 30px;
        width: 350px;
        height: 500px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        z-index: 1001;
        display: none;
        flex-direction: column;
        border: 1px solid #E2E8F0;
        overflow: hidden;
    }
    
    .floating-chat-window.visible {
        display: flex;
        animation: slideUp 0.3s ease-out;
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .chat-header {
        background: linear-gradient(135deg, #2E5266, #4A90A4);
        color: white;
        padding: 15px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-weight: 600;
    }
    
    .chat-close {
        cursor: pointer;
        font-size: 20px;
        background: none;
        border: none;
        color: white;
        padding: 0;
    }
    
    .chat-messages {
        flex: 1;
        padding: 15px;
        overflow-y: auto;
        background: #F8FAFC;
    }
    
    .chat-input-area {
        padding: 15px;
        border-top: 1px solid #E2E8F0;
        background: white;
    }
    
    .message {
        margin-bottom: 12px;
        padding: 8px 12px;
        border-radius: 18px;
        max-width: 80%;
        word-wrap: break-word;
    }
    
    .user-message {
        background: #2E5266;
        color: white;
        margin-left: auto;
    }
    
    .bot-message {
        background: white;
        border: 1px solid #E2E8F0;
    }
    </style>
    
    <div id="floating-chat-btn" class="floating-chat-btn" onclick="toggleFloatingChat()">
        ▸
    </div>
    
    <div id="floating-chat-window" class="floating-chat-window">
        <div class="chat-header">
            <span>Healthcare AI Assistant</span>
            <button class="chat-close" onclick="toggleFloatingChat()">✕</button>
        </div>
        <div class="chat-messages" id="chat-messages">
            <div class="message bot-message">
                Hello! I'm your healthcare AI assistant. I can help you analyze patient data, explain medical indicators, and provide insights about the dashboard. What would you like to know?
            </div>
        </div>
        <div class="chat-input-area">
            <input type="text" 
                   id="chat-input" 
                   placeholder="Ask about patient data, medical terms..."
                   style="width: 100%; padding: 10px; border: 1px solid #E2E8F0; border-radius: 20px; outline: none;">
        </div>
    </div>
    
    <script>
    function toggleFloatingChat() {
        const chatWindow = document.getElementById('floating-chat-window');
        chatWindow.classList.toggle('visible');
    }
    
    // Handle chat input
    document.addEventListener('DOMContentLoaded', function() {
        const chatInput = document.getElementById('chat-input');
        const chatMessages = document.getElementById('chat-messages');
        
        if (chatInput) {
            chatInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && this.value.trim()) {
                    sendFloatingMessage(this.value.trim());
                    this.value = '';
                }
            });
        }
    });
    
    function sendFloatingMessage(message) {
        const chatMessages = document.getElementById('chat-messages');
        
        // Add user message
        const userMsg = document.createElement('div');
        userMsg.className = 'message user-message';
        userMsg.textContent = message;
        chatMessages.appendChild(userMsg);
        
        // Add loading indicator
        const loadingMsg = document.createElement('div');
        loadingMsg.className = 'message bot-message';
        loadingMsg.innerHTML = 'Thinking...';
        loadingMsg.id = 'loading-msg';
        chatMessages.appendChild(loadingMsg);
        
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Send to backend (simulate API call for now)
        setTimeout(() => {
            const loading = document.getElementById('loading-msg');
            if (loading) {
                loading.innerHTML = generateFloatingResponse(message);
            }
        }, 1500);
    }
    
    function generateFloatingResponse(userMessage) {
        // Simple response logic - in real implementation this would call the ChatGPT API
        const message = userMessage.toLowerCase();
        
        if (message.includes('risk') || message.includes('high risk')) {
            return 'High-risk patients are those with length of stay > 90th percentile or readmission flags. You can filter them using the Risk Level filter in the sidebar.';
        } else if (message.includes('creatinine')) {
            return 'Creatinine levels indicate kidney function. Higher levels may suggest kidney problems. Normal range is typically 0.6-1.2 mg/dL.';
        } else if (message.includes('length') || message.includes('stay')) {
            return 'Length of stay is a key metric. Longer stays often indicate complex cases or complications. Our data shows average LOS varies by department and patient condition.';
        } else if (message.includes('dashboard') || message.includes('help')) {
            return 'This dashboard shows patient analytics, KPIs, and trends. You can filter by date, gender, department, age group, and risk level. Click patient names to see detailed records.';
        } else {
            return 'I can help with patient data analysis, medical terms, and dashboard navigation. Try asking about "high risk patients", "creatinine levels", or "length of stay".';
        }
    }
    </script>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache responses for 5 minutes
def get_chatgpt_response(user_message, context=""):
    """Get response from ChatGPT API"""
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        system_prompt = """You are a helpful AI assistant specialized in healthcare analytics and data interpretation. 
        You are integrated into a hospital management dashboard that shows:
        - Patient length of stay data
        - Laboratory test results (creatinine, glucose, hematocrit, etc.)
        - Readmission rates
        - Department performance metrics
        - Disease condition impacts on hospital stays
        
        Provide clear, accurate, and professional responses about healthcare data analysis, medical insights, 
        and dashboard interpretation. Keep responses concise but informative. If you're unsure about medical 
        specifics, acknowledge limitations and suggest consulting healthcare professionals."""
        
        if context:
            system_prompt += f"\n\nCurrent dashboard context: {context}"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"I apologize, but I'm having trouble connecting to my AI service right now. Error: {str(e)[:100]}... Please try again later or contact support if the issue persists."

def add_chat_widget_DISABLED():
    """Add floating chat widget with ChatGPT integration"""
    
    # Initialize chat messages in session state
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hi! I'm your AI assistant for healthcare analytics. Ask me about the dashboard data, medical insights, or any questions you have!"}
        ]
    
    # Force reset floating chat visibility to ensure it starts hidden
    st.session_state.float_chat_visible = False
    
    if "chat_visible" not in st.session_state:
        st.session_state.chat_visible = False
    
    # Handle new messages
    if "pending_message" in st.session_state and st.session_state.pending_message:
        user_message = st.session_state.pending_message
        st.session_state.pending_message = ""
        
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": user_message})
        
        # Get ChatGPT response
        with st.spinner("AI Assistant is thinking..."):
            ai_response = get_chatgpt_response(user_message)
            st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
        
        # Force rerun to update the chat
        st.rerun()
    
    # Create a sidebar for chat functionality
    with st.sidebar:
        st.markdown("---")
        
        # Chat toggle button
        if st.button("▸ AI Assistant", use_container_width=True, help="Chat with AI about the dashboard data"):
            st.session_state.chat_visible = not st.session_state.chat_visible
        
        # Show chat interface if visible
        if st.session_state.chat_visible:
            st.markdown("### AI Healthcare Assistant")
            
            # Display chat messages
            chat_container = st.container()
            with chat_container:
                # Display chat history in a scrollable area
                for i, message in enumerate(st.session_state.chat_messages):
                    if message["role"] == "user":
                        st.markdown(f"""
                        <div style="background-color: #2E5266; color: white; padding: 0.75rem; border-radius: 0.75rem; margin: 0.5rem 0; margin-left: 2rem;">
                            {message["content"]}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background-color: #F1F5F9; color: #2D3748; padding: 0.75rem; border-radius: 0.75rem; margin: 0.5rem 0; margin-right: 2rem;">
                            {message["content"]}
                        </div>
                        """, unsafe_allow_html=True)
            
            # Chat input
            user_input = st.text_area(
                "Ask me anything about the healthcare data:",
                key="sidebar_chat_input",
                height=80,
                placeholder="E.g., 'What do the creatinine levels tell us about patient outcomes?'"
            )
            
            # Send button
            col1, col2 = st.columns([2, 1])
            with col1:
                if st.button("Send", key="sidebar_send_message", use_container_width=True, type="primary"):
                    if user_input and user_input.strip():
                        st.session_state.pending_message = user_input.strip()
                        st.rerun()
            
            with col2:
                if st.button("Clear", key="sidebar_clear_chat", use_container_width=True):
                    st.session_state.chat_messages = [
                        {"role": "assistant", "content": "Hi! I'm your AI assistant for healthcare analytics. Ask me about the dashboard data, medical insights, or any questions you have!"}
                    ]
                    st.rerun()
    
    # Floating chat functionality
    # Toggle floating chat when button is clicked
    if st.button("", key="float_chat_toggle", help="Open floating AI chat"):
        st.session_state.float_chat_visible = not st.session_state.float_chat_visible
        st.rerun()
    
    # Floating chat button and modal
    chat_visibility = "block" if st.session_state.float_chat_visible else "none"
    
    # This function has been disabled - all functionality moved to dynamic JavaScript chat
    pass

if __name__ == "__main__":
    main()
    
