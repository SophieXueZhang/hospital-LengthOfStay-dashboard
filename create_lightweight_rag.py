#!/usr/bin/env python3
"""
Create a lightweight RAG system for Streamlit Cloud deployment
"""

import sqlite3
import json
import os

def create_lightweight_db():
    """Create a lightweight database with just paper metadata and text chunks"""

    # Sample medical papers data for demonstration
    sample_papers = [
        {
            "id": 1,
            "filename": "anemia_study.pdf",
            "title": "Anemia in General Medical Inpatients Prolongs Length of Stay and Increases 30-day Unplanned Readmission Rate",
            "author": "Kim et al.",
            "year": "2019",
            "chunk_text": "Anemia is associated with increased length of hospital stay in medical patients. Our study of 1,247 patients found that anemic patients had significantly longer stays (7.2 vs 4.8 days, p<0.001) and higher readmission rates (18.3% vs 12.1%, p<0.01). Low hemoglobin levels correlate with increased complications and delayed discharge.",
            "keywords": "anemia,hemoglobin,length of stay,readmission,medical patients"
        },
        {
            "id": 2,
            "filename": "pneumonia_los.pdf",
            "title": "Duration of length of stay in pneumonia: influence of clinical factors and hospital type",
            "author": "Rodriguez et al.",
            "year": "2018",
            "chunk_text": "Pneumonia patients show variable length of stay depending on severity and comorbidities. Community-acquired pneumonia averaged 5.1 days while hospital-acquired pneumonia averaged 8.7 days. Factors associated with longer stays include age >65, comorbid conditions, and severity scores.",
            "keywords": "pneumonia,length of stay,respiratory infection,comorbidities,severity"
        },
        {
            "id": 3,
            "filename": "asthma_hospitalization.pdf",
            "title": "Trends in adult asthma hospitalization: gender-age effect",
            "author": "Chen et al.",
            "year": "2017",
            "chunk_text": "Adult asthma hospitalizations show distinct patterns by age and gender. Women aged 25-44 have higher hospitalization rates than men. Length of stay averages 3.2 days for asthma exacerbations. Factors influencing duration include severity of exacerbation and response to initial treatment.",
            "keywords": "asthma,hospitalization,respiratory,exacerbation,treatment response"
        },
        {
            "id": 4,
            "filename": "diabetes_complications.pdf",
            "title": "Diabetes complications and hospital length of stay analysis",
            "author": "Thompson et al.",
            "year": "2020",
            "chunk_text": "Diabetic patients with complications show extended hospital stays. Hyperglycemia is associated with longer recovery times and increased infection risk. Proper glucose control reduces length of stay by an average of 1.8 days. HbA1c levels >9% correlate with extended admissions.",
            "keywords": "diabetes,glucose,hyperglycemia,complications,infection,recovery"
        },
        {
            "id": 5,
            "filename": "kidney_disease_outcomes.pdf",
            "title": "Chronic kidney disease impact on hospital outcomes",
            "author": "Williams et al.",
            "year": "2021",
            "chunk_text": "Chronic kidney disease patients require longer hospitalizations due to fluid management and medication adjustments. Average length of stay is 6.8 days vs 4.2 days for non-CKD patients. Creatinine levels >2.0 mg/dL are associated with significantly longer stays and higher readmission rates.",
            "keywords": "kidney disease,creatinine,fluid management,medication,readmission"
        }
    ]

    # Create database
    os.makedirs('data', exist_ok=True)
    db_path = 'data/papers_rag.db'

    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
        CREATE TABLE paper_chunks (
            id INTEGER PRIMARY KEY,
            filename TEXT,
            title TEXT,
            author TEXT,
            year TEXT,
            chunk_text TEXT,
            keywords TEXT,
            embedding BLOB
        )
    ''')

    # Insert sample data
    for paper in sample_papers:
        cursor.execute('''
            INSERT INTO paper_chunks (filename, title, author, year, chunk_text, keywords, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            paper['filename'],
            paper['title'],
            paper['author'],
            paper['year'],
            paper['chunk_text'],
            paper['keywords'],
            None  # No embeddings for lightweight version
        ))

    conn.commit()
    conn.close()

    print(f"Created lightweight database at {db_path}")
    print(f"Database size: {os.path.getsize(db_path) / 1024:.1f} KB")

if __name__ == "__main__":
    create_lightweight_db()