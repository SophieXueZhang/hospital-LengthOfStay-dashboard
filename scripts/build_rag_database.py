#!/usr/bin/env python3
"""
构建RAG数据库：提取PDF和TXT文本，生成embeddings，存储到SQLite数据库
"""

import os
import sqlite3
import json
import openai
import numpy as np
from pathlib import Path
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import time

# 加载环境变量
load_dotenv()

def extract_pdf_text(pdf_path):
    """从PDF文件中提取文本"""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"提取PDF文本失败 {pdf_path}: {e}")
        return ""

def extract_txt_text(txt_path):
    """从TXT文件中提取文本"""
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"提取TXT文本失败 {txt_path}: {e}")
        return ""

def chunk_text(text, chunk_size=1000, overlap=200):
    """将文本分块处理"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # 尝试在句号处分割，避免截断句子
        if end < len(text):
            last_period = chunk.rfind('.')
            if last_period > chunk_size // 2:
                end = start + last_period + 1
                chunk = text[start:end]
        
        chunks.append(chunk.strip())
        start = end - overlap
        
        if start >= len(text):
            break
    
    return chunks

def get_embedding(text, client):
    """获取文本的embedding"""
    try:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"获取embedding失败: {e}")
        return None

def create_database():
    """创建SQLite数据库"""
    conn = sqlite3.connect('/Users/pc/Documents/cursor/ml_course/project/data/papers_rag.db')
    cursor = conn.cursor()
    
    # 创建表格
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            title TEXT,
            full_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_id INTEGER,
            chunk_text TEXT NOT NULL,
            chunk_index INTEGER,
            embedding TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (paper_id) REFERENCES papers (id)
        )
    ''')
    
    conn.commit()
    return conn

def extract_title_from_filename(filename):
    """从文件名中提取标题"""
    # 去掉扩展名
    title = filename.replace('.pdf', '').replace('.txt', '')
    # 替换连字符和下划线为空格
    title = title.replace('-', ' ').replace('_', ' ')
    # 首字母大写
    return title.title()

def build_rag_database():
    """构建RAG数据库"""
    print("开始构建RAG数据库...")
    
    # 初始化OpenAI客户端
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # 创建数据库
    conn = create_database()
    cursor = conn.cursor()
    
    # 清空现有数据
    cursor.execute('DELETE FROM chunks')
    cursor.execute('DELETE FROM papers')
    conn.commit()
    
    papers_dir = Path('/Users/pc/Documents/cursor/ml_course/project/data/papers')
    
    for file_path in papers_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.txt']:
            print(f"\n处理文件: {file_path.name}")
            
            # 提取文本
            if file_path.suffix.lower() == '.pdf':
                full_text = extract_pdf_text(file_path)
            else:
                full_text = extract_txt_text(file_path)
            
            if not full_text:
                print(f"跳过空文件: {file_path.name}")
                continue
            
            # 生成标题
            title = extract_title_from_filename(file_path.name)
            
            # 插入论文记录
            cursor.execute('''
                INSERT INTO papers (filename, title, full_text)
                VALUES (?, ?, ?)
            ''', (file_path.name, title, full_text))
            
            paper_id = cursor.lastrowid
            
            # 分块处理文本
            chunks = chunk_text(full_text)
            print(f"  生成 {len(chunks)} 个文本块")
            
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) < 50:  # 跳过太短的块
                    continue
                
                print(f"  处理第 {i+1}/{len(chunks)} 块...", end=' ')
                
                # 获取embedding
                embedding = get_embedding(chunk, client)
                if embedding:
                    embedding_json = json.dumps(embedding)
                    
                    # 插入chunk记录
                    cursor.execute('''
                        INSERT INTO chunks (paper_id, chunk_text, chunk_index, embedding)
                        VALUES (?, ?, ?, ?)
                    ''', (paper_id, chunk, i, embedding_json))
                    
                    print("✅")
                else:
                    print("❌")
                
                # 避免API限制
                time.sleep(0.1)
            
            conn.commit()
            print(f"  完成处理: {file_path.name}")
    
    # 统计信息
    cursor.execute('SELECT COUNT(*) FROM papers')
    paper_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM chunks')
    chunk_count = cursor.fetchone()[0]
    
    print(f"\n数据库构建完成!")
    print(f"总共处理: {paper_count} 篇论文")
    print(f"生成文本块: {chunk_count} 个")
    
    conn.close()

if __name__ == "__main__":
    build_rag_database()