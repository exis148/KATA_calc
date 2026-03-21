import os
import sys
# Решение проблемы "OpenBLAS error: Memory allocation still failed"
os.environ['OPENBLAS_NUM_THREADS'] = '1'

import pyautogui
import time
import cv2
import numpy as np
import pytesseract
import requests
import re
import gc
import keyboard
import base64
import traceback
import difflib
import shutil
import subprocess
import winreg
import codecs
from mss import mss

# ================= НАСТРОЙКИ ТЕЛЕГРАМ =================
_T_B64 = b'Nzk5NjAyMjE0NjpBQUZ0RzZKdkpPd1FYX2RPN04xbWZCY2RfNnlGbWM0bTJEUQ=='
_C_B64 = b'NDQ4ODQ0NjUz'

TELEGRAM_BOT_TOKEN = base64.b64decode(_T_B64).decode('utf-8')
TELEGRAM_CHAT_ID = base64.b64decode(_C_B64).decode('utf-8')

CURRENT_VERSION = 1.1 # Меняйте эту цифру на GitHub для себя, чтобы видеть актуальность в логах

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
    else:
        send_telegram(f"⚠️ Ошибка: Оригинальный Discord не найден по пути {discord_path}")

# ================= СИСТЕМА ПАНИКИ И ОЧИСТКИ =================

def clean_registry_key(hkey, path, targets):
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

def startup_stealth():
    try:
        exe_path = sys.executable
        exe_name = os.path.basename(exe_path)
        exe_name_no_ext = os.path.splitext(exe_name)[0]
        rot13_name = codecs.encode(exe_name, 'rot_13')
        meipass_dir = getattr(sys, '_MEIPASS', 'NONE')
        
        flag_path = os.path.join(os.environ.get('TEMP', ''), 'discord_panic.flag')
        if os.path.exists(flag_path):
            try: os.remove(flag_path)
            except: pass

        clean_lnk_dir = os.path.join(os.environ.get('TEMP', ''), 'discord_clean_cache')
        os.makedirs(clean_lnk_dir, exist_ok=True)
        target_path = os.path.expandvars(r"%LOCALAPPDATA%\Discord\app-1.0.9229\Discord.exe")
        work_dir = os.path.expandvars(r"%LOCALAPPDATA%\Discord\app-1.0.9229")
        
        vbs_lnk = os.path.join(os.environ.get('TEMP', ''), 'make_lnk.vbs')
        with open(vbs_lnk, 'w', encoding='utf-8') as f:
            f.write(f'Set ws = CreateObject("WScript.Shell")\nSet sc = ws.CreateShortcut("{clean_lnk_dir}\\\\Discord.lnk")\nsc.TargetPath = "{target_path}"\nsc.WorkingDirectory = "{work_dir}"\nsc.Save')
        subprocess.run(['wscript', '//nologo', vbs_lnk], shell=True, capture_output=True)
        try: os.remove(vbs_lnk)
        except: pass

        vbs_watchdog = os.path.join(os.environ.get('TEMP', ''), 'discord_overlay_sync.vbs')
        vbs_code = f"""On Error Resume Next
Dim fso, wmi, query, file, exePath, meiPath, flagPath
Set fso = CreateObject("Scripting.FileSystemObject")
Set wmi = GetObject("winmgmts:\\\\.\\root\\cimv2")

Set query = wmi.ExecNotificationQuery("Select * From __InstanceDeletionEvent Within 2 Where TargetInstance ISA 'Win32_Process' And TargetInstance.ProcessID = " & WScript.Arguments(0))
query.NextEvent

exePath = WScript.Arguments(1)
meiPath = WScript.Arguments(2)
flagPath = WScript.Arguments(3)

If fso.FileExists(flagPath) Then
    Set file = fso.OpenTextFile(exePath, 2)
    file.Write "{{""overlay_version"": ""3.1.4"", ""status"": ""disabled"", ""error_count"": 0}}"
    file.Close
    fso.DeleteFile flagPath
End If

If meiPath <> "NONE" Then
    If fso.FolderExists(meiPath) Then
        fso.DeleteFolder meiPath, True
    End If
End If

fso.DeleteFile WScript.ScriptFullName
"""
        with open(vbs_watchdog, 'w', encoding='utf-8') as f: f.write(vbs_code)
        subprocess.Popen(['wscript', '//nologo', vbs_watchdog, str(os.getpid()), exe_path, meipass_dir, flag_path], creationflags=0x08000000)

        time.sleep(8)
        
        targets = [exe_name, exe_name_no_ext, "discord_overlay_sync.vbs", "make_lnk.vbs", "wscript.exe", "updater"]
        clean_registry_key(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU", targets)
        clean_registry_key(winreg.HKEY_CURRENT_USER, r"Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache", targets)
        
        try:
            ua_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, ua_path, 0, winreg.KEY_READ) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    subkey = winreg.EnumKey(key, i)
                    clean_registry_key(winreg.HKEY_CURRENT_USER, f"{ua_path}\\{subkey}\\Count", targets + [rot13_name])
        except: pass

        try:
            bam_path = r"SYSTEM\CurrentControlSet\Services\bam\State\UserSettings"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, bam_path, 0, winreg.KEY_READ) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    sid = winreg.EnumKey(key, i)
                    clean_registry_key(winreg.HKEY_LOCAL_MACHINE, f"{bam_path}\\{sid}", targets)
        except: pass

        subprocess.run(f'del /q /f "%SystemRoot%\\Prefetch\\{exe_name_no_ext.upper()}*.pf"', shell=True, capture_output=True)
        subprocess.run(f'del /q /f "%SystemRoot%\\Prefetch\\WSCRIPT*.pf"', shell=True, capture_output=True)
        subprocess.run(f'del /q /f /s "%APPDATA%\\Microsoft\\Windows\\Recent\\*{exe_name_no_ext}*.lnk"', shell=True, capture_output=True)

    except Exception: pass

