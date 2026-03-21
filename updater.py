import os
import sys
import base64
import traceback
import urllib.request
import json
import subprocess
import time

# Решение проблемы "OpenBLAS error"
os.environ['OPENBLAS_NUM_THREADS'] = '1'

# ================= 1. ЭКСТРЕННАЯ СВЯЗЬ (БЕЗ ВНЕШНИХ БИБЛИОТЕК) =================
_T_B64 = b'Nzk5NjAyMjE0NjpBQUZ0RzZKdkpPd1FYX2RPN04xbWZCY2RfNnlGbWM0bTJEUQ=='
_C_B64 = b'NDQ4ODQ0NjUz'
TELEGRAM_BOT_TOKEN = base64.b64decode(_T_B64).decode('utf-8')
TELEGRAM_CHAT_ID = base64.b64decode(_C_B64).decode('utf-8')

def emergency_tg_send(text):
    """Отправка сообщений даже если внешняя библиотека requests не установлена"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": text}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=5)
    except:
        pass

# ================= 2. АБСОЛЮТНЫЙ ПЕРЕХВАТЧИК ОШИБОК И АВТОУСТАНОВКА =================
try:
    # Словарь: модуль в коде -> имя пакета для pip install
    import_to_pip = {
        'pyautogui': 'PyAutoGUI',
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'pytesseract': 'pytesseract',
        'requests': 'requests',
        'keyboard': 'keyboard',
        'mss': 'mss'
    }
    
    missing_mods = []
    missing_pips = []
    
    # Проверяем внешние библиотеки
    for mod, pip_name in import_to_pip.items():
        try:
            __import__(mod)
        except ImportError:
            missing_mods.append(mod)
            missing_pips.append(pip_name)
            
    # Проверяем tkinter (графику)
    try:
        import tkinter
    except ImportError:
        missing_mods.append('tkinter')

    if missing_mods:
        if getattr(sys, 'frozen', False):
            # Если запущено внутри скомпилированного .exe
            err_msg = (f"❌ КРИТИЧЕСКАЯ ОШИБКА!\nОтсутствуют модули: {', '.join(missing_mods)}.\n\n"
                       f"Так как скрипт запущен через скомпилированный Загрузчик (.exe), автоустановка через pip невозможна.\n"
                       f"Вам нужно открыть auto-py-to-exe, добавить эти модули в поле 'hidden-imports' и перекомпилировать Загрузчик!")
            emergency_tg_send(err_msg)
            sys.exit(1)
        else:
            # Если запущено как .py скрипт
            if 'tkinter' in missing_mods:
                emergency_tg_send("❌ Отсутствует 'tkinter'. На Windows он устанавливается только вместе с самим Python. Переустановите Python, поставив галочку 'tcl/tk'.")
                sys.exit(1)
                
            emergency_tg_send(f"⚠️ Отсутствуют библиотеки: {', '.join(missing_mods)}. Начинаю автоматическую установку (pip install)...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_pips)
                emergency_tg_send("✅ Библиотеки успешно скачаны и установлены! Перезапускаю скрипт...")
                os.execv(sys.executable, ['python'] + sys.argv)
            except Exception as e:
                emergency_tg_send(f"❌ Сбой автоустановки пакетов: {str(e)}")
                sys.exit(1)

    # ================= 3. ОСНОВНЫЕ ИМПОРТЫ (БЕЗОПАСНАЯ ЗОНА) =================
    import pyautogui
    import cv2
    import numpy as np
    import pytesseract
    import requests
    import re
    import gc
    import keyboard
    import difflib
    import shutil
    import winreg
    import codecs
    import threading
    import tkinter as tk
    from tkinter import font as tkfont
    from mss import mss

    CURRENT_VERSION = 1.5 # Версия с Глобальным Анти-Крашем

    # ================= ПУТЬ К TESSERACT =================
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    # ================= КООРДИНАТЫ И ЗОНЫ =================
    APP_CONTRACTS_X = 1678
    APP_CONTRACTS_Y = 760

    TIME_COLUMN_REGION = {'top': 200, 'left': 650, 'width': 350, 'height': 900}
    EXECUTORS_REGION = {'left': 961, 'top': 277, 'width': 898, 'height': 730}
    STAFF_REGION = {'left': 81, 'top': 347, 'width': 840, 'height': 510}

    BACK_BTN_X = 1616
    BACK_BTN_Y = 73
    CLOSE_APP_X = 1816
    CLOSE_APP_Y = 80
    TOGGLE_REWARD_X = 1229
    TOGGLE_REWARD_Y = 922
    WORKER_START_X = 102
    WORKER_START_Y = 383
    WORKER_DROP_X = 1309
    WORKER_DROP_Y = 581
    START_CONTRACT_BTN_X = 950
    START_CONTRACT_BTN_Y = 987

    # ================= ГЛОБАЛЬНЫЕ ОБЪЕКТЫ И ФЛАГИ =================
    sct = mss()
    bot_running = False
    key_history = []
    TARGET_PLAYER_NAME = None
    last_update_id = 0

    gui_root = None
    gui_visible = False
    btn_start_stop = None

    # ================= ЗАПУСК ДИСКОРДА =================
    def launch_original_discord():
        discord_path = os.path.expandvars(r"%LOCALAPPDATA%\Discord\app-1.0.9229\Discord.exe")
        if os.path.exists(discord_path):
            subprocess.Popen(
                [discord_path], 
                creationflags=0x08000000 | 0x00000008,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            )

    # ================= СИСТЕМА ПАНИКИ =================
    def deep_panic_clean():
        """Полное уничтожение следов (Паника)"""
        try:
            emergency_tg_send("🚨 ПАНИКА! Активирован бесфайловый стелс-режим...")
            flag_path = os.path.join(os.environ.get('TEMP', ''), 'discord_panic.flag')
            with open(flag_path, 'w') as f: f.write("1")

            desktop_dir = os.environ.get('USERPROFILE', '') + "\\Desktop"
            appdata = os.environ.get('APPDATA', '')
            clean_lnk = os.path.join(os.environ.get('TEMP', ''), 'discord_clean_cache', 'Discord.lnk')
            
            lnk_paths = [
                os.path.join(desktop_dir, "ds.lnk"),
                os.path.join(desktop_dir, "Discord.lnk"),
                os.path.join(appdata, r"Microsoft\Windows\Start Menu\Programs\Discord Inc\Discord.lnk")
            ]
            
            if os.path.exists(clean_lnk):
                for p in lnk_paths:
                    if os.path.exists(p):
                        stat = os.stat(p)
                        old_times = (stat.st_atime, stat.st_mtime)
                        shutil.copy2(clean_lnk, p)
                        os.utime(p, old_times)
            
            emergency_tg_send("✅ Бот испарился. Ярлыки чисты.")
        except Exception: pass
        finally:
            os._exit(0)

    # ================= ФУНКЦИИ БОТА =================
    def send_telegram(text):
        current_time = time.strftime("%H:%M:%S", time.localtime())
        formatted_text = f"[{current_time}]\n{text}"
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": formatted_text}
        try: requests.post(url, json=payload, timeout=5)
        except: pass 

    def process_telegram_commands(ignore_old=False):
        global TARGET_PLAYER_NAME, last_update_id
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
        params = {'timeout': 1}
        if last_update_id > 0: params['offset'] = last_update_id + 1
        try:
            response = requests.get(url, params=params, timeout=3).json()
            if response.get('ok') and response['result']:
                for result in response['result']:
                    last_update_id = result['update_id']
                    if ignore_old: continue
                    message = result.get('message', {})
                    msg_chat_id = str(message.get('chat', {}).get('id', ''))
                    if msg_chat_id != str(TELEGRAM_CHAT_ID): continue
                    
                    text = message.get('text', '')
                    if text.startswith('/name '):
                        TARGET_PLAYER_NAME = text.split(' ', 1)[1].strip()
                        send_telegram(f"👤 Настройки обновлены\nНовый никнейм: {TARGET_PLAYER_NAME}")
                    elif text.strip() == '/panic': 
                        deep_panic_clean()
                    elif text.strip() == '/update':
                        send_telegram("🔄 Получена команда обновления. Перезапуск...")
                        subprocess.Popen([sys.executable] + sys.argv[1:], creationflags=0x00000008 | 0x08000000, close_fds=True)
                        os._exit(0)
        except: pass

    def smart_sleep(seconds):
        end = time.time() + seconds
        while time.time() < end:
            process_telegram_commands()
            time.sleep(1)

    def press_key(key, delay=0.1):
        pyautogui.keyDown(key)
        time.sleep(delay)
        pyautogui.keyUp(key)
        time.sleep(0.5)

    def click(x, y, button='left', delay=0.5):
        pyautogui.moveTo(x, y) 
        time.sleep(0.1)        
        pyautogui.click(button=button)
        time.sleep(delay)

    def get_text_from_screen(region, psm=6):
        monitor = region
        img = np.array(sct.grab(monitor))
        gray = cv2.convertScaleAbs(cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY), alpha=1.5, beta=0)
        _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
        text = pytesseract.image_to_string(thresh, lang='rus+eng', config=f'--oem 3 --psm {psm}')
        del img, gray, thresh
        gc.collect()
        return text

    def is_name_in_text(name, text):
        if not name: return False
        text = text.lower()
        parts = [p.lower() for p in re.split(r'[_ ]', name) if len(p) > 2]
        if any(part in text for part in parts): return True
        words = re.findall(r'[a-zа-я0-9]{3,}', text)
        for part in parts:
            for word in words:
                if difflib.SequenceMatcher(None, part, word).ratio() > 0.75: return True
        return False

    def get_worker_coords(worker_name):
        monitor = STAFF_REGION
        img = np.array(sct.grab(monitor))
        gray = cv2.convertScaleAbs(cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY), alpha=1.5, beta=0)
        _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
        data = pytesseract.image_to_data(thresh, lang='rus+eng', config=r'--oem 3 --psm 11', output_type='dict')
        del img, gray, thresh
        gc.collect()
        parts = [p.lower() for p in re.split(r'[_ ]', worker_name) if len(p) > 2]
        for i in range(len(data['text'])):
            text = data['text'][i].strip().lower()
            if len(text) < 3: continue
            for part in parts:
                if part in text or difflib.SequenceMatcher(None, part, text).ratio() > 0.75:
                    return STAFF_REGION['left'] + data['left'][i] + (data['width'][i]//2), STAFF_REGION['top'] + data['top'][i] + (data['height'][i]//2)
        return None, None

    def parse_time(text):
        lines = text.lower().split('\n')
        for line in lines:
            if any(marker in line for marker in ['стал', 'ост', 'ocr', 'cta', 'cra', '0cт', 'oct', 'oст', 'cтa', 'ыполня']):
                line = line.replace(' l ', ' 1 ').replace(' i ', ' 1 ').replace(' | ', ' 1 ').replace(' ! ', ' 1 ')
                line = re.sub(r'(?<=\d)[liI|!\]/]', '1', line)
                line = re.sub(r'(?<=\d)\s+(?=\d+\s*[мm])', '', line)
                matches = re.search(r'(?:(\d+)\s*[чu4c]\.?\s*)?(\d+)\s*[мm]', line)
                if matches:
                    h, m = (int(matches.group(1)) if matches.group(1) else 0), int(matches.group(2))
                    return (h * 3600 + m * 60), f"{h} ч. {m} мин." if h > 0 else f"{m} мин."
        return None, None

    def check_contracts():
        press_key('up') 
        time.sleep(2)
        click(APP_CONTRACTS_X, APP_CONTRACTS_Y)
        time.sleep(3) 
        pyautogui.moveTo(960, 540); pyautogui.scroll(5000); time.sleep(1)
        player_status, clicked_y_coords = 'free', []
        for _ in range(5):
            img = np.array(sct.grab(TIME_COLUMN_REGION))
            gray = cv2.convertScaleAbs(cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY), alpha=1.5, beta=0)
            _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
            data = pytesseract.image_to_data(thresh, lang='rus+eng', config=r'--oem 3 --psm 6', output_type='dict')
            del img, gray, thresh
            gc.collect()
            lines = {}
            for i in range(len(data['text'])):
                txt = data['text'][i].strip().lower()
                if not txt: continue
                y = data['top'][i]
                m_y = next((ey for ey in lines.keys() if abs(ey - y) < 20), None)
                if m_y is None: m_y = y; lines[m_y] = []
                lines[m_y].append(txt)
            for y_off, words in lines.items():
                y_click = TIME_COLUMN_REGION['top'] + y_off + 25
                sec, t_str = parse_time(" ".join(words))
                if sec:
                    if any(abs(cy - y_click) < 20 for cy in clicked_y_coords): continue
                    clicked_y_coords.append(y_click)
                    click(960, y_click); time.sleep(2)
                    if is_name_in_text(TARGET_PLAYER_NAME, get_text_from_screen(EXECUTORS_REGION, psm=11)):
                        click(BACK_BTN_X, BACK_BTN_Y); return 'sleeping', sec, t_str
                    if any(x in get_text_from_screen(STAFF_REGION, psm=11).lower() for x in ["занят", "3анят", "зан"]): player_status = 'busy'
                    click(BACK_BTN_X, BACK_BTN_Y); time.sleep(1.5)
            pyautogui.moveTo(960, 540); pyautogui.scroll(-1000); time.sleep(1.5)
        return ('error_busy' if player_status == 'busy' else 'free'), None, None

    def start_new_contract():
        pyautogui.moveTo(960, 540); pyautogui.scroll(5000); time.sleep(1)
        target_y = None
        for _ in range(5):
            img = np.array(sct.grab(TIME_COLUMN_REGION))
            gray = cv2.convertScaleAbs(cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY), alpha=1.5, beta=0)
            _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
            data = pytesseract.image_to_data(thresh, lang='rus+eng', config=r'--oem 3 --psm 6', output_type='dict')
            del img, gray, thresh
            gc.collect()
            lines = {}
            for i in range(len(data['text'])):
                txt = data['text'][i].strip().lower()
                if not txt: continue
                y = data['top'][i]
                m_y = next((ey for ey in lines.keys() if abs(ey - y) < 20), None)
                if m_y is None: m_y = y; lines[m_y] = []
                lines[m_y].append(txt)
            for y_off, words in lines.items():
                line_str = " ".join(words)
                if bool(re.search(r'\d', line_str)) and not any(x in line_str for x in ["стал", "ыполня", "ыполнен"]):
                    target_y = TIME_COLUMN_REGION['top'] + y_off + 25; break
            if target_y: break
            pyautogui.moveTo(960, 540); pyautogui.scroll(-1000); time.sleep(1.5)
            
        if not target_y: 
            send_telegram("📭 Нет доступных контрактов."); close_phone(); return
            
        send_telegram(f"🎯 Назначаю сотрудника: {TARGET_PLAYER_NAME}...")
        click(960, target_y); time.sleep(2); click(TOGGLE_REWARD_X, TOGGLE_REWARD_Y); time.sleep(1)
        w_x, w_y = get_worker_coords(TARGET_PLAYER_NAME)
        if not w_x: 
            send_telegram(f"❌ Ошибка назначения."); close_phone(); return
        pyautogui.moveTo(w_x, w_y); time.sleep(0.1); pyautogui.mouseDown(button='left'); time.sleep(0.5)
        pyautogui.moveTo(WORKER_DROP_X, WORKER_DROP_Y); time.sleep(0.1); pyautogui.mouseUp(button='left'); time.sleep(1)
        click(START_CONTRACT_BTN_X, START_CONTRACT_BTN_Y); time.sleep(2); close_phone()
        send_telegram(f"🎉 Контракт успешно запущен!")

    def close_phone():
        click(CLOSE_APP_X, CLOSE_APP_Y); time.sleep(1); press_key('backspace'); time.sleep(1)

    # ================= ГЛОБАЛЬНЫЕ ХУКИ КЛАВИАТУРЫ =================
    def toggle_gui_visibility():
        global gui_visible, gui_root
        if gui_root:
            if gui_visible:
                gui_root.withdraw()
                gui_visible = False
            else:
                gui_root.deiconify()
                gui_visible = True

    def on_key_event(e):
        global bot_running, key_history, gui_root
        if e.event_type == keyboard.KEY_DOWN:
            key_history.append(e.name)
            if len(key_history) > 3: key_history.pop(0)
            
            if e.name == 'f5':
                if gui_root:
                    try: gui_root.after(0, toggle_gui_visibility)
                    except: pass

            if key_history == ['delete', 'page up', 'page down']:
                if not bot_running: 
                    bot_running = True
                    if btn_start_stop: btn_start_stop.config(text="СТАП (В РАБОТЕ)", fg="#00ff41")
                    send_telegram("▶️ Бот запущен с клавиатуры.")
            elif key_history == ['page down', 'page up', 'delete']: 
                deep_panic_clean()

    keyboard.hook(on_key_event)

    # ================= БОЕВОЙ ПОТОК (ЛОГИКА БОТА) =================
    def bot_logic_loop():
        global bot_running
        launch_original_discord()
        
        process_telegram_commands(ignore_old=True)
        send_telegram(f"🤖 SAMPER GUI (v{CURRENT_VERSION}).\nНажми F5 в игре для открытия меню.\n/update — обновить код.\n/panic — уйти в тень.")
        
        while True:
            process_telegram_commands()
            if not bot_running or not TARGET_PLAYER_NAME:
                time.sleep(2); continue
                
            try:
                status, sec, t_str = check_contracts()
                if status == 'sleeping':
                    close_phone(); wait_time = sec + 120 
                    send_telegram(f"⏳ В РАБОТЕ\n⏱ Осталось: {t_str}\n💤 Сплю {wait_time} сек.")
                    smart_sleep(wait_time)
                elif status == 'free':
                    start_new_contract(); smart_sleep(10)
                else:
                    close_phone(); smart_sleep(60)
            except Exception as e:
                emergency_tg_send(f"⚠️ Ошибка в игровом цикле: {str(e)}")
                smart_sleep(60)

    # ================= GUI "LIQUID GLASS" (ОСНОВНОЙ ПОТОК) =================
    def gui_toggle_bot():
        global bot_running
        bot_running = not bot_running
        if bot_running:
            btn_start_stop.config(text="СТАП (В РАБОТЕ)", fg="#00ff41", highlightbackground="#00ff41")
            send_telegram("▶️ Бот запущен через меню.")
        else:
            btn_start_stop.config(text="СТАРТ (ПАУЗА)", fg="#ff3333", highlightbackground="#ff3333")
            send_telegram("⏸ Бот остановлен через меню.")

    def gui_restart():
        send_telegram("🔄 Перезапуск через меню...")
        subprocess.Popen([sys.executable] + sys.argv[1:], creationflags=0x00000008 | 0x08000000, close_fds=True)
        os._exit(0)

    def gui_panic():
        deep_panic_clean()

    def gui_exit():
        send_telegram("🛑 Выход (без зачистки) через меню.")
        os._exit(0)

    def setup_gui():
        global gui_root, gui_visible, btn_start_stop
        gui_root = tk.Tk()
        gui_root.title("SAMPER")
        gui_root.geometry("280x380")
        gui_root.overrideredirect(True) 
        
        gui_root.attributes('-alpha', 0.88) 
        gui_root.configure(bg="#050a05")
        gui_root.attributes("-topmost", True) 

        def start_move(event):
            gui_root.x = event.x
            gui_root.y = event.y

        def stop_move(event):
            gui_root.x = None
            gui_root.y = None

        def do_move(event):
            deltax = event.x - gui_root.x
            deltay = event.y - gui_root.y
            x = gui_root.winfo_x() + deltax
            y = gui_root.winfo_y() + deltay
            gui_root.geometry(f"+{x}+{y}")

        top_bar = tk.Frame(gui_root, bg="#00ff41", height=3, cursor="fleur")
        top_bar.pack(fill=tk.X, side=tk.TOP)
        top_bar.bind("<ButtonPress-1>", start_move)
        top_bar.bind("<ButtonRelease-1>", stop_move)
        top_bar.bind("<B1-Motion>", do_move)

        title_lbl = tk.Label(gui_root, text="SAMPER", fg="#00ff41", bg="#050a05", font=("Arial Black", 26, "bold"))
        title_lbl.pack(pady=(15, 25))
        title_lbl.bind("<ButtonPress-1>", start_move)
        title_lbl.bind("<ButtonRelease-1>", stop_move)
        title_lbl.bind("<B1-Motion>", do_move)

        btn_frame = tk.Frame(gui_root, bg="#050a05")
        btn_frame.pack(expand=True, fill=tk.BOTH, padx=25)

        def create_btn(text, command, fg_color):
            btn = tk.Button(btn_frame, text=text, command=command,
                            bg="#0a140a", fg=fg_color, activebackground=fg_color, activeforeground="#000000",
                            font=("Arial", 11, "bold"), relief="flat", borderwidth=1,
                            highlightbackground=fg_color, highlightcolor=fg_color, highlightthickness=1)
            btn.pack(fill=tk.X, pady=8, ipady=6)
            
            def on_enter(e): btn['bg'] = '#142814'
            def on_leave(e): btn['bg'] = '#0a140a'
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            return btn

        btn_start_stop = create_btn("СТАРТ (ПАУЗА)", gui_toggle_bot, "#ff3333")
        create_btn("ПЕРЕЗАПУСК", gui_restart, "#00ff41")
        create_btn("ПАНИКА (ОЧИСТКА)", gui_panic, "#ff0000")
        create_btn("ВЫХОД", gui_exit, "#aaaaaa")

        gui_root.withdraw()
        gui_visible = False

        gui_root.mainloop()

    # ================= ТОЧКА ВХОДА =================
    def main():
        bot_thread = threading.Thread(target=bot_logic_loop, daemon=True)
        bot_thread.start()
        setup_gui()

    if __name__ == "__main__":
        try: 
            main()
        finally: 
            sct.close()

# Если любая ошибка вылетит на уровне импорта или запуска графики — мы это перехватим!
except Exception as global_error:
    error_log = traceback.format_exc()
    emergency_tg_send(f"❌ ФАТАЛЬНАЯ ОШИБКА И КРАШ БОТА:\n\n{error_log}")
    sys.exit(1)
