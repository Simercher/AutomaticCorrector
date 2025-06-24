import jieba

# --- 設定 ---
# 上一步產生的檔案列表
SOURCE_FILES = ['corpus_en_raw.txt', 'corpus_zh_raw.txt']
# 最終要給 KenLM 訓練用的檔案
FINAL_OUTPUT_FILE = 'corpus_final_for_kenlm.txt'

# 載入 jieba 的繁體大字典
jieba.set_dictionary('dict.txt.big')

print("--- 開始進行分詞與合併 ---")
line_count = 0
with open(FINAL_OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
    for source_file in SOURCE_FILES:
        print(f"正在處理檔案: {source_file}...")
        with open(source_file, 'r', encoding='utf-8') as infile:
            for line in infile:
                # jieba 能很好地處理中英混合，會將英文單字正確地切分
                words = jieba.cut(line.strip(), cut_all=False)
                segmented_line = " ".join(words)
                
                outfile.write(segmented_line + '\n')
                line_count += 1
                if line_count % 100000 == 0:
                    print(f"已處理 {line_count} 行...")

print(f"所有處理完成！共 {line_count} 行已寫入至 {FINAL_OUTPUT_FILE}")