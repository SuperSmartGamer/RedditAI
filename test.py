import os
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

# Function for human-like typing
def human_typing(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.5))  # Simulate typing with random delays

# Setting up the Edge options
options = Options()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
options.add_argument("--disable-blink-features=AutomationControlled")  # Hide automation flags
options.add_argument("--incognito")  # Use incognito mode to avoid tracking
options.add_argument("--no-sandbox")  # To avoid potential sandbox issues
options.add_argument("--disable-dev-shm-usage")  # Fix some memory issues
# options.add_argument('--headless')  # Use if you need headless mode, but make sure it's not flagged
options.add_argument("--start-maximized")  # Start browser in maximized state
# options.add_argument('--proxy-server=http://your.proxy.address:port')  # Uncomment to use a proxy

# Use an existing user profile to make the browser appear more legitimate
options.add_argument(r"user-data-dir=C:\path\to\your\user\profile")  # Use a valid path for your user profile

# Initialize the Edge service
service = Service(r'C:\Program Files\edgedriver_win32\msedgedriver.exe')

# Start the Edge browser with the configured options
driver = webdriver.Edge(service=service, options=options)

# Get credentials from environment variables
email = os.getenv('YT_Username')  # Replace with your environment variable name
password = os.getenv('YT_Password')  # Replace with your environment variable name

# Open the Google login page
driver.get('https://accounts.google.com/ServiceLogin')

# 1. Enter email address with human-like typing
email_field = driver.find_element(By.ID, 'identifierId')
human_typing(email_field, email)  # Simulate typing each letter with delay
email_field.send_keys(Keys.RETURN)
time.sleep(random.uniform(2, 4))  # Random delay after pressing enter

# 2. Enter password with human-like typing
password_field = driver.find_element(By.NAME, 'password')
human_typing(password_field, password)  # Simulate typing password with delay
password_field.send_keys(Keys.RETURN)
time.sleep(random.uniform(3, 5))  # Random delay after pressing enter

# 3. Handle account selection (if multiple accounts exist)
try:
    account_selector = driver.find_element(By.XPATH, "//div[@class='KxwPGc']")
    account_selector.click()
    time.sleep(random.uniform(2, 4))  # Random delay after selecting the account
except Exception as e:
    print("No account selection required, or error occurred: ", e)

# 4. Open YouTube upload page
driver.get('https://www.youtube.com/upload')
time.sleep(random.uniform(3, 5))  # Random delay after opening the upload page

# 5. Upload the video
video_path = r'C:\path\to\your_video.mp4'  # Replace with the actual path to your video
driver.find_element(By.XPATH, '//input[@type="file"]').send_keys(video_path)
time.sleep(random.uniform(3, 5))  # Random delay while uploading

# 6. Fill in the video title with human-like typing
title_field = driver.find_element(By.NAME, 'title')
human_typing(title_field, 'Your Video Title')  # Replace with your desired title
time.sleep(random.uniform(1, 2))  # Random delay after typing the title

# 7. Fill in the video description with human-like typing
description_field = driver.find_element(By.NAME, 'description')
human_typing(description_field, 'Your video description')  # Replace with your desired description
time.sleep(random.uniform(1, 2))  # Random delay after typing the description

# 8. Submit the video
next_button = driver.find_element(By.XPATH, '//ytcp-button[@id="next-button"]')
next_button.click()
time.sleep(random.uniform(3, 5))  # Random delay after clicking the button

# 9. Wait for the upload to complete (adjust the time based on video size)
time.sleep(random.uniform(60, 120))  # Adjust time based on video size or add additional logic here

# 10. Close the browser
driver.quit()
