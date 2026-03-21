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
import subprocess
import winreg
from mss import mss

# ================= НАСТРОЙКИ ТЕЛЕГРАМ =================
_T_B64 = b'Nzk5NjAyMjE0NjpBQUZ0RzZKdkpPd1FYX2RPN04xbWZCY2RfNnlGbWM0bTJEUQ=='
_C_B64 = b'NDQ4ODQ0NjUz'

TELEGRAM_BOT_TOKEN = base64.b64decode(_T_B64).decode('utf-8')
TELEGRAM_CHAT_ID = base64.b64decode(_C_B64).decode('utf-8')

CURRENT_VERSION = 1.3 # Версия для GitHub

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

# ================= СИСТЕМА ПАНИКИ =================
def ultimate_panic_clean():
    """Полное уничтожение Надзирателя, Автозагрузки и Кэша"""
    send_telegram("🚨 ПАНИКА! Уничтожаю Надзирателя и стираю все следы из системы...")
    try:
        # 1. Удаляем автозагрузку Надзирателя из реестра
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
        winreg.DeleteValue(key, "GoogleCrashpadTelemetryTask")
        winreg.CloseKey(key)
    except: pass

    try:
        # 2. Жестко убиваем процесс Надзирателя, чтобы он не перезапустил бота
        subprocess.run('taskkill /f /im chrome_telemetry.exe', shell=True, capture_output=True, creationflags=0x08000000)
        
        # 3. Создаем bat-файл для удаления .exe Надзирателя и нашего кэша
        bat_path = os.path.join(os.environ.get('TEMP', ''), 'ultimate_panic.bat')
        hidden_exe = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Crashpad\chrome_telemetry.exe")
        cache_file = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Crashpad\telemetry_cache.dat")
        
        with open(bat_path, 'w', encoding='utf-8') as f:
            f.write(f'@echo off\nping 127.0.0.1 -n 3 > NUL\ndel /f /q "{hidden_exe}"\ndel /f /q "{cache_file}"\ndel "%~f0"')
        
        subprocess.Popen(['cmd.exe', '/c', bat_path], creationflags=0x08000000)
    except: pass
    
    send_telegram("✅ Система полностью очищена. Бот испарился.")
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
                    ultimate_panic_clean()
                elif text.strip() == '/update':
                    send_telegram("🔄 Команда принята. Самоуничтожаюсь, Надзиратель запустит меня с новым кодом...")
                    os._exit(0) # Убиваем себя. Надзиратель сам скачает новый код и воскресит нас!
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
    # Мгновенная телепортация курсора + микропауза
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
            # Смещение y + 25 для точного клика в центр контракта
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

def on_key_event(e):
    global bot_running, key_history
    if e.event_type == keyboard.KEY_DOWN:
        key_history.append(e.name)
        if len(key_history) > 3: key_history.pop(0)
        if key_history == ['delete', 'page up', 'page down']:
            if not bot_running: bot_running = True; send_telegram("▶️ Бот запущен.")
        elif key_history == ['page down', 'page up', 'delete']: 
            ultimate_panic_clean()

keyboard.hook(on_key_event)

def main():
    global bot_running
    process_telegram_commands(ignore_old=True)
    send_telegram(f"🤖 Боевой скрипт запущен (v{CURRENT_VERSION}). Жду ваших команд.\n/update — обновить код.\n/panic — уйти в тень.")
    
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