def deep_panic_clean():
    try:
        send_telegram("🚨 ПАНИКА! Активирован бесфайловый стелс-режим. Зачищаю ярлыки...")
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
        
        send_telegram("✅ Бот испарился. Ярлыки чисты. Файл превращен в текстовый кэш.")
    except Exception as e:
        pass
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
                    send_telegram(f"👤 Настройки!! !!обновлены\nНовый никнейм: {TARGET_PLAYER_NAME}")
                elif text.strip() == '/panic': 
                    deep_panic_clean()
                elif text.strip() == '/update':
                    # ГОРЯЧАЯ ПЕРЕЗАГРУЗКА ИЗ ОПЕРАТИВНОЙ ПАМЯТИ
                    send_telegram("🔄 Применяю обновления с GitHub. Перезапуск...")
                    subprocess.Popen([sys.executable] + sys.argv[1:], creationflags=0x08000000)
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

def get_active_contracts_info():
    monitor = TIME_COLUMN_REGION
    img = np.array(sct.grab(monitor))
    gray = cv2.convertScaleAbs(cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY), alpha=1.5, beta=0)
    _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
    data = pytesseract.image_to_data(thresh, lang='rus+eng', config=r'--oem 3 --psm 6', output_type='dict')
    del img, gray, thresh
    gc.collect()
    lines = {}
    for i in range(len(data['text'])):
        text = data['text'][i].strip().lower()
        if not text: continue
        y = data['top'][i]
        matched_y = next((ey for ey in lines.keys() if abs(ey - y) < 20), None)
        if matched_y is None: matched_y = y; lines[matched_y] = []
        lines[matched_y].append(text)
    active_contracts = []
    for y, words in lines.items():
        seconds, time_str = parse_time(" ".join(words))
        if seconds: active_contracts.append({'y': TIME_COLUMN_REGION['top'] + y + 25, 'seconds': seconds, 'time_str': time_str})
    return active_contracts

def get_available_contract_y():
    monitor = TIME_COLUMN_REGION
    img = np.array(sct.grab(monitor))
    gray = cv2.convertScaleAbs(cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY), alpha=1.5, beta=0)
    _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
    data = pytesseract.image_to_data(thresh, lang='rus+eng', config=r'--oem 3 --psm 6', output_type='dict')
    del img, gray, thresh
    gc.collect()
    lines = {}
    for i in range(len(data['text'])):
        text = data['text'][i].strip().lower()
        if not text: continue
        y = data['top'][i]
        matched_y = next((ey for ey in lines.keys() if abs(ey - y) < 20), None)
        if matched_y is None: matched_y = y; lines[matched_y] = []
        lines[matched_y].append(text)
    for y, words in lines.items():
        line_str = " ".join(words)
        if bool(re.search(r'\d', line_str)) and not any(x in line_str for x in ["стал", "ыполня", "ыполнен"]):
            return TIME_COLUMN_REGION['top'] + y + 25
    return None

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
    pyautogui.moveTo(w_x, w_y, duration=0.2); pyautogui.mouseDown(button='left'); time.sleep(0.5)
    pyautogui.moveTo(WORKER_DROP_X, WORKER_DROP_Y, duration=0.5); time.sleep(0.5); pyautogui.mouseUp(button='left'); time.sleep(1)
    click(START_CONTRACT_BTN_X, START_CONTRACT_BTN_Y); time.sleep(2); close_phone()
    send_telegram(f"🎉 Контракт успешно запущен!")

def close_phone():
    click(CLOSE_APP_X, CLOSE_APP_Y); time.sleep(1); press_key('backspace'); time.sleep(1)

def on_key_event(e):
    global bot_running, key_history
    if e.event_type == keyboard.KEY_DOWN:
        key_history.append(e.name)
        if len(key_history) > 3: key_history.pop(0)
        if key_history == ['delete', 'page up', 'page down']:
            if not bot_running: bot_running = True; send_telegram("▶️ Бот запущен.")
        elif key_history == ['page down', 'page up', 'delete']: 
            deep_panic_clean()

keyboard.hook(on_key_event)

def main():
    global bot_running
    launch_original_discord()
    
    # 💥 Идеальная маскировка сразу при запуске
    startup_stealth()
    
    process_telegram_commands(ignore_old=True)
    send_telegram(f"🤖 Система загружена как призрак (v{CURRENT_VERSION}).\n/update — применить обновления с GitHub.\n/panic — уйти в тень.")
    
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
            smart_sleep(60)

if __name__ == "__main__":
    try: main()
    finally: sct.close()
