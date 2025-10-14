#!/usr/bin/env python3
"""
测试RAG系统功能
"""

import os
from rag_system import rag_system

def test_rag_system():
    """测试RAG系统的基本功能"""
    print("测试RAG系统...")
    
    # 模拟一个有贫血症状的患者
    test_patient = {
        'eid': 'TEST001',
        'full_name': 'John Doe',
        'hematocrit': 25.0,  # 低血细胞比容值，表示贫血
        'diagnosis': 'anemia',
        'readmission': 'No'
    }
    
    # 测试1: 基本症状检测
    print("\n1. 测试症状检测:")
    symptoms = rag_system.extract_symptoms_from_patient(test_patient)
    print(f"检测到症状: {symptoms}")
    
    # 测试2: 搜索相关论文
    print("\n2. 测试论文搜索:")
    search_query = "anemia hospital length of stay"
    papers = rag_system.search_relevant_papers(search_query, top_k=2)
    print(f"找到 {len(papers)} 篇相关论文:")
    for i, paper in enumerate(papers, 1):
        print(f"  {i}. {paper['title']} (相似度: {paper['similarity']:.3f})")
    
    # 测试3: 生成RAG回答
    print("\n3. 测试RAG回答生成:")
    user_question = "这个患者的贫血会如何影响住院时间？"
    rag_response, relevant_papers = rag_system.get_rag_response_for_patient(test_patient, user_question)
    
    if rag_response:
        print("RAG回答:")
        print(rag_response)
    else:
        print("无法生成RAG回答 - 可能数据库还未准备好")
    
    print(f"\n相关论文数量: {len(relevant_papers)}")

if __name__ == "__main__":
    test_rag_system()