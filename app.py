"""
Claude.ai Automation Script

Purpose:
This script automates interactions with the Claude.ai platform, specifically for logging in
and syncing local files with the cloud-based project.

Key Functionalities:
1. Automated login to Claude.ai using either default or custom Chrome profiles.
2. File change detection in a specified local directory.
3. Synchronization of local files with the Claude.ai project interface.
4. Implementation of anti-detection measures to mimic human-like browsing behavior.

Technical Overview:
- Uses undetected_chromedriver for browser automation to avoid detection.
- Implements randomized delays and user-agent spoofing for a more human-like interaction.
- Utilizes Selenium WebDriver for web element interactions.

Usage:
1. Ensure all required libraries are installed.
2. Run the script and follow the prompts for login and directory selection.
3. The script will monitor the specified directory and sync changes to Claude.ai.

Note: This script is provided as-is and should be used at your own risk. Always ensure you
have permission to automate interactions with web services.
"""

# Rest of your Python code starts here



import os
import time
import random
import subprocess
import psutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from fake_useragent import UserAgent


from selenium.common.exceptions import SessionNotCreatedException
import os
import time
import random
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
from fake_useragent import UserAgent
from selenium.common.exceptions import WebDriverException, TimeoutException
import re
import psutil

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, driver, local_dir):
        self.driver = driver
        self.local_dir = local_dir

    def on_modified(self, event):
        if not event.is_directory:
            file_name = os.path.basename(event.src_path)
            if not self.is_temp_file(file_name):
                print(f"File {file_name} has been modified")
                self.sync_file(file_name)

    def is_temp_file(self, file_name):
        # Filter out temporary and hidden files
        return file_name.startswith('.') or file_name.endswith('.swp') or file_name.endswith('.tmp')

    def sync_file(self, file_name):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if not self.is_browser_alive():
                    print("Browser session is not responsive. Restarting...")
                    self.restart_browser()

                self.delete_existing_file(file_name)
                self.upload_new_file(file_name)
                break
            except Exception as e:
                print(f"Error syncing file {file_name} (Attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt == max_retries - 1:
                    print(f"Failed to sync file {file_name} after {max_retries} attempts.")
                else:
                    time.sleep(5)  # Wait before retrying

    def is_browser_alive(self):
        try:
            self.driver.title  # This will throw an exception if the browser is not responsive
            return True
        except:
            return False

    def restart_browser(self):
        self.driver.quit()
        self.driver = create_driver(use_default_profile=True)
        self.driver.get("https://claude.ai/project/b4d5521b-5402-4be5-b7ad-70feccbfcd6b")
        # You might need to re-implement login logic here

    def delete_existing_file(self, file_name):
        try:
            file_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//div[contains(text(), '{file_name}')]"))
            )
            delete_button = file_element.find_element(By.XPATH, ".//button[contains(@class, 'delete')]")
            delete_button.click()
            print(f"Deleted existing file: {file_name}")
        except Exception as e:
            print(f"Error deleting file {file_name}: {str(e)}")

    def upload_new_file(self, file_name):
        try:
            add_content_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add Content')]"))
            )
            add_content_button.click()

            upload_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Upload from device')]"))
            )
            upload_button.click()

            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
            )
            file_path = os.path.join(self.local_dir, file_name)
            file_input.send_keys(file_path)

            print(f"Uploaded new file: {file_name}")
        except Exception as e:
            print(f"Error uploading file {file_name}: {str(e)}")
            raise



def kill_chrome_processes():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'chrome':
            proc.kill()

def create_driver(use_default_profile=False, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            kill_chrome_processes()  # Kill any existing Chrome processes

            options = uc.ChromeOptions()
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-extensions")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-browser-side-navigation")
            options.add_argument("--disable-gpu")

            # Randomize user agent
            ua = UserAgent()
            user_agent = ua.random
            options.add_argument(f'user-agent={user_agent}')

            if use_default_profile:
                options.add_argument(f"user-data-dir={os.path.expanduser('~/.config/google-chrome')}")
            else:
                user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
                options.add_argument(f"user-data-dir={user_data_dir}")

            chrome_version = get_chrome_version()
            print(f"Detected Chrome version: {chrome_version}")

            # Use webdriver_manager to get the correct ChromeDriver
            driver_path = ChromeDriverManager(version=chrome_version).install()
            service = Service(driver_path)

            driver = webdriver.Chrome(service=service, options=options)

            # Test if the driver is working
            driver.get("https://www.google.com")
            print("Successfully connected to Google")

            return driver
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_attempts - 1:
                raise Exception(f"Failed to create Chrome driver after {max_attempts} attempts")
            time.sleep(5)  # Wait before next attempt




def random_delay(min_delay=1, max_delay=5):
    time.sleep(random.uniform(min_delay, max_delay))

def human_like_mouse_move(driver, element):
    action = ActionChains(driver)
    action.move_to_element_with_offset(element, 1, 1)
    action.move_by_offset(random.randint(10, 50), random.randint(10, 50))
    action.move_to_element(element)
    action.perform()
    random_delay(0.5, 2)

def get_chrome_version():
    try:
        # This works on most Linux systems
        version = subprocess.check_output(['google-chrome', '--version']).decode().strip().split()[-1]
        return version
    except:
        return None



def is_logged_in(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Add Content')]"))
        )
        return True
    except:
        return False
def login(driver, username, password):
    try:
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='email']"))
        )
        human_like_mouse_move(driver, email_input)
        email_input.send_keys(username)
        random_delay()

        continue_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Continue with email')]")
        human_like_mouse_move(driver, continue_button)
        continue_button.click()
        random_delay()

        # Add steps for password input and final login button click
        # This will depend on the exact structure of the Claude.ai login process

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Add Content')]"))
        )
        print("Login successful")
    except Exception as e:
        print(f"Login failed: {str(e)}")
        raise



def main():
    local_dir = "/home/hemang/Downloads/notebook_scripts/claude_project_sync/tests"
    url = "https://claude.ai/project/b4d5521b-5402-4be5-b7ad-70feccbfcd6b"

    use_default_profile = True

    try:
        driver = create_driver(use_default_profile)
        driver.get(url)

        if not is_logged_in(driver):
            username = input("Enter your email: ")
            password = input("Enter your password: ")
            login(driver, username, password)

        # Set up the file system event handler
        event_handler = FileChangeHandler(driver, local_dir)
        observer = Observer()
        observer.schedule(event_handler, local_dir, recursive=False)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    main()






















