import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Setup Chrome with webdriver-manager
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

events_data = []

# Loop through pages
for page_number in range(1, 13):
    url = f"https://egotickets.com/events"
    driver.get(url)
    print(f"\n🌐 Scraping Page {page_number}: {url}")
    time.sleep(5)

    # Get all event cards
    try:
        event_cards = driver.find_elements(By.CLASS_NAME, "ego-border-rounded")
        print(f"🔎 Found {len(event_cards)} events on page {page_number}")
    except Exception as e:
        print(f"❌ Failed to get events on page {page_number}: {e}")
        continue

    for index in range(len(event_cards)):
        try:
            # Re-fetch cards each time due to DOM refresh after back
            event_cards = driver.find_elements(By.CLASS_NAME, "ego-border-rounded")
            event = event_cards[index]

            driver.execute_script("arguments[0].scrollIntoView();", event)
            time.sleep(1)
            event.click()
            print(f"\n🔍 Opened Event {index + 1} on Page {page_number}")
            time.sleep(5)

            # Extract details
            try:
                name = driver.find_element(By.CSS_SELECTOR, "h1.display-one.uk-margin-remove-bottom.uk-margin-remove-top").text
            except:
                name = ""

            try:
                organizer = driver.find_element(By.CSS_SELECTOR, "p.uk-margin-remove-bottom.uk-margin-remove-top.uk-width-4-5\\@s").text
            except:
                organizer = ""

            try:
                raw_date_time = driver.find_element(By.CSS_SELECTOR, "h3.uk-flex.uk-flex-row.uk-flex-middle").text
                if '.' in raw_date_time:
                    parts = raw_date_time.split('.')
                    date = parts[0].strip()
                    time_range = parts[1].strip()
                else:
                    date = raw_date_time.strip()
                    time_range = ""
            except:
                date = ""
                time_range = ""

            try:
                location = driver.find_element(By.CSS_SELECTOR, "h3.uk-flex.uk-flex-row.uk-flex-middle a").text
            except:
                location = ""

            try:
                email_links = driver.find_elements(By.CSS_SELECTOR, "a.uk-link")
                email = ""
                for link in email_links:
                    href = link.get_attribute("href")
                    if href and "mailto:" in href:
                        email = href.replace("mailto:", "").strip()
                        break
            except:
                email = ""

            try:
                price = driver.find_element(By.CSS_SELECTOR, "span.uk-text-bold.uk-display-block.ego-orange-text").text
            except:
                price = ""

            event_info = {
                "name": name,
                "organizer": organizer,
                "date": date,
                "time": time_range,
                "location": location,
                "email": email,
                "price": price
            }

            print("✅ Extracted:", event_info)
            events_data.append(event_info)

            # Go back
            driver.back()
            time.sleep(3)
        except Exception as e:
            print(f"❌ Error scraping event {index + 1} on Page {page_number}: {e}")
            continue

# Save to CSV
with open("events.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["name", "organizer", "date", "time", "location", "email", "price"])
    writer.writeheader()
    writer.writerows(events_data)

print("\n📁 Scraping complete. Data saved to events.csv")
driver.quit()