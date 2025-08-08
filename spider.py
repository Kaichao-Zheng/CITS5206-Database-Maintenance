import time
import random
import pandas as pd
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from linkedin_scraper import Person, actions

# ====================
# Helpers
# ====================

def human_delay(a=1.5, b=4.0):
    time.sleep(random.uniform(a, b))

def random_scroll(driver):
    scroll_script = f"window.scrollBy(0, {random.randint(-300, 300)});"
    driver.execute_script(scroll_script)
    human_delay(1, 2)

# ====================
# Setup WebDriver
# ====================
# USER_AGENT = (
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#     "AppleWebKit/537.36 (KHTML, like Gecko) "
#     "Chrome/114.0.0.0 Safari/537.36"
# )

# # create the Chromeoption
# options = webdriver.ChromeOptions()
# options.add_argument(f"user-agent={USER_AGENT}")
# # option: mimic genuine user
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument("--start-maximized")

driver = webdriver.Chrome()
load_dotenv()
email = os.getenv("LINKEDIN_EMAIL")
password = os.getenv("LINKEDIN_PASSWORD")
actions.login(driver, email, password)
# human_delay(3, 6)

# ====================
# Name list
# ====================

name_list = [
    "Andre Iguodala",
    "Adam D'Angelo",
    "Satya Nadella"
    # 你可以继续添加更多名字
]

# ====================
# Data collection
# ====================

records = []

for name in name_list:
    print(f"\nSearching for: {name}")
    try:
        # enter search url
        search_url = f"https://www.linkedin.com/search/results/people/?keywords={name.replace(' ', '%20')}"
        driver.get("https://www.linkedin.com")
        driver.get(search_url)
#         human_delay(3, 6)
        # Mimic human scrolls
        for _ in range(random.randint(3, 6)):
            random_scroll(driver)

        # position information that we want 
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "search-results-container"))
        )

        ul = container.find_element(By.TAG_NAME, "ul")
        li_list = ul.find_elements(By.TAG_NAME, "li")

        if li_list:
            first_li = li_list[0]
            a_tag = first_li.find_element(By.TAG_NAME, "a")
            href = a_tag.get_attribute("href")

            if href and "/in/" in href:
                print("Opening profile:", href)
                profile_url = href
#                 human_delay(4, 7)

                # scrape information 
                person = Person(profile_url,driver=driver,scrape=False)
                
                name = person.name or ""
                company = person.company or ""

                # get the positiontitle
                position_title = ""
                if person.experiences:
                    position_title = person.experiences[0].position_title or ""

                print("Name:", name)
                print("Company:", company)
                print("Position:", position_title)

                # record to record list
                records.append({
                    "Name": name,
                    "Company": company,
                    "Position": position_title
                })
            else:
                print("No valid profile link found.")
        else:
            print("No <li> elements found.")
    except Exception as e:
        print("Error during search/profile:", e)

    # delay
    human_delay(2,4)

# ====================
# Export to Excel
# ====================

df = pd.DataFrame(records)
excel_filename = "linkedin_profiles.xlsx"
df.to_excel(excel_filename, index=False)
print(f"\n✅ Done. Exported {len(records)} profiles to {excel_filename}")

# ====================
# Close
# ====================
# driver.quit()