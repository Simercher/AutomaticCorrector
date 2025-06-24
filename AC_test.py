import re
import os
import pickle
from collections import Counter
from symspellpy import SymSpell, Verbosity
from pycorrector import Corrector
from opencc import OpenCC

# --- 模型檔案名稱定義 ---
SYMPELL_MODEL_PATH = "symspell_unified.pkl"

# --- Helper 函式 (來自之前的版本) ---
def restore_case(original_word, corrected_word):
    if original_word.islower(): return corrected_word.lower()
    if original_word.isupper(): return corrected_word.upper()
    if original_word.istitle(): return corrected_word.title()
    return corrected_word

def create_or_load_symspell_model(corpus_path, model_path):
    if os.path.exists(model_path):
        print(f"載入已儲存的 SymSpell 模型 from '{model_path}'...")
        with open(model_path, 'rb') as f:
            return pickle.load(f)
    
    print("建立新的統一 SymSpell 模型...")
    sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
    if not os.path.exists(corpus_path):
        raise FileNotFoundError(f"語料庫檔案 '{corpus_path}' 不存在，無法建立新的 SymSpell 模型。")
    
    print("從語料庫載入詞彙...")
    word_frequency = Counter(re.findall(r'[a-zA-Z]+', open(corpus_path, "r", encoding="utf-8").read().lower()))
    for word, count in word_frequency.items():
        sym_spell.create_dictionary_entry(word, count)
        
    print(f"建立完成，正在儲存 SymSpell 模型至 '{model_path}'...")
    with open(model_path, 'wb') as f:
        pickle.dump(sym_spell, f)
    return sym_spell

# --- ★★★ 新增的核心函式 ★★★ ---

def split_text_by_language(text):
    """
    將文本分割成中文和英文片段的列表。
    返回: [('片段1', 'zh'), ('片段2', 'en'), ...]
    """
    # 使用正規表示式找到所有英文/數字/空格的連續區塊
    segments = []
    # 找到所有英文區塊的位置
    english_blocks = [(m.start(), m.end()) for m in re.finditer(r'[a-zA-Z0-9\s]+', text)]
    
    last_idx = 0
    for start, end in english_blocks:
        # 添加英文區塊之前的中文區塊
        if start > last_idx:
            segments.append((text[last_idx:start], 'zh'))
        # 添加英文區塊
        segments.append((text[start:end], 'en'))
        last_idx = end
        
    # 添加最後剩餘的中文區塊
    if last_idx < len(text):
        segments.append((text[last_idx:], 'zh'))
        
    return segments

def correct_english_segment(segment, sym_spell):
    """
    對一個純英文片段進行拼寫校正。
    """
    words = segment.split(' ')
    corrected_words = []
    for word in words:
        if not word or not re.search(r'[a-zA-Z]', word):
            corrected_words.append(word)
            continue

        suggestions = sym_spell.lookup(word.lower(), Verbosity.TOP, max_edit_distance=2)
        if suggestions:
            suggestion = suggestions[0]
            # 簡單選擇編輯距離最近的建議詞
            corrected_word = restore_case(word, suggestion.term)
            print(f"  - (英文處理) 將 '{word}' 修正為 '{corrected_word}'")
            corrected_words.append(corrected_word)
        else:
            corrected_words.append(word)
    return ' '.join(corrected_words)

# --- 主程式 ---

def main():
    # --- 1. 載入所有模型與工具 ---
    print("--- 開始載入模型 ---")
    
    # ... create_or_load_symspell_model 的部分保持不變 ...
    corpus_path = "DataProcessor/corpus_final_for_kenlm.txt"
    sym_spell = create_or_load_symspell_model(corpus_path, SYMPELL_MODEL_PATH)
    
    # --- ★★★ 這是本次實驗的核心修改 ★★★ ---
    # ★★★ 暫時移除 language_model_path，只用混淆集來測試 ★★★
    my_confusion_path = 'my_confusion.txt'
    if not os.path.exists(my_confusion_path):
        raise FileNotFoundError(f"找不到混淆集檔案: '{my_confusion_path}'")

    print(f"【實驗模式】正在載入 Corrector，但暫不使用您的 KenLM 模型...")
    # 注意：這裡的初始化完全沒有 language_model_path 參數
    py_corrector = Corrector(custom_confusion_path_or_dict=my_confusion_path)
    print("Corrector 初始化完成！\n")
    # --- ★★★★★★★★★★★★★★★★★★★★★★★★★

    # --- 2. 執行糾錯流程 (後續程式碼完全不變) ---
    original_sentence = "今舔天氣好好，我想吃一個 Aple。"
    print(f"原始句子 (繁體): '{original_sentence}'\n")

    segments = split_text_by_language(original_sentence)
    print(f"分割後的片段: {segments}\n")

    print("--- 開始對各片段進行修正 ---")
    corrected_segments = []
    for text, lang_type in segments:
        if not text.strip():
            corrected_segments.append(text)
            continue
            
        if lang_type == 'zh':
            result = py_corrector.correct(text)
            corrected_text = result['target']
            if text != corrected_text:
                print(f"  - (中文處理) 將 '{text.strip()}' 修正為 '{corrected_text.strip()}'")
            corrected_segments.append(corrected_text)
        else: # lang_type == 'en'
            corrected_text = correct_english_segment(text, sym_spell)
            corrected_segments.append(corrected_text)
    print("--- 片段修正完成 ---\n")
    
    final_sentence = "".join(corrected_segments)
    print(f"組合後的結果 (繁體): '{final_sentence}'\n")
    
    print("--- 最終結果 ---")
    print(f"修正後的句子 (繁體): '{final_sentence}'")

if __name__ == "__main__":
    # 這裡不再需要設定 jieba 詞典，因為 pycorrector 內部會處理
    main()