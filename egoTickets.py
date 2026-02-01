from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# -----------------------------
# Setup Chrome
# -----------------------------
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

# -----------------------------
# Open the Ghana events page
# -----------------------------
url = "https://egotickets.com/events?country=gh"
driver.get(url)
print(f"🌐 Opened Events Page: {url}")

# -----------------------------
# Wait for the events grid
# -----------------------------
try:
    events_grid = wait.until(EC.presence_of_element_located((By.ID, "events-grid")))
    event_links = events_grid.find_elements(By.TAG_NAME, "a")  # all event links
    print(f"🔎 Found {len(event_links)} events on the page")
except Exception as e:
    print(f"❌ Failed to find events: {e}")
    driver.quit()
    exit()

# -----------------------------
# Click the first five events and extract details
# -----------------------------
for i in range(5):
    try:
        print(f"\n➡️ Opening Event {i+1}")
        link = event_links[i].get_attribute("href")
        driver.get(link)
        print(f"✅ Opened Event {i+1}: {link}")

        # ---- Event Name ----
        try:
            name_element = wait.until(EC.presence_of_element_located((By.XPATH, "//h1[1]")))
            event_name = name_element.text
            print(f"🎫 Event Name: {event_name}")
        except:
            event_name = ""
            print(f"❌ Failed to extract event name")

        # ---- Organizer Name ----
        try:
            organizer_element = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class,'flex') and contains(@class,'items-center') and contains(@class,'gap-3')]//h3[1]")
            ))
            organizer_name = organizer_element.text
            print(f"👤 Organizer: {organizer_name}")
        except:
            organizer_name = ""
            print(f"❌ Failed to extract organizer name")

        # ---- Organizer Phone & Email ----
        try:
            contact_div = driver.find_element(
                By.XPATH,
                "//div[contains(@class,'flex') and contains(@class,'flex-col') and contains(@class,'gap-3')]"
            )
            contact_links = contact_div.find_elements(By.TAG_NAME, "a")
            phone = ""
            email = ""
            for link_tag in contact_links:
                href = link_tag.get_attribute("href")
                if href and href.startswith("tel:"):
                    phone = href.replace("tel:", "").strip()
                elif href and href.startswith("mailto:"):
                    email = href.replace("mailto:", "").strip()
            print(f"📞 Organizer Phone: {phone}")
            print(f"✉️ Organizer Email: {email}")
        except:
            phone = ""
            email = ""
            print(f"❌ Failed to extract phone/email")

        # ---- Wait and go back ----
        time.sleep(2)
        driver.back()
        time.sleep(2)

        # Re-fetch the links after going back
        events_grid = wait.until(EC.presence_of_element_located((By.ID, "events-grid")))
        event_links = events_grid.find_elements(By.TAG_NAME, "a")

    except Exception as e:
        print(f"❌ Failed with Event {i+1}: {e}")
        continue

driver.quit()
