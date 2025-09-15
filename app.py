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
    page_icon="⚕️",
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
        padding: 2rem 0;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 1rem 1rem;
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
    
    /* Move sidebar to right side with proper layout */
    .css-1d391kg, .css-1cypcdb, .css-17lntkn, 
    [data-testid="stSidebar"], 
    .css-1aumxhk, .css-1y0tads, .css-1lcbmhc,
    section[data-testid="stSidebar"] {
        position: static !important;
        order: 2 !important;
        flex-shrink: 0 !important;
        width: 320px !important;
        max-width: 320px !important;
        min-width: 320px !important;
    }
    
    /* Ensure proper flex layout for main app container */
    .css-1rs6os, .css-17ziqus, [data-testid="stAppViewContainer"] > .main {
        display: flex !important;
        flex-direction: row !important;
    }
    
    /* Adjust main content area */
    .main .block-container {
        flex: 1 !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: calc(100% - 340px) !important;
    }
    
    /* Responsive adjustments for mobile and tablets */
    @media (max-width: 1024px) {
        /* Stack sidebar below content on smaller screens */
        .css-1rs6os, .css-17ziqus, [data-testid="stAppViewContainer"] > .main {
            flex-direction: column !important;
        }
        
        .css-1d391kg, .css-1cypcdb, .css-17lntkn, 
        [data-testid="stSidebar"], 
        .css-1aumxhk, .css-1y0tads, .css-1lcbmhc,
        section[data-testid="stSidebar"] {
            width: 100% !important;
            max-width: 100% !important;
            min-width: 100% !important;
            order: 1 !important;
        }
        
        .main .block-container {
            max-width: 100% !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        .chat-button {
            bottom: 1rem !important;
            right: 1rem !important;
            width: 50px;
            height: 50px;
        }
        
        .chat-modal {
            bottom: 4rem !important;
            right: 1rem !important;
            left: 1rem !important;
            width: auto;
            height: 400px;
        }
        
        /* Mobile sidebar adjustments */
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
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

def show_patient_detail(patient_id, df):
    """Show detailed patient information"""
    patient = df[df['eid'] == patient_id].iloc[0]
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.current_page = "dashboard"
        st.session_state.selected_patient = None
        st.rerun()
    
    # Patient header
    st.markdown(f"""
    <div class="main-header">
        <div class="main-title">👤 Patient Details: {patient['full_name']}</div>
        <div class="main-subtitle">Comprehensive Medical Record</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Basic information
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Age Group", patient['age_group'])
        st.metric("Gender", patient['gender'])
        
    with col2:
        st.metric("Department", patient['facid'])
        st.metric("Length of Stay", f"{patient['lengthofstay']} days")
        
    with col3:
        st.metric("Risk Count", patient['rcount'])
        st.metric("Readmission", "Yes" if patient['readmit_flag'] == 1 else "No")
    
    # Medical conditions
    st.markdown("### 🏥 Medical Conditions")
    conditions = []
    medical_cols = ['dialysisrenalendstage', 'asthma', 'irondef', 'pneum', 'substancedependence', 
                   'psychologicaldisordermajor', 'depress', 'psychother', 'fibrosisandother', 'malnutrition']
    
    for col in medical_cols:
        if patient[col] == 1:
            conditions.append(col.replace('_', ' ').title())
    
    if conditions:
        for condition in conditions:
            st.write(f"• {condition}")
    else:
        st.write("No recorded medical conditions")
    
    # Lab results
    st.markdown("### 🔬 Laboratory Results")
    lab_col1, lab_col2 = st.columns(2)
    
    with lab_col1:
        st.metric("Hemoglobin", f"{patient['hemo']:.1f}")
        st.metric("Hematocrit", f"{patient['hematocrit']:.1f}")
        st.metric("Neutrophils", f"{patient['neutrophils']:.1f}")
        st.metric("Sodium", f"{patient['sodium']:.1f}")
        
    with lab_col2:
        st.metric("Glucose", f"{patient['glucose']:.1f}")
        st.metric("Blood Urea Nitrogen", f"{patient['bloodureanitro']:.1f}")
        st.metric("Creatinine", f"{patient['creatinine']:.3f}")
        st.metric("BMI", f"{patient['bmi']:.1f}")
    
    # Vital signs
    st.markdown("### 💓 Vital Signs")
    vital_col1, vital_col2 = st.columns(2)
    
    with vital_col1:
        st.metric("Pulse", f"{patient['pulse']} bpm")
        
    with vital_col2:
        st.metric("Respiration", f"{patient['respiration']} /min")
    
    # Timeline
    st.markdown("### 📅 Timeline")
    st.write(f"**Admission Date:** {patient['vdate'].strftime('%Y-%m-%d')}")
    st.write(f"**Discharge Date:** {patient['discharged'].strftime('%Y-%m-%d')}")
    st.write(f"**Date of Birth:** {patient['Date_of_Birth'].strftime('%Y-%m-%d')}")

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
        <div class="main-title">⚕️ Hospital Management Dashboard</div>
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
    
    # Apply filters
    mask = (
        (df['vdate'].dt.date >= start_date) &
        (df['vdate'].dt.date <= end_date) &
        (df['gender'].isin(gender_options)) &
        (df['facid'].isin(dept_options)) &
        (df['age_group'].isin(age_options)) &
        (df['risk_level'].isin(risk_options))
    )
    filtered_df = df[mask]
    
    if filtered_df.empty:
        st.warning("No data available with current filters. Please adjust your selection.")
        return
    
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
        ['creatinine', 'glucose', 'hematocrit', 'hemo', 'neutrophils', 'sodium', 'bloodureanitro'],
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
    tab1, tab2 = st.tabs(["📊 Full Patient List", "🔍 Search & Filter"])
    
    with tab1:
        if not df.empty:
            # Add search functionality at the top
            st.markdown("**🔍 Quick Search**")
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
                    if st.button(f"👤 {row['Patient Name']}", key=f"full_list_patient_{patient_id}"):
                        st.session_state.current_page = "patient_detail"
                        st.session_state.selected_patient = patient_id
                        st.rerun()
                
                with col2:
                    # Color code the risk level
                    risk_color = "🔴" if row['Risk Level'] == "High Risk" else "🟢"
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
                        if st.button(f"👤 {row['Patient Name']}", key=f"search_patient_{patient_id}"):
                            st.session_state.current_page = "patient_detail"
                            st.session_state.selected_patient = patient_id
                            st.rerun()
                    
                    with col2:
                        # Color code the risk level
                        risk_color = "🔴" if row['Risk Level'] == "High Risk" else "🟢"
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
        💬
    </div>
    
    <div id="floating-chat-window" class="floating-chat-window">
        <div class="chat-header">
            <span>🏥 Healthcare AI Assistant</span>
            <button class="chat-close" onclick="toggleFloatingChat()">✕</button>
        </div>
        <div class="chat-messages" id="chat-messages">
            <div class="message bot-message">
                👋 Hello! I'm your healthcare AI assistant. I can help you analyze patient data, explain medical indicators, and provide insights about the dashboard. What would you like to know?
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
        loadingMsg.innerHTML = '🤔 Thinking...';
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
            return '🔴 High-risk patients are those with length of stay > 90th percentile or readmission flags. You can filter them using the Risk Level filter in the sidebar.';
        } else if (message.includes('creatinine')) {
            return '🧪 Creatinine levels indicate kidney function. Higher levels may suggest kidney problems. Normal range is typically 0.6-1.2 mg/dL.';
        } else if (message.includes('length') || message.includes('stay')) {
            return '📊 Length of stay is a key metric. Longer stays often indicate complex cases or complications. Our data shows average LOS varies by department and patient condition.';
        } else if (message.includes('dashboard') || message.includes('help')) {
            return '📈 This dashboard shows patient analytics, KPIs, and trends. You can filter by date, gender, department, age group, and risk level. Click patient names to see detailed records.';
        } else {
            return '🤖 I can help with patient data analysis, medical terms, and dashboard navigation. Try asking about "high risk patients", "creatinine levels", or "length of stay".';
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
        if st.button("💬 AI Assistant", use_container_width=True, help="Chat with AI about the dashboard data"):
            st.session_state.chat_visible = not st.session_state.chat_visible
        
        # Show chat interface if visible
        if st.session_state.chat_visible:
            st.markdown("### 🤖 AI Healthcare Assistant")
            
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
    
