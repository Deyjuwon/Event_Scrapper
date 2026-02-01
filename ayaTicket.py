import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# -----------------------------
# Setup Chrome
# -----------------------------
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, 10)
all_events = []
page_number = 1

while True:
    url = f"https://ayatickets.com/en/events?page={page_number}"
    print(f"\n📄 Visiting page {page_number}: {url}")
    driver.get(url)
    time.sleep(3)

    # ------------------------------------
    # Get all event links (a > div.aya-ev2-media)
    # ------------------------------------
    event_links = driver.find_elements(
        By.XPATH,
        "//a[.//div[contains(@class,'aya-ev2-media')]]"
    )

    if not event_links:
        print("❌ No events found. Stopping.")
        break

    print(f"🔎 Found {len(event_links)} events")

    for index in range(len(event_links)):
        try:
            # Re-fetch links (DOM reload safety)
            event_links = driver.find_elements(
                By.XPATH,
                "//a[.//div[contains(@class,'aya-ev2-media')]]"
            )

            event_url = event_links[index].get_attribute("href")
            print(f"\n➡️ Opening event {index + 1}: {event_url}")
            driver.get(event_url)
            time.sleep(3)

            # -----------------------------
            # Extract Event Name
            # -----------------------------
            try:
                name = wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "h1"))
                ).text.strip()
            except:
                name = ""

            # -----------------------------
            # Extract Location
            # -----------------------------
            try:
                location = driver.find_element(
                    By.XPATH,
                    "//span[contains(@class,'location') or contains(text(),'Location')]/following-sibling::*"
                ).text.strip()
            except:
                location = ""

            # -----------------------------
            # Extract Price
            # -----------------------------
            try:
                price = driver.find_element(
                    By.XPATH,
                    "//span[contains(@class,'price') or contains(text(),'₦') or contains(text(),'Free')]"
                ).text.strip()
            except:
                price = ""

            # -----------------------------
            # Extract Host / Organizer
            # -----------------------------
            try:
                host = driver.find_element(
                    By.XPATH,
                    "//span[contains(@class,'organizer') or contains(@class,'host') or contains(text(),'By')]"
                ).text.strip()
            except:
                host = ""

            # -----------------------------
            # Extract Date & Time
            # -----------------------------
            try:
                date_time_text = driver.find_element(
                    By.XPATH,
                    "//div[contains(@class,'date') or contains(@class,'time')]"
                ).text.strip()

                if " at " in date_time_text:
                    date, time_ = date_time_text.split(" at ", 1)
                elif "," in date_time_text:
                    date, time_ = date_time_text.rsplit(",", 1)
                else:
                    date = date_time_text
                    time_ = ""
            except:
                date = ""
                time_ = ""

            event_data = {
                "Event Name": name,
                "Location": location,
                "Price": price,
                "Host": host,
                "Date": date.strip(),
                "Time": time_.strip()
            }

            all_events.append(event_data)

            print("✅ Extracted:")
            for k, v in event_data.items():
                print(f"   {k}: {v}")

            # Go back to listing page
            driver.back()
            time.sleep(2)

        except Exception as e:
            print(f"❌ Failed on event {index + 1}: {e}")
            driver.back()
            time.sleep(2)
            continue

    page_number += 1
    time.sleep(2)

# -----------------------------
# Save to CSV
# -----------------------------
with open("ayatickets_events.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["Event Name", "Location", "Price", "Host", "Date", "Time"]
    )
    writer.writeheader()
    writer.writerows(all_events)

print(f"\n✅ Done. Scraped {len(all_events)} events total.")
driver.quit()
