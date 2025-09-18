#!/usr/bin/env python3
"""
RAG检索系统：根据患者症状检索相关论文
"""

import os
import sqlite3
import json
import openai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class RAGSystem:
    def __init__(self, db_path='/Users/pc/Documents/cursor/ml_course/project/data/papers_rag.db'):
        self.db_path = db_path
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # 医学症状关键词映射
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
    
    def get_embedding(self, text):
        """获取文本的embedding"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return np.array(response.data[0].embedding)
        except Exception as e:
            print(f"获取embedding失败: {e}")
            return None
    
    def extract_symptoms_from_patient(self, patient_data):
        """从患者数据中提取症状关键词和诊断依据"""
        symptoms = []
        diagnostic_info = []
        
        # 检查各种医学指标 - 使用更严格的阈值
        # 严重贫血：血细胞比容 < 8
        if patient_data.get('hematocrit', 0) < 8:
            symptoms.append('anemia')
            hct_value = patient_data.get('hematocrit', 0)
            diagnostic_info.append(f"严重贫血 (血细胞比容: {hct_value:.1f}g/dL, 正常值: 12-16g/dL)")
        
        # 检查具体的疾病标志位
        if patient_data.get('irondef', 0) == 1:
            symptoms.append('anemia')
            diagnostic_info.append("缺铁性贫血 (铁缺乏症指标阳性)")
            
        if patient_data.get('hemo', 0) == 1:
            symptoms.append('anemia')
            diagnostic_info.append("贫血 (血红蛋白异常指标阳性)")
            
        if patient_data.get('asthma', 0) == 1:
            symptoms.append('asthma')
            respiration = patient_data.get('respiration', 0)
            neutrophils = patient_data.get('neutrophils', 0)
            lab_findings = []
            if respiration > 20:
                lab_findings.append(f"呼吸频率偏高: {respiration}/min (正常: 12-20)")
            if neutrophils > 70:
                lab_findings.append(f"中性粒细胞偏高: {neutrophils:.1f}% (正常: 40-70%)")
            
            if lab_findings:
                diagnostic_info.append(f"哮喘 (诊断标志阳性, {'; '.join(lab_findings)})")
            else:
                diagnostic_info.append("哮喘 (哮喘诊断标志阳性)")
            
        if patient_data.get('pneum', 0) == 1:
            symptoms.append('pneumonia')
            respiration = patient_data.get('respiration', 0)
            neutrophils = patient_data.get('neutrophils', 0)
            lab_findings = []
            if respiration > 20:
                lab_findings.append(f"呼吸频率偏高: {respiration}/min (正常: 12-20)")
            if neutrophils > 70:
                lab_findings.append(f"中性粒细胞偏高: {neutrophils:.1f}% (正常: 40-70%)")
            
            if lab_findings:
                diagnostic_info.append(f"肺炎 (诊断标志阳性, {'; '.join(lab_findings)})")
            else:
                diagnostic_info.append("肺炎 (肺炎诊断标志阳性)")
            
        if patient_data.get('depress', 0) == 1:
            symptoms.append('depression')
            diagnostic_info.append("抑郁症 (诊断标志阳性)")
            
        if patient_data.get('psychologicaldisordermajor', 0) == 1:
            symptoms.append('depression')
            diagnostic_info.append("重性心理障碍 (诊断标志阳性)")
            
        if patient_data.get('substancedependence', 0) == 1:
            symptoms.append('substance abuse')
            # 物质依赖可能导致营养不良和电解质紊乱，这些是合理的关联
            sodium = patient_data.get('sodium', 0)
            if sodium < 135:
                diagnostic_info.append(f"物质依赖 (诊断标志阳性, 可能伴有电解质紊乱: 血钠 {sodium:.1f} mEq/L, 正常: 135-145)")
            else:
                diagnostic_info.append("物质依赖 (诊断标志阳性)")
            
        if patient_data.get('dialysisrenalendstage', 0) == 1:
            symptoms.append('kidney disease')
            creatinine = patient_data.get('creatinine', 0)
            bloodureanitro = patient_data.get('bloodureanitro', 0)
            lab_findings = []
            if creatinine > 1.2:
                lab_findings.append(f"肌酐偏高: {creatinine:.2f} mg/dL (正常: 0.6-1.2)")
            if bloodureanitro > 25:
                lab_findings.append(f"血尿素氮偏高: {bloodureanitro:.1f} mg/dL (正常: 7-25)")
            
            if lab_findings:
                diagnostic_info.append(f"终末期肾病 (透析治疗标志阳性, {'; '.join(lab_findings)})")
            else:
                diagnostic_info.append("终末期肾病 (透析治疗标志阳性)")
        
        # 检查诊断代码或其他字段中的症状
        diagnosis = str(patient_data.get('diagnosis', '')).lower()
        for symptom, keywords in self.symptom_keywords.items():
            for keyword in keywords:
                if keyword in diagnosis:
                    symptoms.append(symptom)
                    diagnostic_info.append(f"{symptom.title()} (诊断代码包含: {keyword})")
                    break
        
        # 如果没有找到特定症状，添加通用医学术语
        if not symptoms:
            symptoms = ['length of stay', 'hospital admission', 'medical care']
        
        return list(set(symptoms)), diagnostic_info  # 去重，返回症状和诊断依据
    
    def search_relevant_papers(self, query, top_k=3):
        """搜索相关论文"""
        try:
            # 检查数据库是否存在
            if not os.path.exists(self.db_path):
                return []
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查数据库中是否有数据
            cursor.execute('SELECT COUNT(*) FROM chunks')
            count = cursor.fetchone()[0]
            if count == 0:
                conn.close()
                return []
            
            # 获取查询的embedding
            query_embedding = self.get_embedding(query)
            if query_embedding is None:
                conn.close()
                return []
            
            # 获取所有chunks和它们的embeddings
            cursor.execute('''
                SELECT c.id, c.chunk_text, c.embedding, p.title, p.filename
                FROM chunks c
                JOIN papers p ON c.paper_id = p.id
                WHERE c.embedding IS NOT NULL
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
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
            
        except Exception as e:
            print(f"搜索论文失败: {e}")
            return []
    
    def get_rag_response_for_patient(self, patient_data, user_question=None):
        """为患者生成基于RAG的回答"""
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
        
        # 过滤高相似度的论文（0.8以上）并构建上下文（去重）
        context_texts = []
        paper_references = []
        seen_titles = set()
        high_quality_papers = []
        
        for paper in relevant_papers:
            if paper['similarity'] >= 0.8 and paper['title'] not in seen_titles:
                context_texts.append(f"从论文《{paper['title']}》(相似度: {paper['similarity']:.3f}): {paper['chunk_text'][:800]}...")
                paper_references.append(paper['title'])
                seen_titles.add(paper['title'])
                high_quality_papers.append(paper)
        
        context = "\n\n".join(context_texts)
        
        # 生成回答
        prompt = f"""基于以下医学文献内容，回答关于患者的问题。

患者症状关键词: {', '.join(symptoms)}
诊断依据: {'; '.join(diagnostic_info)}
用户问题: {user_question if user_question else '请提供相关医学信息'}

相关文献内容:
{context}

请基于上述文献内容，提供全面详细的医学分析和建议。请务必：
1. 综合所有提供的高相似度文献内容（相似度≥0.8）
2. 详细分析每篇相关论文的核心发现
3. 将文献结论与患者的具体症状和诊断依据关联
4. 提供循证医学建议和治疗指导
5. 不要限制回答长度，请提供完整详尽的分析

如果文献内容不足以回答问题，请说明需要更多信息。"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个医学助手，基于提供的文献内容回答问题。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # 添加参考文献
            if paper_references:
                ai_response += f"\n\n📚 参考文献:\n" + "\n".join([f"• {ref}" for ref in paper_references])
            
            return ai_response, relevant_papers, diagnostic_info
            
        except Exception as e:
            print(f"生成RAG回答失败: {e}")
            return None, relevant_papers, diagnostic_info

# 全局RAG系统实例
rag_system = RAGSystem()