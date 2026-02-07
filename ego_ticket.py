import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# -------------------------------------------------
# Browser setup
# -------------------------------------------------
options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, 15)

# -------------------------------------------------
# Open events page
# -------------------------------------------------
URL = "https://egotickets.com/events?country=gh"
driver.get(URL)
print("🌐 Opened Ghana events page")

wait.until(EC.presence_of_element_located((By.ID, "events-grid")))
time.sleep(3)

# -------------------------------------------------
# Load more events (7 times)
# -------------------------------------------------
LOAD_MORE_XPATH = '//*[@id="pagination"]/div/a/span'

for i in range(7):
    try:
        print(f"⬇️ Loading more events ({i + 1}/7)")
        load_more = wait.until(
            EC.element_to_be_clickable((By.XPATH, LOAD_MORE_XPATH))
        )
        driver.execute_script("arguments[0].click();", load_more)
        time.sleep(10)
    except:
        print("⚠️ No more events to load")
        break

# -------------------------------------------------
# XPaths & constants
# -------------------------------------------------
EVENT_NAME_XPATHS = [
    '//*[@id="main-content"]/div/div[1]/div[3]/div/div/div[1]/div[3]/h1',
    '//*[@id="main-content"]/div/div[1]/div[3]/div/div/div/div[2]/h1'
]

LOCATION_A_XPATHS = [
    '//*[@id="main-content"]/div/div[1]/div[3]/div/div/div[1]/div[4]/a',
    '//*[@id="main-content"]/div/div[1]/div[3]/div/div/div/div[3]/a'
]

EMAIL_XPATH = (
    '//*[@id="main-content"]/div/div[2]/div/div/div[1]'
    '/section[2]/div/div[2]/a[2]'
)

CTA_KEYWORDS = ["get ticket", "buy", "register", "rsvp"]
WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def extract_event_name(driver):
    for xpath in EVENT_NAME_XPATHS:
        try:
            return WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            ).text.strip()
        except TimeoutException:
            continue
    return ""

def extract_location(driver):
    for xpath in LOCATION_A_XPATHS:
        a_tags = driver.find_elements(By.XPATH, xpath)
        for a in a_tags:
            try:
                span = a.find_element(By.TAG_NAME, "span")
                text = span.text.strip()

                if not text:
                    continue
                if any(word in text.lower() for word in CTA_KEYWORDS):
                    continue

                return text
            except:
                continue
    return ""

def extract_date_time(driver):
    spans = driver.find_elements(By.TAG_NAME, "span")
    for span in spans:
        text = span.text.strip()
        if text.startswith(WEEKDAYS):
            return text
    return ""

def extract_phone(driver):
    phone_links = driver.find_elements(
        By.XPATH, "//a[starts-with(@href, 'tel:')]"
    )
    for link in phone_links:
        href = link.get_attribute("href")
        if href:
            return href.replace("tel:", "").strip()
    return ""

def extract_email(driver):
    try:
        email_link = driver.find_element(By.XPATH, EMAIL_XPATH)
        href = email_link.get_attribute("href")
        if href and href.startswith("mailto:"):
            return href.replace("mailto:", "").strip()
    except:
        pass
    return ""

# -------------------------------------------------
# Scrape all loaded events
# -------------------------------------------------
events_data = []

event_cards = driver.find_elements(By.XPATH, '//*[@id="events-grid"]/a')
total_events = len(event_cards)

print(f"📦 Total events loaded: {total_events}")

for i in range(1, total_events + 1):
    try:
        print(f"🔍 Scraping event {i}/{total_events}")

        card_xpath = f'//*[@id="events-grid"]/a[{i}]/div[1]'
        card = wait.until(
            EC.presence_of_element_located((By.XPATH, card_xpath))
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            card
        )
        time.sleep(1)
        driver.execute_script("arguments[0].click();", card)

        event_data = {
            "event_name": extract_event_name(driver),
            "location": extract_location(driver),
            "date_time": extract_date_time(driver),
            "phone": extract_phone(driver),
            "email": extract_email(driver),
        }

        events_data.append(event_data)

        time.sleep(2)
        driver.back()
        wait.until(EC.presence_of_element_located((By.ID, "events-grid")))
        time.sleep(2)

    except Exception as e:
        print(f"❌ Failed on event {i}: {e}")

# -------------------------------------------------
# Save to CSV
# -------------------------------------------------
CSV_FILE = "egotickets_ghana_events.csv"

with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["event_name", "location", "date_time", "phone", "email"]
    )
    writer.writeheader()
    writer.writerows(events_data)

print(f"\n📁 Saved {len(events_data)} events to {CSV_FILE}")

# -------------------------------------------------
# Cleanup
# -------------------------------------------------
driver.quit()
print("🎉 Done")
