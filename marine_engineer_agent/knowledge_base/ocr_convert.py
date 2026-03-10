#!/usr/bin/env python3
import os
import sys
from pdf2image import convert_from_path
import pytesseract

# 配置路径
knowledge_base = "/Users/panglaohu/clawd/agents/marine_engineer/knowledge_base"
output_dir = os.path.join(knowledge_base, "text")

# PDF文件列表
pdfs = [
    ("Basic Ship Theory V2.pdf", 373),
    ("Basic_Ship_Theory.pdf", 400),
    ("Introduction_to_Marine_Engineering.pdf", 383)
]

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

def ocr_pdf(pdf_name, total_pages):
    pdf_path = os.path.join(knowledge_base, pdf_name)
    txt_name = pdf_name.replace(".pdf", ".txt")
    txt_path = os.path.join(output_dir, txt_name)
    
    sys.stdout.flush()
    print(f"[START] Processing: {pdf_name} ({total_pages} pages)", flush=True)
    sys.stdout.flush()
    
    all_text = []
    batch_size = 10
    
    for batch_start in range(1, total_pages + 1, batch_size):
        batch_end = min(batch_start + batch_size - 1, total_pages)
        
        print(f"[BATCH] Pages {batch_start}-{batch_end}", flush=True)
        sys.stdout.flush()
        
        try:
            # 转换当前批次页面为图片
            images = convert_from_path(pdf_path, first_page=batch_start, last_page=batch_end, dpi=200)
            
            # OCR识别每张图片
            for i, image in enumerate(images):
                page_num = batch_start + i
                text = pytesseract.image_to_string(image, lang='eng')
                all_text.append(f"--- Page {page_num} ---\n{text}\n---PAGE BREAK---\n")
            
            print(f"[OK] Batch {batch_start}-{batch_end} done", flush=True)
            sys.stdout.flush()
            
        except Exception as e:
            print(f"[ERROR] Batch {batch_start}-{batch_end}: {e}", flush=True)
            sys.stdout.flush()
    
    # 保存到txt文件
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_text))
    
    file_size = os.path.getsize(txt_path)
    print(f"[DONE] {txt_path} ({file_size/1024/1024:.1f} MB)", flush=True)
    sys.stdout.flush()
    return txt_path

# 执行转换
for pdf_name, total_pages in pdfs:
    try:
        result_path = ocr_pdf(pdf_name, total_pages)
    except Exception as e:
        print(f"[FATAL] {pdf_name}: {e}", flush=True)
        sys.stdout.flush()

print("[ALL DONE]", flush=True)
sys.stdout.flush()
