#!/usr/bin/env python3
"""
OCR 转换脚本 - The Design and Construction of Ships.pdf

将 PDF 转换为文本，提取船舶设计与建造知识。
"""

import os
import sys
from pdf2image import convert_from_path
import pytesseract

# 配置
PDF_PATH = "/Users/panglaohu/Downloads/LocalKB/ship/The Design and Construction of Ships.pdf"
OUTPUT_PATH = "/Users/panglaohu/Downloads/DoubleBoatSimWebGL/marine_engineer_agent/knowledge_base/text/The_Design_and_Construction_of_Ships.txt"
SUMMARY_PATH = "/Users/panglaohu/Downloads/DoubleBoatSimWebGL/marine_engineer_agent/knowledge_base/the_design_and_construction_of_ships_summary.md"

# 确保输出目录存在
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

print(f"📖 开始处理：{PDF_PATH}")
print(f"📁 输出：{OUTPUT_PATH}")
print()

# 检查文件
if not os.path.exists(PDF_PATH):
    print(f"❌ 文件不存在：{PDF_PATH}")
    sys.exit(1)

file_size = os.path.getsize(PDF_PATH)
print(f"📊 文件大小：{file_size / 1024 / 1024:.1f} MB")

# 尝试获取页数
try:
    from PyPDF2 import PdfReader
    reader = PdfReader(PDF_PATH)
    total_pages = len(reader.pages)
    print(f"📄 总页数：{total_pages}")
except:
    total_pages = 300  # 估计值
    print(f"⚠️  无法获取页数，使用估计值：{total_pages}")

print()
print("开始 OCR 处理...")
print()

# 转换 PDF 为图片并 OCR
all_text = []
batch_size = 5  # 小批量处理
error_pages = []

# 先处理前 50 页
for batch_start in range(1, min(total_pages + 1, 51), batch_size):
    batch_end = min(batch_start + batch_size - 1, min(total_pages, 51))
    
    print(f"[{batch_start:3d}-{batch_end:3d}] ", end="", flush=True)
    
    try:
        images = convert_from_path(PDF_PATH, first_page=batch_start, last_page=batch_end, dpi=150)
        
        for i, image in enumerate(images):
            page_num = batch_start + i
            text = pytesseract.image_to_string(image, lang='eng')
            all_text.append(f"--- Page {page_num} ---\n{text}\n")
        
        print("✅")
        
    except Exception as e:
        print(f"❌ {e}")
        error_pages.append(f"{batch_start}-{batch_end}")

# 保存文本
print()
print("保存文本...")
with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(all_text))

output_size = os.path.getsize(OUTPUT_PATH)
print(f"✅ 已保存：{OUTPUT_PATH} ({output_size / 1024 / 1024:.1f} MB)")
print(f"📊 处理页数：{len(all_text)}")
if error_pages:
    print(f"⚠️  错误页码：{', '.join(error_pages)}")

print()
print("OCR 完成！开始分析内容...")

# 简单分析
print()
print("📊 内容分析：")
full_text = '\n'.join(all_text)
keywords = ['ship', 'hull', 'design', 'construction', 'structure', 'deck', 'bulkhead', 'frame', 'welding', 'steel']
for kw in keywords:
    count = full_text.lower().count(kw.lower())
    if count > 0:
        print(f"  - '{kw}': {count} 次")

print()
print("✅ 第一阶段的 OCR 完成！")
