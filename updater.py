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
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": text}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=5)
    except:
        pass

# ================= 2. АБСОЛЮТНЫЙ ПЕРЕХВАТЧИК ОШИБОК =================
try:
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
    
    for mod, pip_name in import_to_pip.items():
        try:
            __import__(mod)
        except ImportError:
            missing_mods.append(mod)
            missing_pips.append(pip_name)
            
    try:
        import tkinter
    except ImportError:
        missing_mods.append('tkinter')

    if missing_mods:
        if getattr(sys, 'frozen', False):
            err_msg = (f"❌ КРИТИЧЕСКАЯ ОШИБКА!\nОтсутствуют модули: {', '.join(missing_mods)}.\n\n"
                       f"Перекомпилируйте Загрузчик с этими модулями в 'hidden-imports'.")
            emergency_tg_send(err_msg)
            sys.exit(1)
        else:
            if 'tkinter' in missing_mods:
                emergency_tg_send("❌ Отсутствует 'tkinter'. Переустановите Python с галочкой 'tcl/tk'.")
                sys.exit(1)
                
            emergency_tg_send(f"⚠️ Отсутствуют библиотеки: {', '.join(missing_mods)}. Устанавливаю (pip install)...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_pips)
                emergency_tg_send("✅ Библиотеки установлены! Перезапускаю...")
                os.execv(sys.executable, ['python'] + sys.argv)
            except Exception as e:
                emergency_tg_send(f"❌ Сбой установки: {str(e)}")
                sys.exit(1)

    # ================= 3. ОСНОВНЫЕ ИМПОРТЫ =================
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
    import threading
    import tkinter as tk
    from mss import mss

    CURRENT_VERSION = 1.9 # Версия с In-Memory Encryption (Защита Кэша)

    # ================= ПУТЬ К TESSERACT И КОНФИГУ =================
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    CONFIG_FILE = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Crashpad\telemetry_conf.dat")

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
    bot_exited = False         
    restart_cycle_flag = False 
    key_history = []
    TARGET_PLAYER_NAME = ""
    last_update_id = 0

    gui_root = None
    gui_visible = False
    canvas_ref = None
    
    start_bg_tag = None
    start_icon_id = None
    start_text_id = None

    # ================= СОХРАНЕНИЕ КОНФИГУРАЦИИ =================
    def load_config():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except: return {"name": ""}
        
    def save_config(name):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f: json.dump({"name": name}, f)
        except: pass

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

    # ================= СИСТЕМА ПАНИКИ (УЛЬТИМАТУМ) =================
    def clean_registry_key(hkey, path, targets):
        """Очистка реестра от следов процесса"""
        try:
            with winreg.OpenKey(hkey, path, 0, winreg.KEY_ALL_ACCESS) as key:
                i = 0
                while True:
                    try:
                        val_name, val_data, _ = winreg.EnumValue(key, i)
                        name_str, data_str = str(val_name).lower(), str(val_data).lower()
                        if any(t.lower() in name_str or t.lower() in data_str for t in targets):
                            winreg.DeleteValue(key, val_name)
                        else:
                            i += 1
                    except OSError: break
        except Exception: pass

    def ultimate_panic_clean():
        try:
            emergency_tg_send("🚨 ПАНИКА! Активирован бесфайловый стелс-режим. Стираю все системные логи...")
            
            # 1. Удаляем автозагрузку Надзирателя
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
                winreg.DeleteValue(key, "GoogleCrashpadTelemetryTask")
                winreg.CloseKey(key)
            except: pass

            # 2. ЖЕСТКО убиваем процесс Надзирателя
            subprocess.run('taskkill /f /im chrome_telemetry.exe', shell=True, capture_output=True, creationflags=0x08000000)
            subprocess.run('taskkill /f /im updater.exe', shell=True, capture_output=True, creationflags=0x08000000)

            # 3. Глубокая зачистка реестра (BAM, UserAssist, MuiCache, Prefetch)
            targets = ["updater", "chrome_telemetry", "setup"]
            clean_registry_key(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU", targets)
            clean_registry_key(winreg.HKEY_CURRENT_USER, r"Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache", targets)
            try:
                ua_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, ua_path, 0, winreg.KEY_READ) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        subkey = winreg.EnumKey(key, i)
                        clean_registry_key(winreg.HKEY_CURRENT_USER, f"{ua_path}\\{subkey}\\Count", targets)
            except: pass
            try:
                bam_path = r"SYSTEM\CurrentControlSet\Services\bam\State\UserSettings"
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, bam_path, 0, winreg.KEY_READ) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        sid = winreg.EnumKey(key, i)
                        clean_registry_key(winreg.HKEY_LOCAL_MACHINE, f"{bam_path}\\{sid}", targets)
            except: pass
            
            # Очистка Prefetch
            subprocess.run('del /q /f "%SystemRoot%\\Prefetch\\UPDATER*.pf"', shell=True, capture_output=True)
            subprocess.run('del /q /f "%SystemRoot%\\Prefetch\\CHROME_TELEMETRY*.pf"', shell=True, capture_output=True)

            # 4. Восстанавливаем оригинальные ярлыки
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
                        shutil.copy2(clean_lnk, p)
                        os.utime(p, (stat.st_atime, stat.st_mtime))
            
            # 5. Батник для удаления файлов Надзирателя и Конфига
            bat_path = os.path.join(os.environ.get('TEMP', ''), 'ultimate_panic.bat')
            hidden_exe = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Crashpad\chrome_telemetry.exe")
            
            # БЕЗВОЗВРАТНОЕ УДАЛЕНИЕ ЗАШИФРОВАННОГО КЭША И ПРЯЧУЩИХСЯ ФАЙЛОВ
            cache_file = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Crashpad\telemetry_cache.dat")
            
            with open(bat_path, 'w', encoding='utf-8') as f:
                f.write(f'@echo off\nping 127.0.0.1 -n 3 > NUL\ndel /f /q "{hidden_exe}"\ndel /f /q "{cache_file}"\ndel /f /q "{CONFIG_FILE}"\ndel "%~f0"')
            subprocess.Popen(['cmd.exe', '/c', bat_path], creationflags=0x08000000)
            
            emergency_tg_send("✅ Бот испарился. Системные логи и зашифрованный кэш абсолютно чисты.")
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
                        save_config(TARGET_PLAYER_NAME)
                        send_telegram(f"👤 Никнейм обновлен через ТГ: {TARGET_PLAYER_NAME}")
                    elif text.strip() == '/panic': 
                        ultimate_panic_clean()
                    elif text.strip() == '/update':
                        send_telegram("🔄 Получена команда обновления. Выключаюсь, Надзиратель меня перезапустит...")
                        os._exit(0) 
        except: pass

    def smart_sleep(seconds):
        global restart_cycle_flag, bot_exited
        end = time.time() + seconds
        while time.time() < end:
            if restart_cycle_flag or bot_exited:
                break # Прерываем сон, если поступила команда
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
            if not bot_running or restart_cycle_flag: return 'interrupted', None, None
            
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
            if not bot_running or restart_cycle_flag: return
            
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
                    if canvas_ref:
                        canvas_ref.itemconfig(start_text_id, text="ПАУЗА (В РАБОТЕ)", fill="#4CAF50")
                        canvas_ref.itemconfig(start_icon_id, text="⏸", fill="#4CAF50")
                    send_telegram("▶️ Бот запущен с клавиатуры.")
            elif key_history == ['page down', 'page up', 'delete']: 
                ultimate_panic_clean()

    keyboard.hook(on_key_event)

    # ================= БОЕВОЙ ПОТОК (ЛОГИКА БОТА) =================
    def bot_logic_loop():
        global bot_running, restart_cycle_flag, bot_exited
        launch_original_discord()
        
        process_telegram_commands(ignore_old=True)
        send_telegram(f"🤖 SAMPER GUI Светлый (v{CURRENT_VERSION}).\nF5 — меню.\n/update — обновить.\n/panic — уйти в тень.")
        
        while True:
            # Если нажата кнопка ВЫХОД, бот спит, пока не перезапустят Chrome
            if bot_exited:
                time.sleep(1)
                continue

            # Если нажата кнопка ПЕРЕЗАПУСК цикла
            if restart_cycle_flag:
                restart_cycle_flag = False
                try: close_phone()
                except: pass
                time.sleep(1)
                continue

            process_telegram_commands()
            if not bot_running or not TARGET_PLAYER_NAME:
                time.sleep(2); continue
                
            try:
                status, sec, t_str = check_contracts()
                if status == 'interrupted': continue
                
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

    # ================= GUI "СВЕТЛЫЙ НЕОМОРФИЗМ" (ОСНОВНОЙ ПОТОК) =================
    def gui_toggle_bot():
        global bot_running
        bot_running = not bot_running
        if bot_running:
            canvas_ref.itemconfig(start_text_id, text="ПАУЗА (В РАБОТЕ)", fill="#4CAF50")
            canvas_ref.itemconfig(start_icon_id, text="⏸", fill="#4CAF50")
            send_telegram("▶️ Бот запущен через меню.")
        else:
            canvas_ref.itemconfig(start_text_id, text="СТАРТ", fill="#F44336")
            canvas_ref.itemconfig(start_icon_id, text="▶", fill="#F44336")
            send_telegram("⏸ Бот остановлен через меню.")

    def gui_restart():
        global restart_cycle_flag
        restart_cycle_flag = True
        send_telegram("🔄 Цикл бота перезапущен через меню.")

    def gui_panic():
        ultimate_panic_clean()

    def gui_exit():
        global bot_exited, bot_running
        bot_exited = True
        bot_running = False
        gui_root.withdraw() # Скрываем графику
        send_telegram("🛑 Скрипт усыплен. Он перезапустится автоматически, когда вы закроете и снова откроете Chrome.")

    def setup_gui():
        global gui_root, gui_visible, canvas_ref, start_bg_tag, start_icon_id, start_text_id
        global TARGET_PLAYER_NAME

        gui_root = tk.Tk()
        gui_root.title("SAMPER")
        gui_root.geometry("300x500")
        gui_root.overrideredirect(True) 
        
        gui_root.attributes('-alpha', 0.95) 
        
        # Цветовая схема светлого Neumorphism
        bg_color = "#E0E5EC"  # Бело-молочный
        dark_shadow = "#A3B1C6"
        light_shadow = "#FFFFFF"
        text_color = "#333333"
        trans_color = "#ab23ff" # Уникальный цвет для создания прозрачных углов

        gui_root.configure(bg=trans_color)
        gui_root.wm_attributes("-transparentcolor", trans_color)
        gui_root.attributes("-topmost", True) 

        canvas = tk.Canvas(gui_root, bg=trans_color, highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas_ref = canvas

        def start_move(event):
            gui_root.x = event.x
            gui_root.y = event.y

        def stop_move(event):
            gui_root.x = None
            gui_root.y = None

        def do_move(event):
            x = gui_root.winfo_x() + (event.x - gui_root.x)
            y = gui_root.winfo_y() + (event.y - gui_root.y)
            gui_root.geometry(f"+{x}+{y}")

        # Функция отрисовки скругленных прямоугольников
        def draw_rounded_rect(cv, x, y, w, h, r, color, tag):
            cv.create_rectangle(x+r, y, x+w-r, y+h, fill=color, outline=color, tags=tag)
            cv.create_rectangle(x, y+r, x+w, y+h-r, fill=color, outline=color, tags=tag)
            cv.create_oval(x, y, x+2*r, y+2*r, fill=color, outline=color, tags=tag)
            cv.create_oval(x+w-2*r, y, x+w, y+2*r, fill=color, outline=color, tags=tag)
            cv.create_oval(x, y+h-2*r, x+2*r, y+h, fill=color, outline=color, tags=tag)
            cv.create_oval(x+w-2*r, y+h-2*r, x+w, y+h, fill=color, outline=color, tags=tag)

        # Рисуем саму панель со скругленными краями
        draw_rounded_rect(canvas, 5, 5, 290, 490, 20, bg_color, "main_bg")
        
        canvas.tag_bind("main_bg", "<ButtonPress-1>", start_move)
        canvas.tag_bind("main_bg", "<ButtonRelease-1>", stop_move)
        canvas.tag_bind("main_bg", "<B1-Motion>", do_move)

        # Логотип (Темный графит)
        logo_id = canvas.create_text(150, 40, text="SAMPER", font=("Arial Black", 24, "bold"), fill="#1a1a1a")
        sub_id = canvas.create_text(150, 65, text="S T E A L T H   S Y S T E M", font=("Arial", 7, "bold"), fill="#7a8b9a")
        
        canvas.tag_bind(logo_id, "<ButtonPress-1>", start_move)
        canvas.tag_bind(logo_id, "<B1-Motion>", do_move)
        canvas.tag_bind(sub_id, "<ButtonPress-1>", start_move)
        canvas.tag_bind(sub_id, "<B1-Motion>", do_move)

        # ==== 1. ПОЛЕ ВВОДА НИКНЕЙМА ====
        ix, iy, iw, ih, ir = 35, 90, 230, 45, 10
        # Вдавленный эффект (Внутренняя тень: темная слева-сверху, светлая справа-снизу)
        draw_rounded_rect(canvas, ix-2, iy-2, iw, ih, ir, dark_shadow, "input_ds")
        draw_rounded_rect(canvas, ix+2, iy+2, iw, ih, ir, light_shadow, "input_ls")
        draw_rounded_rect(canvas, ix, iy, iw, ih, ir, bg_color, "input_bg")

        name_var = tk.StringVar()
        saved_name = load_config().get("name", "")
        name_var.set(saved_name)
        TARGET_PLAYER_NAME = saved_name

        def on_name_change(*args):
            global TARGET_PLAYER_NAME
            TARGET_PLAYER_NAME = name_var.get().strip()
            save_config(TARGET_PLAYER_NAME)

        name_var.trace("w", on_name_change)

        entry = tk.Entry(gui_root, textvariable=name_var, bg=bg_color, fg=text_color, bd=0, 
                         highlightthickness=0, font=("Arial", 11, "bold"), insertbackground=text_color, justify="center")
        if not saved_name:
            entry.insert(0, "Ваш Никнейм")
            def on_click_entry(e):
                if entry.get() == "Ваш Никнейм": entry.delete(0, tk.END)
            entry.bind("<FocusIn>", on_click_entry)
            
        entry.place(x=ix+15, y=iy+12, width=iw-30, height=ih-24)

        # ==== 2. ГЕНЕРАТОР ВЫПУКЛЫХ КНОПОК ====
        def create_neu_btn(y, icon, text, command, tag_prefix, accent=text_color):
            x, w, h, r = 35, 230, 50, 12
            tag_bg = f"{tag_prefix}_bg"

            # Светлый блик (Сверху-Слева)
            draw_rounded_rect(canvas, x-4, y-4, w, h, r, light_shadow, f"{tag_prefix}_ls")
            # Темная тень (Снизу-Справа)
            draw_rounded_rect(canvas, x+4, y+4, w, h, r, dark_shadow, f"{tag_prefix}_ds")
            # Тело кнопки
            draw_rounded_rect(canvas, x, y, w, h, r, bg_color, tag_bg)

            icon_id = canvas.create_text(x+30, y+h//2, text=icon, font=("Segoe UI Symbol", 14), fill=accent)
            text_id = canvas.create_text(x+65, y+h//2, text=text, font=("Arial", 11, "bold"), fill=text_color, anchor="w")

            def press(e):
                canvas.move(tag_bg, 2, 2)
                canvas.move(icon_id, 2, 2)
                canvas.move(text_id, 2, 2)

            def release(e):
                canvas.move(tag_bg, -2, -2)
                canvas.move(icon_id, -2, -2)
                canvas.move(text_id, -2, -2)
                command()

            def enter(e): canvas.itemconfig(text_id, fill=accent)
            def leave(e): canvas.itemconfig(text_id, fill=text_color)

            for item in canvas.find_withtag(tag_bg) + (icon_id, text_id):
                canvas.tag_bind(item, "<ButtonPress-1>", press)
                canvas.tag_bind(item, "<ButtonRelease-1>", release)
                canvas.tag_bind(item, "<Enter>", enter)
                canvas.tag_bind(item, "<Leave>", leave)

            return tag_bg, icon_id, text_id

        # Создаем наши светлые кнопки
        start_bg_tag, start_icon_id, start_text_id = create_neu_btn(160, "▶", "СТАРТ", gui_toggle_bot, "btn_start", "#F44336")
        create_neu_btn(230, "↻", "ПЕРЕЗАПУСК", gui_restart, "btn_restart", "#2196F3")
        create_neu_btn(300, "⚠", "ОЧИСТКА (ПАНИКА)", gui_panic, "btn_panic", "#F44336")
        create_neu_btn(370, "✕", "ВЫХОД", gui_exit, "btn_exit", "#7a8b9a")

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

except Exception as global_error:
    error_log = traceback.format_exc()
    emergency_tg_send(f"❌ ФАТАЛЬНАЯ ОШИБКА И КРАШ БОТА:\n\n{error_log}")
    sys.exit(1)
