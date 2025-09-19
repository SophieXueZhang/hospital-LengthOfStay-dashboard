#!/usr/bin/env python3
"""
增强版论文提取：优化标题、作者、年份提取算法
"""

import os
import sqlite3
import json
import openai
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
import time
import re
from datetime import datetime

# PDF处理相关
import fitz  # PyMuPDF

# 加载环境变量
load_dotenv()

class EnhancedPaperExtractor:
    def __init__(self, papers_dir="data/papers", db_path="data/papers_rag.db"):
        self.papers_dir = Path(papers_dir)
        self.db_path = db_path
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.init_database()

    def init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 删除旧表重新创建
        cursor.execute("DROP TABLE IF EXISTS paper_chunks")

        cursor.execute('''
        CREATE TABLE paper_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            title TEXT,
            authors TEXT,
            year INTEGER,
            content TEXT NOT NULL,
            chunk_text TEXT NOT NULL,
            chunk_index INTEGER,
            embedding TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        conn.commit()
        conn.close()
        print("数据库初始化完成")

    def extract_txt_content(self, txt_path):
        """提取TXT文件内容"""
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            # 使用增强算法提取元数据
            title = self.extract_title_enhanced(content, txt_path.stem)
            authors = self.extract_authors_enhanced(content)
            year = self.extract_year_enhanced(content)

            return {
                'title': title,
                'authors': authors,
                'year': year,
                'content': content
            }
        except Exception as e:
            print(f"❌ 提取TXT失败 {txt_path}: {e}")
            return None

    def extract_pdf_content(self, pdf_path):
        """提取PDF内容"""
        try:
            doc = fitz.open(pdf_path)
            content = ""

            # 提取文本
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                if page_text.strip():
                    content += f"\n=== 第{page_num+1}页 ===\n{page_text}\n"

            doc.close()

            if len(content.strip()) > 100:
                print(f"  ✅ 原生文本提取成功，内容长度: {len(content)}")

                # 使用增强算法提取元数据
                title = self.extract_title_enhanced(content, pdf_path.stem)
                authors = self.extract_authors_enhanced(content)
                year = self.extract_year_enhanced(content)

                return {
                    'title': title,
                    'authors': authors,
                    'year': year,
                    'content': content
                }
            else:
                print(f"  ❌ 原生提取文本不足，跳过此文件")
                return None

        except Exception as e:
            print(f"❌ PDF处理失败 {pdf_path}: {e}")
            return None

    def extract_title_enhanced(self, content, fallback_title):
        """增强版标题提取算法"""
        lines = [line.strip() for line in content.split('\n') if line.strip()]

        # 策略1: 查找明确的标题标记
        title_patterns = [
            r'(?i)^title[:\s]+(.+)',
            r'(?i)^article title[:\s]+(.+)',
            r'(?i)^paper title[:\s]+(.+)'
        ]

        for line in lines[:20]:
            for pattern in title_patterns:
                match = re.search(pattern, line)
                if match:
                    title = match.group(1).strip()
                    if 10 <= len(title) <= 200:
                        return title

        # 策略2: 查找第一页的主要标题（通常是最大的文本块）
        first_page_lines = []
        capturing = False

        for line in lines:
            if '=== 第1页 ===' in line:
                capturing = True
                continue
            elif '=== 第2页 ===' in line:
                break
            elif capturing:
                first_page_lines.append(line)

        # 在第一页中查找潜在标题
        for line in first_page_lines[:15]:
            # 跳过常见的非标题行
            if re.match(r'^(abstract|introduction|keywords|references|page \d+|vol\.|vol |journal|doi:|pmid:)', line, re.IGNORECASE):
                continue
            if re.match(r'^[A-Z\s]{5,}$', line):  # 全大写可能是标题
                continue
            if re.match(r'^\d+[\.\s]', line):  # 数字开头可能是编号
                continue

            # 可能的标题特征
            if (20 <= len(line) <= 200 and
                line.count(' ') >= 3 and  # 至少4个单词
                not line.startswith('=') and
                ':' not in line[:20]):  # 标题通常不在开头有冒号
                return line

        # 策略3: 从文件名优化标题
        enhanced_title = self.enhance_title_from_filename(fallback_title)
        return enhanced_title

    def enhance_title_from_filename(self, filename):
        """从文件名优化标题"""
        # 移除常见的文件标识符
        title = filename.replace('-', ' ').replace('_', ' ')

        # 首字母大写
        words = title.split()
        enhanced_words = []

        for word in words:
            if word.lower() in ['of', 'and', 'in', 'on', 'with', 'for', 'to', 'a', 'an', 'the']:
                enhanced_words.append(word.lower())
            else:
                enhanced_words.append(word.capitalize())

        return ' '.join(enhanced_words)

    def extract_authors_enhanced(self, content):
        """增强版作者提取算法"""
        lines = [line.strip() for line in content.split('\n') if line.strip()]

        # 策略1: 查找明确的作者标记
        author_patterns = [
            r'(?i)^authors?[:\s]+(.+)',
            r'(?i)^by[:\s]+(.+)',
            r'(?i)^written by[:\s]+(.+)',
            r'(?i)^correspondent?[:\s]+(.+)'
        ]

        for line in lines[:30]:
            for pattern in author_patterns:
                match = re.search(pattern, line)
                if match:
                    authors = match.group(1).strip()
                    if len(authors) < 150:  # 避免提取过长的文本
                        return self.clean_authors(authors)

        # 策略2: 查找典型的作者姓名模式
        first_page_lines = []
        capturing = False

        for line in lines:
            if '=== 第1页 ===' in line:
                capturing = True
                continue
            elif '=== 第2页 ===' in line:
                break
            elif capturing:
                first_page_lines.append(line)

        # 在前几行查找作者模式
        author_name_patterns = [
            r'([A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+)',  # John A. Smith
            r'([A-Z][a-z]+ [A-Z][a-z]+)',          # John Smith
            r'([A-Z]\. [A-Z][a-z]+)',              # J. Smith
            r'([A-Z][a-z]+, [A-Z]\.[A-Z]\.)',      # Smith, J.A.
        ]

        found_authors = []
        for line in first_page_lines[:10]:
            # 跳过明显不是作者行的内容
            if re.match(r'^(abstract|introduction|keywords|background)', line, re.IGNORECASE):
                break

            for pattern in author_name_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    if len(match) >= 4 and match not in found_authors:
                        found_authors.append(match)

        if found_authors:
            if len(found_authors) == 1:
                return found_authors[0]
            else:
                return found_authors[0] + " et al."

        # 策略3: 查找"et al."模式
        for line in first_page_lines[:15]:
            if 'et al' in line.lower():
                # 尝试提取主作者
                words = line.split()
                for i, word in enumerate(words):
                    if 'et' in word.lower() and i > 0:
                        potential_author = words[i-1]
                        if len(potential_author) >= 3:
                            return potential_author + " et al."

        return "Unknown"

    def clean_authors(self, authors_text):
        """清理作者文本"""
        # 移除常见的无关信息
        authors = authors_text.replace('\n', ' ').strip()

        # 移除邮箱
        authors = re.sub(r'\S+@\S+', '', authors)

        # 移除机构信息（通常在括号或逗号后）
        authors = re.sub(r'\([^)]+\)', '', authors)

        # 限制长度
        if len(authors) > 100:
            # 如果太长，只保留第一个作者 + et al.
            first_author = authors.split(',')[0].split(' and ')[0].strip()
            authors = first_author + " et al."

        return authors.strip()

    def extract_year_enhanced(self, content):
        """增强版年份提取算法"""
        lines = [line.strip() for line in content.split('\n') if line.strip()]

        # 策略1: 查找明确的年份标记
        year_patterns = [
            r'(?i)year[:\s]+(\d{4})',
            r'(?i)published[:\s]+(\d{4})',
            r'(?i)copyright[:\s]+(\d{4})',
            r'(?i)\((\d{4})\)',
        ]

        for line in lines[:50]:
            for pattern in year_patterns:
                match = re.search(pattern, line)
                if match:
                    year = int(match.group(1))
                    if 1980 <= year <= 2030:
                        return year

        # 策略2: 在标题附近查找年份
        first_page_lines = []
        capturing = False

        for line in lines:
            if '=== 第1页 ===' in line:
                capturing = True
                continue
            elif '=== 第2页 ===' in line:
                break
            elif capturing:
                first_page_lines.append(line)

        # 查找年份模式
        year_candidates = []
        for line in first_page_lines[:20]:
            # 查找4位数年份
            years = re.findall(r'\b(19[8-9]\d|20[0-3]\d)\b', line)
            for year_str in years:
                year = int(year_str)
                if 1980 <= year <= 2030:
                    year_candidates.append(year)

        if year_candidates:
            # 返回最常见的年份，或者最新的年份
            return max(year_candidates)

        # 策略3: 从期刊信息中提取
        for line in first_page_lines:
            # 查找期刊格式中的年份
            journal_patterns = [
                r'(\d{4});',
                r'(\d{4})\s*[;:]',
                r'Vol\.\s*\d+.*?(\d{4})',
                r'Volume\s*\d+.*?(\d{4})'
            ]

            for pattern in journal_patterns:
                match = re.search(pattern, line)
                if match:
                    year = int(match.group(1))
                    if 1980 <= year <= 2030:
                        return year

        return None

    def split_into_chunks(self, content, chunk_size=1000, overlap=200):
        """将内容分割成块"""
        if not content or len(content) < chunk_size:
            return [content] if content else []

        chunks = []
        start = 0

        while start < len(content):
            end = start + chunk_size

            if end < len(content):
                period_pos = content.rfind('.', start, end)
                if period_pos > start + chunk_size // 2:
                    end = period_pos + 1

            chunk = content[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap

        return chunks

    def get_embedding(self, text):
        """获取文本的embedding向量"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text[:8000]
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"  ⚠️ 获取embedding失败: {e}")
            return None

    def save_to_database(self, paper_data, chunks):
        """保存论文数据到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            for i, chunk in enumerate(chunks):
                embedding = self.get_embedding(chunk)
                embedding_json = json.dumps(embedding) if embedding else None

                cursor.execute('''
                INSERT INTO paper_chunks
                (filename, title, authors, year, content, chunk_text, chunk_index, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    paper_data['filename'],
                    paper_data['title'],
                    paper_data['authors'],
                    paper_data['year'],
                    paper_data['content'],
                    chunk,
                    i,
                    embedding_json
                ))

                time.sleep(0.1)

            conn.commit()
            print(f"  ✅ 保存成功: {len(chunks)} 个文本块")

        except Exception as e:
            print(f"  ❌ 保存失败: {e}")
            conn.rollback()
        finally:
            conn.close()

    def process_all_papers(self):
        """处理所有论文文件"""
        if not self.papers_dir.exists():
            print(f"❌ 论文目录不存在: {self.papers_dir}")
            return

        txt_files = list(self.papers_dir.glob("*.txt"))
        pdf_files = list(self.papers_dir.glob("*.pdf"))

        print(f"发现 {len(txt_files)} 个TXT文件，{len(pdf_files)} 个PDF文件")

        total_processed = 0

        # 处理TXT文件
        print("\n=== 处理TXT文件 ===")
        for txt_file in txt_files:
            print(f"\n📄 处理: {txt_file.name}")

            paper_data = self.extract_txt_content(txt_file)
            if paper_data:
                paper_data['filename'] = txt_file.name
                chunks = self.split_into_chunks(paper_data['content'])
                self.save_to_database(paper_data, chunks)
                total_processed += 1
                print(f"  标题: {paper_data['title']}")
                print(f"  作者: {paper_data['authors']}")
                print(f"  年份: {paper_data['year']}")

        # 处理PDF文件
        print("\n=== 处理PDF文件 ===")
        for pdf_file in pdf_files:
            print(f"\n📄 处理: {pdf_file.name}")

            paper_data = self.extract_pdf_content(pdf_file)
            if paper_data:
                paper_data['filename'] = pdf_file.name
                chunks = self.split_into_chunks(paper_data['content'])
                self.save_to_database(paper_data, chunks)
                total_processed += 1
                print(f"  标题: {paper_data['title']}")
                print(f"  作者: {paper_data['authors']}")
                print(f"  年份: {paper_data['year']}")

        print(f"\n🎉 提取完成！总共处理了 {total_processed} 篇论文")

def main():
    print("开始增强版论文元数据提取...")

    extractor = EnhancedPaperExtractor()
    extractor.process_all_papers()

    # 验证结果
    conn = sqlite3.connect("data/papers_rag.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(DISTINCT filename) FROM paper_chunks")
    count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM paper_chunks")
    total_chunks = cursor.fetchone()[0]

    # 统计元数据质量
    cursor.execute("SELECT COUNT(*) FROM paper_chunks WHERE authors != 'Unknown' AND authors IS NOT NULL")
    has_authors = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM paper_chunks WHERE year IS NOT NULL")
    has_years = cursor.fetchone()[0]

    conn.close()

    print(f"\n📊 数据库统计:")
    print(f"   论文数量: {count}")
    print(f"   文本块数量: {total_chunks}")
    print(f"   有作者信息: {has_authors}")
    print(f"   有年份信息: {has_years}")

if __name__ == "__main__":
    main()