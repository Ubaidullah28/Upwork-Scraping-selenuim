import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import random
import sys
import re
from datetime import datetime, timedelta
import json
import pyautogui
import os


sys.stdout.reconfigure(encoding='utf-8')

GMAIL_EMAIL = "aliraza289777@gmail.com"
GMAIL_PASSWORD = "upworkscrap123"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TIME_FILE = os.path.join(BASE_DIR, "time.txt")

def human_sleep(min_s=2, max_s=5):
    time.sleep(random.uniform(min_s, max_s))

def slow_scroll(driver, pause_time=1):
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        human_sleep(pause_time, pause_time + 2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def simulate_typing(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.15))

def parse_posted_time(text):
    now = datetime.now()
    text = text.lower()
    if 'minute' in text:
        return now - timedelta(minutes=int(re.search(r'\d+', text).group()))
    elif 'hour' in text:
        return now - timedelta(hours=int(re.search(r'\d+', text).group()))
    elif 'day' in text:
        return now - timedelta(days=int(re.search(r'\d+', text).group()))
    return now

def click_cloudflare_checkbox_pyautogui():
   
    time.sleep(4.5)                           #7
    #pyautogui.moveTo(799, 495, duration=1.5)  # Move to checkbox      
    pyautogui.click(799,495)
    time.sleep(5)

# 🔁 Read and update time.txt
def read_last_scrape_time(query):
    try:
        with open(TIME_FILE, "r", encoding="utf-8") as f:
            for line in f:
                saved_query, saved_time = line.strip().split(",")
                if saved_query.lower() == query.lower():
                    return datetime.strptime(saved_time, '%Y-%m-%d %H:%M:%S')
    except FileNotFoundError:
        pass
    return None

def update_scrape_time(query):
    current_time = datetime.now() - timedelta(minutes=2)
    lines = []
    found = False
    try:
        with open(TIME_FILE, "r", encoding="utf-8") as f:
            for line in f:
                saved_query, saved_time = line.strip().split(",")
                if saved_query.lower() == query.lower():
                    lines.append(f"{query},{current_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    found = True
                else:
                    lines.append(line)
    except FileNotFoundError:
        pass

    if not found:
        lines.append(f"{query},{current_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    with open(TIME_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)




def login_with_google(driver, email, password):
    driver.get("https://www.upwork.com/ab/account-security/login")
    human_sleep(3, 5)
    try:
        google_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#login_google_submit > span"))
        )
        google_btn.click()
    except:
        return
    human_sleep(4, 6)
    driver.switch_to.window(driver.window_handles[-1])
    try:
        email_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
        )
        simulate_typing(email_input, email)
        email_input.send_keys(Keys.ENTER)
    except:
        return
    human_sleep(4, 6)
    try:
        password_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
        )
        simulate_typing(password_input, password)
        password_input.send_keys(Keys.ENTER)
    except:
        return
    human_sleep(8, 12)
    driver.switch_to.window(driver.window_handles[0])

def extract_jobs_from_current_page(driver, last_scrape_time=None):
    jobs_data = []
    try:
        job_section = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section > article"))
        ).find_element(By.XPATH, "./..")
    except:
        return jobs_data
    human_sleep(2, 4)
    job_cards = job_section.find_elements(By.XPATH, './article')
    for job in job_cards:
        try:
            title_elem = job.find_element(By.CSS_SELECTOR, 'h2.job-tile-title a')
            title = title_elem.text.strip()
            job_link = title_elem.get_attribute("href")
        except:
            title, job_link = "N/A", "N/A"
        try:
            tags_elements = job.find_elements(By.CSS_SELECTOR, 'div.air3-token-container button')
            tags = ', '.join([tag.text.strip() for tag in tags_elements if tag.text.strip() != ''])
        except:
            tags = "N/A"
        try:
            spent = job.find_element(By.CSS_SELECTOR, 'ul.d-flex.align-items-center.flex-wrap.text-light.gap-wide.text-base-sm.mb-4 li:nth-child(3) > div').text.strip()
        except:
            spent = "N/A"
        try:
            payment = job.find_element(By.CSS_SELECTOR, 'ul.job-tile-info-list.text-base-sm.mb-4 li:nth-child(3)').text.strip()
        except:
            payment = "N/A"
        try:
            payment_verified = job.find_element(By.CSS_SELECTOR, 'ul.d-flex.align-items-center.flex-wrap.text-light.gap-wide.text-base-sm.mb-4 li:nth-child(1) > div').text.strip()
        except:
            payment_verified = "N/A"
        try:
            description = job.find_element(By.CSS_SELECTOR, 'p.mb-0.text-body-sm').text.strip()
        except:
            description = "N/A"
        try:
            posted_text = job.find_element(By.CSS_SELECTOR, 'div.job-tile-header small > span:nth-child(2)').text.strip()
            posted_time = parse_posted_time(posted_text)
        except:
            posted_text = "N/A"
            posted_time = datetime.now()

        
        if last_scrape_time and posted_time <= last_scrape_time:
            continue

        jobs_data.append({
            'Search Query': search_query,
            'Title': title,
            'Job Link': job_link,
            'Tags': tags,
            'Client Spent': spent,
            'Payment Info': payment,
            'Payment Verified/Unverified': payment_verified,
            'Description': description,
            'Posted Time': posted_time.strftime('%Y-%m-%d %H:%M:%S')
        })
        human_sleep(1, 2)
    return jobs_data

# === MAIN ===
options = uc.ChromeOptions()
options.add_argument("--start-maximized")
driver = uc.Chrome(options=options)

login_with_google(driver, GMAIL_EMAIL, GMAIL_PASSWORD)
human_sleep(6, 9)

search_query = "Machine Learning Data Science"
search_url = f"https://www.upwork.com/nx/jobs/search/?q={search_query.replace(' ', '%20')}&sort=recency"
driver.get(search_url)
human_sleep(3, 4)                        #5,7
click_cloudflare_checkbox_pyautogui()



last_scrape_time = read_last_scrape_time(search_query)

all_jobs = extract_jobs_from_current_page(driver, last_scrape_time)

# Page 2
try:
    page2_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR,
            '#main > div.container > div:nth-child(4) > div:nth-child(2) > div.air3-grid-container.jobs-grid-container > div.span-12.span-lg-9 > div.air3-card-section.d-lg-flex.justify-space-between > div:nth-child(2) > div > nav > ul > li:nth-child(6) > button'))
    )
    page2_button.click()
    human_sleep(5, 8)
    slow_scroll(driver)
    all_jobs += extract_jobs_from_current_page(driver, last_scrape_time)
except:
    pass

# Page 3
try:
    page3_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR,
            '#main > div.container > div:nth-child(4) > div:nth-child(2) > div.air3-grid-container.jobs-grid-container > div.span-12.span-lg-9 > div.air3-card-section.d-lg-flex.justify-space-between > div:nth-child(2) > div > nav > ul > li:nth-child(7) > button'))
    )
    page3_button.click()
    human_sleep(5, 8)
    slow_scroll(driver)
    all_jobs += extract_jobs_from_current_page(driver, last_scrape_time)
except:
    pass

# Write result
df = pd.DataFrame(all_jobs)
df_dict = df.to_dict(orient='records')
if not df.empty:
    df.to_csv("upwork_jobs.csv", index=False, encoding='utf-8-sig')


update_scrape_time(search_query)

print(json.dumps(df_dict, ensure_ascii=False))
driver.quit()
