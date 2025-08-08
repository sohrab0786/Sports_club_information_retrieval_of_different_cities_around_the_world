import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup

# ------------------------------
# Configuration
# ------------------------------
driver_path = "C:/Users/sohra/Downloads/chatbot_filing_13_02_2025/webscrapping_data_for_link_ticker_compName/chromedriver-win64/chromedriver.exe"  # Update as needed
url = "https://www.tradingview.com/screener/"  # Replace with the actual URL
excel_file = "extracted_ticker_data.xlsx"

# ------------------------------
# Setup Selenium WebDriver in headless mode (change/remove headless option if you want the browser visible)
# ------------------------------
chrome_options = Options()
chrome_options.add_argument("--headless")  # Remove this line if you want Chrome to open visibly
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)


# ✅ Open Playo website
url = "https://playo.co/venues/bangalore/sports/all"
driver.get(url)

# ✅ Scroll down to load more cards
def scroll_down():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# ✅ Extract text safely
def get_text(element):
    return element.text.strip() if element else "N/A"

# ✅ Extract sport complex cards
def get_sport_complex_cards():
    scroll_down()  # Ensure all venues load
    return driver.find_elements(By.XPATH, "//div[contains(@class, 'border_radius') and contains(@class, 'card_shadow')]")

# ✅ Store extracted data
data_list = []

# ✅ Click on each card and extract details
def scrape_sports_complex():
    cards = get_sport_complex_cards()

    if not cards:
        print("⚠ No sports complex cards found! Exiting...")
        return

    for i in range(min(10, len(cards))):  # Process up to 10 cards
        try:
            cards = get_sport_complex_cards()  # Refresh elements
            venue = cards[i]
            driver.execute_script("arguments[0].scrollIntoView();", venue)
            driver.execute_script("arguments[0].click();", venue)

            # ✅ Wait for venue details page
            wait.until(EC.presence_of_element_located((By.XPATH, "//h1[contains(@class, 'text-[24px]')]")))

            # ✅ Extract Data
            name = get_text(driver.find_element(By.XPATH, "//h1[contains(@class, 'text-[24px]')]"))
            location = get_text(driver.find_element(By.XPATH, "//span[contains(@class, 'text-md')]"))
            exact_location = get_text(driver.find_element(By.XPATH, "//p[contains(@class, 'my-2')]"))
            timing_label = get_text(driver.find_element(By.XPATH, "//h2[contains(text(), 'Timing')]"))
            timing = get_text(driver.find_element(By.XPATH, "//p[contains(@class, 'leading-1')]"))
            about_label = get_text(driver.find_element(By.XPATH, "//h2[contains(text(), 'About Venue')]"))
            about_venue = get_text(driver.find_element(By.XPATH, "//p[contains(@class, 'text-sm')]"))

            # ✅ Extract Price, Amenities, Sports
            try:
                price = get_text(driver.find_element(By.XPATH, "//span[contains(@class, 'text-xl')]"))
            except:
                price = "N/A"

            try:
                amenities = [elem.text for elem in driver.find_elements(By.XPATH, "//span[contains(@class, 'text-sm')]")]
                amenities = ", ".join(amenities) if amenities else "N/A"
            except:
                amenities = "N/A"

            try:
                sports = [elem.text for elem in driver.find_elements(By.XPATH, "//span[contains(@class, 'text-md')]")]
                sports = ", ".join(sports) if sports else "N/A"
            except:
                sports = "N/A"

            # ✅ Save data
            data_list.append({
                "Name": name,
                "Location": location,
                "Exact Location": exact_location,
                "Timing": timing if "Timing" in timing_label else "N/A",
                "About Venue": about_venue if "About Venue" in about_label else "N/A",
                "Price": price,
                "Amenities": amenities,
                "Sports": sports
            })

            # ✅ Go back to the main page
            driver.back()
            wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'border_radius') and contains(@class, 'card_shadow')]")))

        except Exception as e:
            print(f"⚠ Error scraping card {i+1}: {e}")
            driver.back()
            continue

# ✅ Run scraper
scrape_sports_complex()

# ✅ Convert to DataFrame and save
df = pd.DataFrame(data_list)
file_path = "playo_sports.xlsx"
df.to_excel(file_path, index=False)

# ✅ Close WebDriver
driver.quit()

print(f"✅ Data scraping completed! Excel file saved as {file_path}")
