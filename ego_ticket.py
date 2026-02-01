import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, 10)

url = "https://egotickets.com/events?country=gh"
driver.get(url)
print("🌐 Page opened")

wait.until(EC.presence_of_element_located((By.ID, "events-grid")))
time.sleep(2)

# Event name XPaths (template variants)
NAME_XPATHS = [
    '//*[@id="main-content"]/div/div[1]/div[3]/div/div/div[1]/div[3]/h1',
    '//*[@id="main-content"]/div/div[1]/div[3]/div/div/div/div[2]/h1'
]

for i in range(1, 6):
    try:
        print(f"\n🔍 Opening event {i}")

        event_xpath = f'//*[@id="events-grid"]/a[{i}]/div[1]'
        event_card = wait.until(
            EC.presence_of_element_located((By.XPATH, event_xpath))
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            event_card
        )
        time.sleep(1)

        driver.execute_script("arguments[0].click();", event_card)

        # Try multiple XPaths
        event_name = ""
        for xpath in NAME_XPATHS:
            try:
                event_name = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                ).text
                break
            except TimeoutException:
                continue

        if event_name:
            print(f"✅ Event Name: {event_name}")
        else:
            print("⚠️ Event name not found (unknown layout)")

        time.sleep(3)

        driver.back()
        wait.until(EC.presence_of_element_located((By.ID, "events-grid")))
        time.sleep(2)

    except Exception as e:
        print(f"❌ Error on event {i}: {e}")

driver.quit()
print("\n🎉 Done")
