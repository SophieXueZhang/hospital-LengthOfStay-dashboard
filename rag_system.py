#!/usr/bin/env python3
"""
RAG Retrieval System: Search relevant papers based on patient symptoms
"""

import os
import sqlite3
import json
import openai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RAGSystem:
    def __init__(self, db_path=None):
        # Auto-detect database path for different environments
        if db_path is None:
            possible_paths = [
                '/Users/pc/Documents/cursor/ml_course/project/data/papers_rag.db',  # Local development
                './data/papers_rag.db',  # Streamlit Cloud
                'data/papers_rag.db',    # Alternative path
            ]
            self.db_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    self.db_path = path
                    break
        else:
            self.db_path = db_path

        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Manual paper metadata mapping (fallback for papers without extractable metadata)
        self.paper_metadata_map = {
            "Anemia in General Medical Inpatients Prolongs Length of Stay and Increases 30-day Unplanned Readmission Rate.pdf": {
                "year": "2019", "author": "Kim et al."
            },
            "Prevalence and risk factors for hospital‑acquired anemia in internal medicine patients- learning from the \"less is more\" perspective.pdf": {
                "year": "2020", "author": "Thavendiranathan et al."
            },
            "Prevalence and risk factors for hospital‑acquired anemia in internal medicine patients- learning from the \"less is more\" perspective.pdf": {
                "year": "2020", "author": "Thavendiranathan et al."
            },
            "Length of hospital stay, delayed pneumonia diagnosis and post-discharge mortality. The Pneumonia in Italian Acute Care for Elderly units (PIACE)-SIGOT study.pdf": {
                "year": "2025", "author": "Fimognari et al."
            },
            "Duration of length of stay in pneumonia- influence of clinical factors and hospital type.pdf": {
                "year": "2018", "author": "Rodriguez et al."
            },
            "Trends in adult asthma hospitalization- gender-age effect.pdf": {
                "year": "2017", "author": "Chen et al."
            }
        }
        
        # Medical symptom keyword mapping
        self.symptom_keywords = {
            'anemia': ['anemia', 'anemic', 'hemoglobin', 'hematocrit', 'iron deficiency', 'low blood count'],
            'pneumonia': ['pneumonia', 'lung infection', 'respiratory infection', 'chest infection'],
            'asthma': ['asthma', 'breathing problems', 'respiratory issues', 'airway obstruction'],
            'depression': ['depression', 'depressive', 'mental health', 'psychiatric', 'mood disorder'],
            'anxiety': ['anxiety', 'anxious', 'stress', 'panic', 'worry'],
            'diabetes': ['diabetes', 'diabetic', 'blood sugar', 'glucose', 'insulin'],
            'hypertension': ['hypertension', 'high blood pressure', 'blood pressure'],
            'heart disease': ['heart disease', 'cardiac', 'cardiovascular', 'heart failure'],
            'kidney disease': ['kidney disease', 'renal', 'nephrology', 'dialysis'],
            'substance abuse': ['substance abuse', 'drug abuse', 'addiction', 'substance use disorder']
        }

    def is_available(self):
        """Check if RAG system is available"""
        return self.db_path is not None and os.path.exists(self.db_path)

    def get_embedding(self, text):
        """Get text embedding"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return np.array(response.data[0].embedding)
        except Exception as e:
            print(f"Failed to get embedding: {e}")
            return None
    
    def extract_paper_metadata(self, filename, paper_text=None):
        """Extract year and author from paper filename and content"""
        import re
        
        year = None
        author = None
        
        # Remove file extension
        name = filename.replace('.pdf', '').replace('.txt', '')
        
        # First try to extract from filename
        # Extract year (4 digits)
        year_match = re.search(r'\b(19|20)\d{2}\b', name)
        if year_match:
            year = year_match.group()
        
        # Extract author patterns - only for specific academic formats
        # Only try to extract author if filename follows academic naming conventions
        if '-' in name and any(pattern in name.lower() for pattern in ['et-al', '-and-', '-']):
            author_patterns = [
                r'^([a-zA-Z-]+(?:-et-al)?)-\d{4}',  # author-et-al-2012
                r'^([a-zA-Z-]+(?:-[a-zA-Z-]+){1,2}?)-(?:and|et-al|\d{4})',  # multi-author patterns (limit to 2 parts)
            ]
            
            for pattern in author_patterns:
                author_match = re.search(pattern, name)
                if author_match:
                    author_raw = author_match.group(1)
                    # Only accept if it looks like a name (not starting with common words)
                    common_words = ['a', 'an', 'the', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
                    first_word = author_raw.split('-')[0].lower()
                    if first_word not in common_words and len(first_word) > 2:
                        # Clean up author name
                        if 'et-al' in author_raw:
                            author = author_raw.replace('-et-al', ' et al.').replace('-', ' ').title()
                        else:
                            author = author_raw.replace('-', ' ').title()
                        break
        
        # If no year found from filename, try to extract from paper content
        if not year and paper_text:
            # Look for years in common publication patterns
            year_patterns = [
                r'\b(19|20)\d{2}\b',  # General 4-digit years
                r'published.*?(\d{4})',  # "published in 2020"
                r'copyright.*?(\d{4})',  # "copyright 2019"
                r'\((\d{4})\)',  # Years in parentheses
            ]
            
            # Only look at first 2000 characters to avoid false positives
            text_sample = paper_text[:2000] if paper_text else ""
            
            for pattern in year_patterns:
                matches = re.findall(pattern, text_sample, re.IGNORECASE)
                if matches:
                    # Take the first reasonable year (between 1990-2030)
                    for match in matches:
                        year_val = int(match if isinstance(match, str) else match[-1])
                        if 1990 <= year_val <= 2030:
                            year = str(year_val)
                            break
                    if year:
                        break
        
        # Fallback to manual mapping if automatic extraction didn't find anything
        if not year and not author and filename in self.paper_metadata_map:
            metadata = self.paper_metadata_map[filename]
            year = metadata.get("year")
            author = metadata.get("author")
        
        return year, author
    
    def extract_symptoms_from_patient(self, patient_data):
        """Extract symptom keywords and diagnostic basis from patient data"""
        symptoms = []
        diagnostic_info = []
        
        # Check various medical indicators - using stricter thresholds
        # Severe anemia: hematocrit < 8
        if patient_data.get('hematocrit', 0) < 8:
            symptoms.append('anemia')
            hct_value = patient_data.get('hematocrit', 0)
            diagnostic_info.append(f"Severe Anemia (Hematocrit: {hct_value:.1f}g/dL, Normal: 12-16g/dL)")
        
        # Check specific disease flags
        if patient_data.get('irondef', 0) == 1:
            symptoms.append('anemia')
            diagnostic_info.append("Iron Deficiency Anemia (Iron deficiency indicator positive)")
            
        if patient_data.get('hemo', 0) == 1:
            symptoms.append('anemia')
            diagnostic_info.append("Anemia (Hemoglobin abnormal indicator positive)")
            
        if patient_data.get('asthma', 0) == 1:
            symptoms.append('asthma')
            respiration = patient_data.get('respiration', 0)
            neutrophils = patient_data.get('neutrophils', 0)
            lab_findings = []
            if respiration > 20:
                lab_findings.append(f"Elevated respiratory rate: {respiration}/min (Normal: 12-20)")
            if neutrophils > 70:
                lab_findings.append(f"Elevated neutrophils: {neutrophils:.1f}% (Normal: 40-70%)")
            
            if lab_findings:
                diagnostic_info.append(f"Asthma (Diagnostic marker positive, {'; '.join(lab_findings)})")
            else:
                diagnostic_info.append("Asthma (Asthma diagnostic marker positive)")
            
        if patient_data.get('pneum', 0) == 1:
            symptoms.append('pneumonia')
            respiration = patient_data.get('respiration', 0)
            neutrophils = patient_data.get('neutrophils', 0)
            lab_findings = []
            if respiration > 20:
                lab_findings.append(f"Elevated respiratory rate: {respiration}/min (Normal: 12-20)")
            if neutrophils > 70:
                lab_findings.append(f"Elevated neutrophils: {neutrophils:.1f}% (Normal: 40-70%)")
            
            if lab_findings:
                diagnostic_info.append(f"Pneumonia (Diagnostic marker positive, {'; '.join(lab_findings)})")
            else:
                diagnostic_info.append("Pneumonia (Pneumonia diagnostic marker positive)")
            
        if patient_data.get('depress', 0) == 1:
            symptoms.append('depression')
            diagnostic_info.append("Depression (Diagnostic marker positive)")
            
        if patient_data.get('psychologicaldisordermajor', 0) == 1:
            symptoms.append('depression')
            diagnostic_info.append("Major Psychological Disorder (Diagnostic marker positive)")
            
        if patient_data.get('substancedependence', 0) == 1:
            symptoms.append('substance abuse')
            # Substance dependence may lead to malnutrition and electrolyte imbalance, these are reasonable associations
            sodium = patient_data.get('sodium', 0)
            if sodium < 135:
                diagnostic_info.append(f"Substance Dependence (Diagnostic marker positive, possible electrolyte imbalance: Sodium {sodium:.1f} mEq/L, Normal: 135-145)")
            else:
                diagnostic_info.append("Substance Dependence (Diagnostic marker positive)")
            
        if patient_data.get('dialysisrenalendstage', 0) == 1:
            symptoms.append('kidney disease')
            creatinine = patient_data.get('creatinine', 0)
            bloodureanitro = patient_data.get('bloodureanitro', 0)
            lab_findings = []
            if creatinine > 1.2:
                lab_findings.append(f"Elevated creatinine: {creatinine:.2f} mg/dL (Normal: 0.6-1.2)")
            if bloodureanitro > 25:
                lab_findings.append(f"Elevated blood urea nitrogen: {bloodureanitro:.1f} mg/dL (Normal: 7-25)")
            
            if lab_findings:
                diagnostic_info.append(f"End-stage Renal Disease (Dialysis treatment marker positive, {'; '.join(lab_findings)})")
            else:
                diagnostic_info.append("End-stage Renal Disease (Dialysis treatment marker positive)")
        
        # 检查诊断代码或其他字段中的症状
        diagnosis = str(patient_data.get('diagnosis', '')).lower()
        for symptom, keywords in self.symptom_keywords.items():
            for keyword in keywords:
                if keyword in diagnosis:
                    symptoms.append(symptom)
                    diagnostic_info.append(f"{symptom.title()} (Diagnosis code contains: {keyword})")
                    break
        
        # 如果没有找到特定症状，添加通用医学术语
        if not symptoms:
            symptoms = ['length of stay', 'hospital admission', 'medical care']
        
        return list(set(symptoms)), diagnostic_info  # 去重，返回症状和诊断依据
    
    def search_relevant_papers(self, query, top_k=3):
        """搜索相关论文"""
        try:
            # 检查数据库是否存在
            if not self.is_available():
                return []

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 检查数据库结构 - 支持新的轻量数据库
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]

            if 'paper_chunks' in tables:
                # 新的轻量数据库结构 - 基于关键词搜索
                return self._search_lightweight_db(cursor, query, top_k)
            elif 'chunks' in tables:
                # 原有的向量数据库结构
                return self._search_vector_db(cursor, query, top_k)
            else:
                conn.close()
                return []

        except Exception as e:
            print(f"Search error: {e}")
            return []

    def _search_lightweight_db(self, cursor, query, top_k=3):
        """在轻量数据库中基于关键词搜索"""
        query_lower = query.lower()

        # 获取所有论文 - 使用正确的字段名
        cursor.execute('SELECT filename, title, authors, year, chunk_text FROM paper_chunks')
        all_papers = cursor.fetchall()

        scored_papers = []

        for paper in all_papers:
            filename, title, authors, year, chunk_text = paper
            score = 0

            # 基于内容匹配计分
            content_lower = (chunk_text or '').lower()
            title_lower = (title or '').lower()

            # 医学关键词匹配
            medical_keywords = [
                'anemia', 'pneumonia', 'diabetes', 'kidney', 'renal', 'asthma',
                'depression', 'length of stay', 'hospital', 'readmission',
                'mortality', 'complications', 'treatment', 'diagnosis',
                'creatinine', 'glucose', 'hematocrit', 'blood', 'medication'
            ]

            # 检查查询词是否在标题中 (高权重)
            for word in query_lower.split():
                if word in title_lower:
                    score += 15
                if word in content_lower:
                    score += 5

            # 检查医学关键词匹配
            for keyword in medical_keywords:
                if keyword in query_lower and keyword in content_lower:
                    score += 8

            # 基于标题匹配计分
            if title:
                title_words = title.lower().split()
                query_words = query_lower.split()
                for query_word in query_words:
                    for title_word in title_words:
                        if query_word in title_word or title_word in query_word:
                            score += 5

            # 基于内容匹配计分
            if chunk_text:
                content_lower = chunk_text.lower()
                query_words = query_lower.split()
                for word in query_words:
                    if word in content_lower:
                        score += 3

            if score > 0:
                scored_papers.append({
                    'filename': filename,
                    'title': title,
                    'authors': authors,  # 修正字段名
                    'year': year,
                    'chunk_text': chunk_text,
                    'score': score
                })

        # 按分数排序并返回前top_k个
        scored_papers.sort(key=lambda x: x['score'], reverse=True)
        return scored_papers[:top_k]

    def _search_vector_db(self, cursor, query, top_k=3):
        """在向量数据库中搜索（原有方法）"""
        # 检查数据库中是否有数据
        cursor.execute('SELECT COUNT(*) FROM chunks')
        count = cursor.fetchone()[0]
        if count == 0:
            return []

        # 获取查询的embedding
        query_embedding = self.get_embedding(query)
        if query_embedding is None:
            return []

        # 获取所有chunks和它们的embeddings
        cursor.execute('''
            SELECT c.id, c.chunk_text, c.embedding, p.title, p.filename
            FROM chunks c
            JOIN papers p ON c.paper_id = p.id
            WHERE c.embedding IS NOT NULL
        ''')

        results = cursor.fetchall()

        if not results:
            return []

        # 计算相似度
        similarities = []
        for result in results:
            chunk_id, chunk_text, embedding_json, title, filename = result
            try:
                chunk_embedding = np.array(json.loads(embedding_json))
                similarity = cosine_similarity([query_embedding], [chunk_embedding])[0][0]
                similarities.append({
                    'chunk_id': chunk_id,
                    'chunk_text': chunk_text,
                    'title': title,
                    'filename': filename,
                    'similarity': similarity
                })
            except Exception as e:
                continue

        # 按相似度排序并返回top_k结果
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]
    
    def get_rag_response_for_patient(self, patient_data, user_question=None):
        """Generate RAG-based response for patient"""
        # 提取患者症状和诊断依据
        symptoms, diagnostic_info = self.extract_symptoms_from_patient(patient_data)
        
        # 构建搜索查询
        if user_question:
            search_query = f"{user_question} {' '.join(symptoms)}"
        else:
            search_query = ' '.join(symptoms)
        
        # 搜索相关论文 - 增加数量以获取更多相关文献
        relevant_papers = self.search_relevant_papers(search_query, top_k=10)
        
        if not relevant_papers:
            return None, [], diagnostic_info
        
        # Filter high similarity papers (0.8 and above) and build context (deduplicate)
        context_texts = []
        paper_references = []
        seen_titles = set()
        high_quality_papers = []
        
        for paper in relevant_papers:
            # Handle both similarity (vector DB) and score (lightweight DB)
            paper_score = paper.get('similarity', paper.get('score', 0))
            score_threshold = 0.8 if 'similarity' in paper else 5  # Different thresholds for different systems

            if paper_score >= score_threshold and paper['title'] not in seen_titles:
                # 优先使用数据库中的元数据，如果没有再从文件名提取
                author = paper.get('authors', 'Unknown')
                year = paper.get('year', None)

                # 如果数据库中没有，再尝试从文件名和内容提取
                if not author or author == 'Unknown':
                    extracted_year, extracted_author = self.extract_paper_metadata(paper['filename'], paper['chunk_text'])
                    if extracted_author:
                        author = extracted_author
                    if extracted_year and not year:
                        year = extracted_year
                metadata_str = ""
                if year or author:
                    metadata_parts = []
                    if author:
                        metadata_parts.append(str(author))
                    if year:
                        metadata_parts.append(str(year))
                    metadata_str = f" ({', '.join(metadata_parts)})"
                
                score_text = f"similarity: {paper_score:.3f}" if 'similarity' in paper else f"relevance score: {paper_score}"
                # 只添加纯文本内容到context，不包含论文标题和元数据
                context_texts.append(paper['chunk_text'][:800])

                # 确保paper对象包含完整的元数据信息
                paper['authors'] = author  # 确保authors字段存在
                paper['year'] = year       # 确保year字段存在

                paper_references.append({
                    'title': paper['title'],
                    'year': year,
                    'author': author,
                    'filename': paper['filename']
                })
                seen_titles.add(paper['title'])
                high_quality_papers.append(paper)
        
        context = "\n\n".join(context_texts)
        
        # 生成回答
        prompt = f"""Based on the following medical literature content, provide a clinical analysis for the patient.

Patient symptom keywords: {', '.join(symptoms)}
Diagnostic basis: {'; '.join(diagnostic_info)}
User question: {user_question if user_question else 'Please provide relevant medical information'}

Relevant literature content:
{context}

Please provide ONLY the clinical conclusions and medical recommendations. Do NOT mention paper titles, authors, years, or reference citations in your response. Focus on:

1. Clinical findings and conclusions from the research
2. How these findings relate to the patient's condition
3. Evidence-based medical recommendations
4. Risk factors and prognosis
5. Treatment considerations

Write as a clinical summary that directly addresses the patient's condition without mentioning the source papers."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a medical assistant that answers questions based on provided literature content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content

            # 不在这里添加引用，让app.py单独处理
            return ai_response, relevant_papers, diagnostic_info
            
        except Exception as e:
            print(f"Failed to generate RAG response: {e}")
            return None, relevant_papers, diagnostic_info

# Global RAG system instance
rag_system = RAGSystem()