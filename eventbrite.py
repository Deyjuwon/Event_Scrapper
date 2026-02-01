import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# -------------------- SETUP --------------------
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")
options.add_argument("--disable-infobars")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

# -------------------- DATA --------------------
categories = [
    "Music",
    "Nightlife",
    "Performing & Visual Arts",
    "Holidays",
    "Hobbies",
    "Business",
    "Food & Drink"
]

output_file = "eventbrite_events.csv"
csv_headers = ["Category", "Event Name", "Organizer", "Date", "Time", "Price"]
all_data = []

# -------------------- SCRAPING --------------------
try:
    for category in categories:
        print(f"\n🎯 Processing Category: {category}")

        driver.get("https://www.eventbrite.com/")
        time.sleep(5)

        # Find categories
        category_elements = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "iconCategoryCardTitle"))
        )

        found = False
        for el in category_elements:
            if el.text.strip() == category:
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", el
                )
                time.sleep(1)
                el.click()
                found = True
                break

        if not found:
            print(f"⚠️ Category not found: {category}")
            continue

        time.sleep(5)
        index = 0

        while True:
            event_titles = driver.find_elements(
                By.XPATH, "//h3[contains(@class, 'event-card__clamp-line--two')]"
            )

            if index >= len(event_titles):
                print(f"✅ Finished {category}")
                break

            print(f"➡️ Visiting event {index + 1} of {len(event_titles)}")

            event_title = event_titles[index]
            parent_link = event_title.find_element(By.XPATH, "./ancestor::a")

            original_window = driver.current_window_handle
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", parent_link
            )
            time.sleep(1)
            parent_link.click()

            # Switch to new tab
            wait.until(EC.number_of_windows_to_be(2))
            new_window = [w for w in driver.window_handles if w != original_window][0]
            driver.switch_to.window(new_window)

            time.sleep(4)

            # -------------------- SCRAPE EVENT --------------------
            try:
                event_name = driver.find_element(
                    By.CSS_SELECTOR, "h1.event-title"
                ).text.strip()
            except:
                event_name = ""

            try:
                organizer = driver.find_element(
                    By.CSS_SELECTOR,
                    "strong.organizer-listing-info-variant-b__name-link"
                ).text.strip()
            except:
                organizer = ""

            try:
                datetime_text = driver.find_element(
                    By.CSS_SELECTOR, "span.date-info__full-datetime"
                ).text.strip()

                if "·" in datetime_text:
                    date, time_ = map(str.strip, datetime_text.split("·", 1))
                else:
                    date, time_ = datetime_text, ""
            except:
                date, time_ = "", ""

            try:
                price = driver.find_element(
                    By.CSS_SELECTOR, "div.conversion-bar__panel-info"
                ).text.strip()
            except:
                price = ""

            print(f"📍 {event_name} | {organizer} | {date} | {time_} | {price}")

            all_data.append([
                category,
                event_name,
                organizer,
                date,
                time_,
                price
            ])

            # Close tab & return
            driver.close()
            driver.switch_to.window(original_window)
            time.sleep(3)

            index += 1

except Exception as e:
    print("❌ Unexpected error:", e)

finally:
    # -------------------- SAVE CSV --------------------
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)
        writer.writerows(all_data)

    print(f"\n📦 Scraping complete. Data saved to '{output_file}'")
    driver.quit()
