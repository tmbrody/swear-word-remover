import time
import pyautogui
import pytesseract
from PIL import Image
import re
import threading
import imagehash

def load_swear_words(file_path):
    with open(file_path, 'r') as file:
        swear_words = [line.strip() for line in file]
    return swear_words

swear_words = load_swear_words('swear_words.txt')

last_subtitle_text = ""

lock = threading.Lock()

def capture_subtitle_thread():
    global last_subtitle_text
    while True:
        subtitle_text = capture_subtitle_text()
        with lock:
            last_subtitle_text = subtitle_text
        time.sleep(0.1)

def capture_subtitle_text():
    try:
        screenshot = pyautogui.screenshot(region=(1100, 1400, 970, 125))

        screenshot.save("screenshot.png")

        pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

        return pytesseract.image_to_string(screenshot)
    except Exception as e:
        print("Error:", e)

def compare_images(image_path1, image_path2, threshold=1):
    image1 = Image.open(image_path1)
    image2 = Image.open(image_path2)

    hash1 = imagehash.average_hash(image1)
    hash2 = imagehash.average_hash(image2)

    similarity = hash1 - hash2
    return similarity <= threshold

def clean_text(text):
    cleaned_words = [re.sub(r'[^a-zA-Z]', '', word) for word in text.split()]
    cleaned_text = ' '.join(cleaned_words)
    return cleaned_text

def swear_check_thread():
    global last_subtitle_text
    video_end_phrase = "videovideodone"
    video_batch_end_phrase = "videovideofinished"
    check_interval = 0.1
    muted = False

    while True:
        with lock:
            subtitle_text = last_subtitle_text
        cleaned_subtitle_text = clean_text(subtitle_text)
        subtitle_words = cleaned_subtitle_text.split()

        next_step = any(word.lower() == video_end_phrase for word in subtitle_words)

        finish_step = any(word.lower() == video_batch_end_phrase for word in subtitle_words)

        if next_step:
            pyautogui.hotkey('alt', 'f4')
            time.sleep(0.5)
            pyautogui.press('space')
        elif finish_step:
            pyautogui.hotkey('alt', 'f4')
            time.sleep(0.5)
            pyautogui.hotkey('alt', 'tab')
            pyautogui.hotkey('alt', 'tab')
            pyautogui.hotkey('ctrl', 'c')
        else:
            should_mute = any(word.lower() in swear_words for word in subtitle_words)

            if should_mute != muted:
                pyautogui.press('m')
                muted = not muted

            time.sleep(check_interval)

capture_thread = threading.Thread(target=capture_subtitle_thread)
capture_thread.daemon = True
capture_thread.start()

swear_thread = threading.Thread(target=swear_check_thread)
swear_thread.daemon = True
swear_thread.start()

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    pass