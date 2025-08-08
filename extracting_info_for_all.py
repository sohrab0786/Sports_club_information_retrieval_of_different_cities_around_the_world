import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException

# Set up Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver_path = "C:/Windows/chromedriver.exe"  
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 10)

# Base URL
#https://playo.co/venues/delhi-ncr/sports/all
#https://playo.co/venues/chennai/sports/all
#https://playo.co/venues/hyderabad/sports/all
#https://playo.co/venues/pune/sports/all
#https://playo.co/venues/vijayawada/sports/all
#https://playo.co/venues/mumbai/sports/all
#https://playo.co/venues/Visakhapatnam/sports/all
#https://playo.co/venues/guntur/sports/all
#https://playo.co/venues/Kochi/sports/all
#https://playo.co/venues/bangalore/sports/all
#https://playo.co/venues/delhi/sports/all
url = "https://playo.co/venues/mumbai/sports/all"
driver.get(url)

# Store extracted data
venues_data = []
visited_boxes = set()  # Track visited venue boxes

def extract_venue_details():
    """Extract venue details after clicking a box."""
    try:
        time.sleep(3)  # Allow page to load
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Venue Name
        venue_name = None
        try:
            name_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            venue_name = name_element.text.strip()
        except:
            print("Venue name not found.")

        # Venue Timing
        venue_timing = None
        try:
            timing_element = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//h2[contains(text(),'Timing')]/following-sibling::div")))
            venue_timing = timing_element.text.strip()
        except:
            print("Timing not found.")

        # Venue Location
        venue_location = None
        try:
            location_element = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[contains(text(),'Location')]/following-sibling::h2")))
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

        # Extract "About Venue" section
        about_venue = ""
        about_venue_section = soup.find("div", class_="font-semibold text-md", string="About Venue")
        if about_venue_section:
            about_venue_container = about_venue_section.find_next("h3")
            if about_venue_container:
                about_venue = about_venue_container.get_text(separator="\n", strip=True)
        # Extract Sports Available
        sports_available = []
        sports_section = soup.find("h2", string="Sports Available")

        if sports_section:
            sports_container = sports_section.find_next("div", class_="grid")
            if sports_container:
                sports_available = [h3.text.strip() for h3 in sports_container.find_all("h3")]


        # Get final URL
        final_url = driver.current_url

        # Store data
        venue_data = {
        "Venue Name": venue_name,
        "Timing": venue_timing,
        "Location": venue_location,
        "URL": final_url,
        "Amenities": amenities,
        "About Venue": about_venue,
        "Sports Available": sports_available  # ✅ New field
    }

        venues_data.append(venue_data)
        print(json.dumps(venue_data, indent=4))

    except Exception as e:
        print("Error extracting venue details:", e)

def process_all_venues():
    """Extract data from all venue boxes and load more if needed."""
    original_window = driver.current_window_handle

    while True:
        venue_boxes = driver.find_elements(By.CLASS_NAME, 
            "border_radius.bg-white.card_shadow.pb-2.cursor-pointer.transition.duration-200.transform.hover\\:scale-\\[1\\.02\\]")

        new_boxes_found = False  # Flag to track if we found new boxes

        for idx, box in enumerate(venue_boxes):
            if idx in visited_boxes:  # Skip already visited venues
                continue  

            new_boxes_found = True  # At least one new box was found

            try:
                driver.execute_script("arguments[0].scrollIntoView();", box)
                time.sleep(1)  # Allow UI to adjust
                box.click()
                print("✅ Clicked venue box. Extracting details...")

                time.sleep(3)  # Allow new page to load

                # Check if new tab opened and switch
                if len(driver.window_handles) > 1:
                    for handle in driver.window_handles:
                        if handle != original_window:
                            driver.switch_to.window(handle)
                            break

                extract_venue_details()

                # Return to the main page
                driver.close()
                driver.switch_to.window(original_window)
                visited_boxes.add(idx)  # Mark as visited
                print("🔙 Returned to main page.")

            except Exception as e:
                print(f"⚠️ Error processing venue box: {e}")
                continue

        # If no new venues were found, try clicking "Show More"
        if not new_boxes_found:
            try:
                show_more_button = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//button[contains(text(),'Show More')]")))

                if show_more_button.is_displayed():
                    driver.execute_script("arguments[0].scrollIntoView();", show_more_button)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", show_more_button)
                    print("✅ Clicked 'Show More'. Loading more venues...")
                    time.sleep(5)  # Allow new venues to load
                    continue  # Restart loop with new venues
                else:
                    print("🚫 'Show More' button is not clickable.")
                    break

            except TimeoutException:
                print("🚫 No 'Show More' button found. All venues processed.")
                break
            except Exception as e:
                print(f"⚠️ Error clicking 'Show More': {e}")
                break

    # Save extracted data
    with open("venues_data.json", "w", encoding="utf-8") as f:
        json.dump(venues_data, f, ensure_ascii=False, indent=4)
    print("✅ Data saved to venues_data.json")

# Start the scraping process
process_all_venues()

# Quit the driver
driver.quit()
