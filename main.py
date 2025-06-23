import sys
from pynput import keyboard

# 用一個列表來儲存當前正在輸入的單字
current_word = []

# 建立一個鍵盤控制器，用來模擬按鍵操作
keyboard_controller = keyboard.Controller()

def on_press(key):
    """
    這個函數會在每次按鍵時被呼叫
    """
    global current_word

    # 將主要邏輯放在 try...except 區塊中，以處理各種可能的錯誤
    try:
        # 1. 處理空格鍵（觸發替換）
        if key == keyboard.Key.space:
            if current_word:
                # 組合成單字前，先確認列表內沒有 None
                word_to_replace = "".join(filter(None, current_word))
                print(f"偵測到單字 '{word_to_replace}' 後按下空格。")

                # 刪除的長度 = 單字長度 + 剛剛按下的空格
                delete_length = len(word_to_replace) + 1

                for _ in range(delete_length):
                    keyboard_controller.press(keyboard.Key.backspace)
                    keyboard_controller.release(keyboard.Key.backspace)

                keyboard_controller.type('Hi ')
                current_word = []
        
        # 2. 處理退格鍵
        elif key == keyboard.Key.backspace:
            if current_word:
                current_word.pop()
        
        # 3. 處理其他所有按鍵
        else:
            # 【關鍵修正】
            # 只有當 key.char 存在且不為 None 時，才將其視為字元加入列表
            if hasattr(key, 'char') and key.char is not None:
                current_word.append(key.char)
            else:
                # 對於其他所有特殊鍵 (Enter, Tab, CapsLock 等)
                # 將其視為單字分隔，清空緩衝區
                # 這樣就不會把 None 加入列表了
                if current_word:
                    print(f"偵測到特殊鍵 {key}，重置單字緩衝區。")
                    current_word = []

    except Exception as e:
        # 捕捉所有未預期的錯誤，並印出，方便除錯
        print(f"發生未知錯誤: {e}")
        # 發生錯誤時清空緩衝區，以避免連續出錯
        current_word = []


def on_release(key):
    """
    按下 Esc 鍵即可停止程式
    """
    if key == keyboard.Key.esc:
        print("\n偵測到 Esc 鍵，程式即將結束...")
        return False # 返回 False 會停止監聽器

# --- 主程式 ---
print("鍵盤監聽程式已啟動...")
print("在任何地方輸入一個英文單字後按下空格，該單字將被替換為 'Hi'。")
print("按下 'Esc' 鍵即可退出程式。")

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

print("程式已結束。")