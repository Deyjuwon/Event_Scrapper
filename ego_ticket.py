import time
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

wait = WebDriverWait(driver, 10)

# -------------------------------------------------
# Open events page
# -------------------------------------------------
URL = "https://egotickets.com/events?country=gh"
driver.get(URL)
print("🌐 Opened Ghana events page")

wait.until(EC.presence_of_element_located((By.ID, "events-grid")))
time.sleep(2)

# -------------------------------------------------
# XPaths
# -------------------------------------------------
EVENT_NAME_XPATHS = [
    '//*[@id="main-content"]/div/div[1]/div[3]/div/div/div[1]/div[3]/h1',
    '//*[@id="main-content"]/div/div[1]/div[3]/div/div/div/div[2]/h1'
]

LOCATION_A_XPATHS = [
    '//*[@id="main-content"]/div/div[1]/div[3]/div/div/div[1]/div[4]/a',
    '//*[@id="main-content"]/div/div[1]/div[3]/div/div/div/div[3]/a'
]

EMAIL_XPATH = '//*[@id="main-content"]/div/div[2]/div/div/div[1]/section[2]/div/div[2]/a[2]'

CTA_KEYWORDS = ["get ticket", "buy", "register", "rsvp"]

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

def extract_phone(driver):
    phone_links = driver.find_elements(By.XPATH, "//a[starts-with(@href, 'tel:')]")
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
# Scrape first 3 events
# -------------------------------------------------
for i in range(1, 10):
    try:
        print(f"\n🔍 Opening event {i}")

        event_card_xpath = f'//*[@id="events-grid"]/a[{i}]/div[1]'
        event_card = wait.until(
            EC.presence_of_element_located((By.XPATH, event_card_xpath))
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            event_card
        )
        time.sleep(1)

        driver.execute_script("arguments[0].click();", event_card)

        # -------------------------
        # Extract data
        # -------------------------
        event_name = extract_event_name(driver)
        location = extract_location(driver)
        phone = extract_phone(driver)
        email = extract_email(driver)

        # -------------------------
        # Print
        # -------------------------
        print(f"✅ Event Name: {event_name if event_name else 'N/A'}")
        print(f"📍 Location: {location if location else 'N/A'}")
        print(f"📞 Phone: {phone if phone else 'N/A'}")
        print(f"✉️ Email: {email if email else 'N/A'}")

        time.sleep(2)

        driver.back()
        wait.until(EC.presence_of_element_located((By.ID, "events-grid")))
        time.sleep(2)

    except Exception as e:
        print(f"❌ Error on event {i}: {e}")

# -------------------------------------------------
# Cleanup
# -------------------------------------------------
driver.quit()
print("\n🎉 Done")
