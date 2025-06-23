from pynput import keyboard

def on_press(key):
    try:
        print(f'你按下了: {key.char}')
    except AttributeError:
        print(f'你按下了特殊鍵: {key}')

def on_release(key):
    if key == keyboard.Key.esc:
        print('結束監聽')
        return False  # 停止監聽
    else:
        print(f'你放開了: {key}')

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

# 不會阻止其他程式使用鍵盤，這只是個監聽器
listener.join()

