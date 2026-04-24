import os
import shutil
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
import subprocess
import re

# --- CONFIGURATION ---
EMAIL = os.environ.get("NAUKRI_EMAIL")
PASSWORD = os.environ.get("NAUKRI_PASSWORD")
COOKIES_STR = os.environ.get("NAUKRI_COOKIES")
SOURCE_RESUME = "Resume.pdf"  # As provided in the repository

if not COOKIES_STR and (not EMAIL or not PASSWORD):
    print("Error: Provide either NAUKRI_COOKIES or NAUKRI_EMAIL/NAUKRI_PASSWORD in secrets.")
    sys.exit(1)

if not os.path.exists(SOURCE_RESUME):
    print(f"Error: {SOURCE_RESUME} not found in the current directory.")
    sys.exit(1)

# --- DYNAMIC RENAMING ---
# Generate today's date in YYYYMMDD format
today_date = datetime.now().strftime("%Y%m%d")
new_resume_name = f"resume_{today_date}.pdf"

# Create a copy with the new name
shutil.copy(SOURCE_RESUME, new_resume_name)
target_resume_path = os.path.abspath(new_resume_name)
print(f"[INFO] Created renamed resume: {target_resume_path}")

# --- WEB AUTOMATION ---
options = uc.ChromeOptions()
# options.add_argument('--headless') # Removing headless to bypass Akamai on Windows runner
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')

print("[INFO] Starting Chrome browser...")

def get_chrome_version():
    try:
        # On Windows, we can use powershell to get Chrome version
        if sys.platform == 'win32':
            output = subprocess.check_output(
                ['powershell', '-command', "(Get-Item (Get-ItemProperty 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\chrome.exe').'(Default)').VersionInfo.ProductVersion"],
                text=True
            )
            match = re.search(r'^(\d+)', output.strip())
        else:
            output = subprocess.check_output(['google-chrome', '--version']).decode()
            match = re.search(r'Google Chrome (\d+)', output)
        if match:
            return int(match.group(1))
    except Exception as e:
        print(f"Version detection error: {e}")
    return None

chrome_version = get_chrome_version()
print(f"[INFO] Detected Chrome major version: {chrome_version}")

if chrome_version:
    driver = uc.Chrome(options=options, version_main=chrome_version)
else:
    driver = uc.Chrome(options=options)
    
wait = WebDriverWait(driver, 30)

try:
    # 1. Login
    if COOKIES_STR:
        import json
        print("[INFO] NAUKRI_COOKIES found! Using session cookies to bypass login...")
        driver.get("https://www.naukri.com/")
        time.sleep(3)
        try:
            cookies = json.loads(COOKIES_STR)
            for cookie in cookies:
                # Selenium requires domain to match
                if 'domain' in cookie:
                    # Strip leading dot if necessary, though selenium usually handles it
                    pass
                driver.add_cookie(cookie)
            print("[INFO] Cookies injected successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to parse or inject cookies: {e}")
    else:
        print("[INFO] Navigating to login page...")
        driver.get("https://www.naukri.com/nlogin/login")
        time.sleep(5)
        
        print(f"[INFO] Current Page Title: {driver.title}")
        print(f"[INFO] Current URL: {driver.current_url}")
        
        try:
            wait.until(EC.visibility_of_element_located((By.ID, "usernameField"))).send_keys(EMAIL)
            driver.find_element(By.ID, "passwordField").send_keys(PASSWORD)
            driver.find_element(By.XPATH, "//button[contains(@class,'loginButton') or @type='submit']").click()
        except Exception as e:
            print("[ERROR] Failed to find login fields. Dumping page source snippet:")
            print(driver.page_source[:2000])
            raise e
            
        print("[INFO] Logging in...")
        time.sleep(10) # Wait for login to process (handles AJAX or slow redirects)
        print(f"[INFO] URL after login attempt: {driver.current_url}")
    
    # 2. Navigate to Profile
    print("[INFO] Navigating to profile page...")
    driver.get("https://www.naukri.com/mnjuser/profile")
    time.sleep(5)  # Wait for full profile load
    
    if "login" in driver.current_url:
        print("[ERROR] Still on login page! Login failed. Possible reasons: Incorrect credentials, CAPTCHA, or OTP required.")
        print(f"[INFO] Page Title: {driver.title}")
        print(f"[INFO] Source Snippet: {driver.page_source[:2000]}")
        raise Exception("Login failed, redirected back to login.")
    else:
        print("[INFO] Login successful. On profile page.")
    
    # 3. Delete existing resume (if present)
    print("[INFO] Checking for existing resume...")
    try:
        delete_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(@class,'delete') and ancestor::*[contains(@class,'resume')]]")
        ))
        delete_btn.click()
        print("[INFO] Clicked delete button.")
        
        # Confirm deletion if prompted
        try:
            confirm_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(),'Delete') or contains(text(),'Yes') or contains(text(),'Confirm')]")
            ))
            confirm_btn.click()
            print("[INFO] Confirmed deletion.")
        except:
            print("[INFO] No confirmation popup found.")
            
        time.sleep(3) # Wait for deletion to process
    except Exception as e:
        print("[WARN] No existing resume found to delete, or delete button structure changed. Proceeding to upload.")
    
    # 4. Upload new dynamically named resume
    print(f"[INFO] Uploading new resume: {new_resume_name}")
    file_input = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//input[@type='file']")
    ))
    
    # Unhide input if necessary and send file
    driver.execute_script("arguments[0].style.display = 'block';", file_input)
    file_input.send_keys(target_resume_path)
    
    # Verify Success
    try:
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(),'successfully') or contains(text(),'uploaded') or contains(text(),'Updated')]")
        ))
        print("[SUCCESS] Resume uploaded successfully!")
    except:
        print("[WARN] Upload finished, but could not detect success message.")

finally:
    print("[INFO] Closing browser...")
    driver.quit()
    
    # Clean up the dynamically named file
    if os.path.exists(target_resume_path):
        os.remove(target_resume_path)
        print("[INFO] Cleaned up temporary resume file.")
