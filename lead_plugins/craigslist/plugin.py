from typing import List
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re, os, time, logging
from fake_useragent import UserAgent
import random
import requests
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)

class Plugin:
    name = "craigslist"

    def __init__(self):
        chrome_opts = Options()
        # Run non-headless for now to avoid Craigslist blocking
        chrome_opts.add_argument("--headless")
        chrome_opts.add_argument("--no-sandbox")
        chrome_opts.add_argument("--disable-dev-shm-usage")

        # Add random user agent
        ua = UserAgent()
        chrome_opts.add_argument(f"user-agent={ua.random}")

        # Mask browser automation flags
        chrome_opts.add_argument("--disable-blink-features=AutomationControlled")
        chrome_opts.add_argument("--disable-infobars")
        chrome_opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_opts.add_experimental_option('useAutomationExtension', False)

        # Connect to Selenium remote
        self.driver = webdriver.Remote(
            command_executor="http://selenium:4444",
            options=chrome_opts,
        )

        # Remove webdriver traces from navigator object
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })

        self.wait = WebDriverWait(self.driver, 10)
        self.cities = [
            "newyork",  # Starting with just New York for now
        ]
        self.gig_path = "/d/computer-gigs/search/cpg?sort=date"

    def is_valid_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def parse_contact(self, text):
        email = re.search(r"[\w\.-]+@[\w\.-]+", text)
        phone = re.search(r"\(?\d{3}[) .-]?\d{3}[ .-]?\d{4}", text)
        return email.group(0) if email else None, phone.group(0) if phone else None

    def fetch(self) -> List[dict]:
        leads = []
        for city in self.cities:
            try:
                url = f"https://{city}.craigslist.org{self.gig_path}"
                logging.info(f"Checking URL: {url}")

                if not self.is_valid_url(url):
                    logging.error(f"Invalid URL format: {url}")
                    continue

                logging.info(f"URL is valid and accessible. Fetching from {url}")

                time.sleep(2 + random.random() * 3)
                self.driver.get(url)

                # Give extra time for dynamic posts to load
                time.sleep(5)
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                logging.info("3 sec over , 8 sec started")
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(8) 
                # Save page source for inspection (optional)
                with open("/code/page_debug.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)

                logging.info("Saved page_debug.html for inspection.")
                logging.info("Waiting for results to load...")

                # posts = self.wait.until(
                #     EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.result-row"))
                # )
                # logging.info(f"Found {len(posts)} posts")

                posts = WebDriverWait(self.driver, 20).until(
                  EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.result-row")))
                logging.info(f"Found {len(posts)} posts")

                for p in posts[:5]:  # Limit to 5 posts
                    try:
                        logging.info("Processing post...")

                        link = p.find_element(By.CSS_SELECTOR, "a.result-title")
                        title = link.text
                        href = link.get_attribute("href")

                        logging.info(f"Found post: {title}")

                        post_id = href.split("/")[-1].split(".")[0]

                        # Open post detail
                        time.sleep(1 + random.random() * 2)
                        self.driver.get(href)

                        body_element = self.wait.until(
                            EC.visibility_of_element_located((By.ID, "postingbody"))
                        )
                        body = body_element.text

                        with open(f"/code/post_debug_{post_id}.html", "w", encoding="utf-8") as f:
                         f.write(self.driver.page_source)

                        email, phone = self.parse_contact(body)
                        logging.info(f"Contact info - Email: {email}, Phone: {phone}")

                        leads.append(dict(
                            source="craigslist",
                            external_id=post_id,
                            city=city,
                            title=title,
                            body=body,
                            contact_name=None,
                            email=email,
                            phone=phone,
                            rate=None,
                            posted_at=datetime.utcnow()
                        ))

                    except Exception as e:
                        logging.error(f"Error processing post: {str(e)}")
                        continue

            except Exception as e:
                logging.error(f"Error processing city {city}: {str(e)}")
                continue

        return leads

if __name__ == "__main__":
    logging.info("Testing Craigslist plugin...")
    plugin = Plugin()
    try:
        leads = plugin.fetch()

        logging.info(f"Found {len(leads)} leads")
        for lead in leads[:3]:  # Sample print first 3 leads
            logging.info(f"Lead: {lead['title']} in {lead['city']}")
            if lead['email']:
                logging.info(f"Contact: {lead['email']}")
    except Exception as e:
        logging.error(f"Error testing plugin: {str(e)}")
    finally:
        plugin.driver.quit()
