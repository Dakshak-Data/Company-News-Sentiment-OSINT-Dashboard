# zauba_scraper.py
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def setup_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
    )



    driver = webdriver.Chrome(options=options)
    return driver


def scrape_zauba_details(company_name: str):
    driver = setup_driver()

    data = {
        "company_name": None,
        "cin": None,
        "status": None,
        "roc": None,
        "registration_date": None,
        "authorized_capital": None,
        "paidup_capital": None,
        "directors": []   #ONLY CURRENT DIRECTORS
    }

    try:
    
        search_url = f"https://www.zaubacorp.com/companysearchresults/{company_name.replace(' ', '%20')}"
        print("[+] Opening search:", search_url)

        driver.get(search_url)
        time.sleep(4)

        rows = driver.find_elements(By.CSS_SELECTOR, "table.table.table-striped tbody tr")
        if not rows:
            print("[-] No results found.")
            return data

        company_url = rows[0].find_element(By.TAG_NAME, "a").get_attribute("href")

        print("[+] Opening company page:", company_url)
        driver.get(company_url)
        time.sleep(4)

        # Scroll down to ensure dynamic content loads
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.5);")
        time.sleep(3)

        page_html = driver.page_source
        soup = BeautifulSoup(page_html, "html.parser")

    
        basic_table = soup.find("table", class_="table table-striped")

        if basic_table:
            for tr in basic_table.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) != 2:
                    continue

                key = tds[0].text.strip().lower()
                val = tds[1].text.strip()

                if "name" in key:
                    data["company_name"] = val
                elif "cin" in key:
                    data["cin"] = val
                elif "status" in key:
                    data["status"] = val
                elif "roc" in key:
                    data["roc"] = val
                elif "date of incorporation" in key:
                    data["registration_date"] = val
                elif "authorised capital" in key:
                    data["authorized_capital"] = val
                elif "paid up capital" in key:
                    data["paidup_capital"] = val

    
        directors = []

        director_section = soup.find("div", id="director-information")

        if director_section:
  
            content = director_section.find("div", id="director-information-content")

            if content:
              
                director_table = content.find("table")

                if director_table:
                    rows = director_table.find("tbody").find_all("tr")[1:]  

                    for tr in rows:
                        tds = tr.find_all("td")

                        if len(tds) < 4:
                            continue

                        directors.append({
                            "din": tds[0].text.strip(),
                            "name": tds[1].text.strip(),
                            "designation": tds[2].text.strip(),
                            "appointment": tds[3].text.strip(),
                        })

        data["directors"] = directors

        return data

    except Exception as e:
        print("Zauba scraping error:", e)
        return data

    finally:
        print("[+] Closing browser...")
        driver.quit()
