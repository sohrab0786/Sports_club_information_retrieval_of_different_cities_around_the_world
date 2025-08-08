import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
# Set up Selenium WebDriver
chrome_options = Options()
#chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver_path = "C:/Users/sohra/Downloads/AIToXR_Projects/chatbot_filing_13_02_2025/webscrapping_data_for_link_ticker_compName/chromedriver-win64/chromedriver.exe"  # Update as needed

service = Service(driver_path)  # Ensure ChromeDriver is in PATH
driver = webdriver.Chrome(service=service, options=chrome_options)

# Base URL
url = "https://playo.co/venues/bangalore/sports/all"
driver.get(url)
wait = WebDriverWait(driver, 10)
# Extract the full HTML content

import time
import json

try:
    wait = WebDriverWait(driver, 10)

    # Store the original window handle
    original_window = driver.current_window_handle

    # Click the venue box
    box = wait.until(EC.element_to_be_clickable(
        (By.CLASS_NAME, "border_radius.bg-white.card_shadow.pb-2.cursor-pointer.transition.duration-200.transform.hover\\:scale-\\[1\\.02\\]"))
    )
    box.click()
    print("Box clicked. Waiting for venue details page to load...")

    # Wait for new tab or page load
    time.sleep(5)  # Give time for page navigation

    # Check if a new tab was opened and switch to it
    if len(driver.window_handles) > 1:
        for handle in driver.window_handles:
            if handle != original_window:
                driver.switch_to.window(handle)
                break
    else:
        print("No new tab detected. Waiting for AJAX load.")

    # Ensure venue details are loaded by waiting for a unique element
    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
    except:
        print("New page content did not load properly.")

    # Extract Venue Name from the new page
    try:
        time.sleep(3)  # Ensure JavaScript loads content
        name_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        venue_name = name_element.text.strip()
    except:
        venue_name = None
    soup = BeautifulSoup(driver.page_source, "html.parser")
    # Extract Venue Timing
    venue_timing = None
    try:
        timing_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//h2[contains(text(),'Timing')]/following-sibling::div")
        ))
        venue_timing = timing_element.text.strip()
    except:
        print("Timing not found.")

    # Extract Venue Location
    venue_location = None
    try:
        location_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[contains(text(),'Location')]/following-sibling::h2")
        ))
        venue_location = location_element.text.strip()
    except:
        print("Location not found.")
    # Extract Amenities
    amenities = []
    amenities_section = soup.find("h3", string="Amenities")
    if amenities_section:
      amenities_container = amenities_section.find_next("div", class_="grid")
      if amenities_container:
        amenities = [h4.text.strip() for h4 in amenities_container.find_all("h4")]

    print("Extracted Amenities:", amenities)
    # Extract "About Venue" section
    about_venue = ""
    about_venue_section = soup.find("div", class_="font-semibold text-md", string="About Venue")
    if about_venue_section:
        about_venue_container = about_venue_section.find_next("h3")
        if about_venue_container:
            about_venue = about_venue_container.get_text(separator="\n", strip=True)

    print("Extracted About Venue:", about_venue)

    print("Extracted About Venue:", about_venue)
    # Get final page URL
    final_url = driver.current_url

    # Store data in JSON format
    venue_data = {
        "Venue Name": venue_name,
        "Timing": venue_timing,
        "Location": venue_location,
        "URL": final_url,
        "Amenities": amenities,
        "About Venue": about_venue
    }

    # Print JSON output
    print(json.dumps(venue_data, indent=4))

    # **Step: Return to the Main Page**
    if len(driver.window_handles) > 1:
        driver.close()  # Close the venue details tab
        driver.switch_to.window(original_window)  # Switch back to main page
    else:
        driver.back()  # If same tab navigation, use browser back

    print("Returned to the main page.")

except Exception as e:
    print("Error:", e)

finally:
    driver.quit()