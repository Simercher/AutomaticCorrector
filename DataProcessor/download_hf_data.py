from datasets import load_dataset
import os
import opencc # <--- 匯入 opencc

# --- 設定 ---
EN_DATASET_NAME = "bookcorpus"
EN_DATASET_SPLIT = "train"
EN_TEXT_COLUMN = "text"
EN_OUTPUT_FILE = "corpus_en_raw.txt"

ZH_DATASET_NAME = "wikimedia/wikipedia"
ZH_DATASET_CONFIG = "20231101.zh" 
ZH_DATASET_SPLIT = "train"
ZH_TEXT_COLUMN = "text"
ZH_OUTPUT_FILE = "corpus_zh_raw.txt"

NUM_SAMPLES_TO_DOWNLOAD = 50000

# --- 初始化 OpenCC ---
# 建立一個從簡體到台灣正體（包含詞彙轉換）的轉換器
# s2twp.json 的意思是: Simplified to Traditional, Taiwan standard, with Phrases.
# 這正是我們需要的，它不只轉字元，還會轉換詞彙！
cc = opencc.OpenCC('s2twp')  

def download_and_save(dataset_name, config_name, split, text_column, output_file, num_samples=None, is_chinese=False):
    """從 Hugging Face 下載數據集，進行繁簡轉換（如果需要），並儲存為純文字檔"""
    print(f"--- 開始處理數據集: {dataset_name} (設定: {config_name}) ---")
    
    try:
        dataset = load_dataset(dataset_name, name=config_name, split=split, streaming=True)
    except Exception as e:
        print(f"載入數據集時發生錯誤: {e}")
        return

    count = 0
    with open(output_file, "w", encoding="utf-8") as f:
        for example in iter(dataset):
            if num_samples is not None and count >= num_samples:
                print(f"已達到下載上限 {num_samples} 筆，停止處理。")
                break
            
            text = example.get(text_column, "")
            
            # 如果是中文數據集，就進行繁簡轉換
            if is_chinese:
                text = cc.convert(text) # <--- 核心轉換步驟
            
            clean_text = " ".join(text.strip().split())
            
            if clean_text:
                f.write(clean_text + '\n')
            
            count += 1
            if count % 10000 == 0:
                print(f"已處理 {count} 筆記錄...")
                
    print(f"處理完成！總共 {count} 筆記錄已儲存至 {output_file}\n")

if __name__ == "__main__":
    # 下載並儲存英文數據集
    download_and_save(EN_DATASET_NAME, None, EN_DATASET_SPLIT, EN_TEXT_COLUMN, EN_OUTPUT_FILE, NUM_SAMPLES_TO_DOWNLOAD, is_chinese=False)
    
    # 下載並儲存中文數據集，並標記需要進行繁簡轉換
    download_and_save(ZH_DATASET_NAME, ZH_DATASET_CONFIG, ZH_DATASET_SPLIT, ZH_TEXT_COLUMN, ZH_OUTPUT_FILE, NUM_SAMPLES_TO_DOWNLOAD, is_chinese=True)

    # --- 範例展示 OpenCC 的強大之處 ---
    print("\n--- OpenCC 轉換範例 ---")
    simplified_text = "U盘里存着很多软件和视频，服务器的性能和内存很重要。"
    traditional_text = cc.convert(simplified_text)
    print(f"簡體原文: {simplified_text}")
    print(f"繁體轉換後: {traditional_text}")