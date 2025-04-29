from typing import List
from playwright.sync_api import sync_playwright
import os, logging, time, random
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)

class Plugin:
    name = "salesnav"

    def __init__(self):
        self.email = "touka.taiga14@gmail.com"
        self.password = "touka.taiga1114"
        self.keyword = os.getenv("LI_KEYWORD", "CTO web3")

    def human_like_delay(self):
        """Add random delays to simulate human behavior"""
        time.sleep(random.uniform(1, 3))

    def handle_security_check(self, page):
        """Handle LinkedIn security checkpoint"""
        try:
            # Check if we're on a security checkpoint page
            if "checkpoint" in page.url:
                logging.info("Security checkpoint detected. Please complete the verification manually...")
                
                # Wait for manual verification
                while "checkpoint" in page.url:
                    time.sleep(2)
                    if "feed" in page.url:
                        logging.info("Security checkpoint passed!")
                        return True
                
                # If we're still on checkpoint after 60 seconds, raise error
                if "checkpoint" in page.url:
                    raise Exception("Security checkpoint not resolved in time")
            return True
        except Exception as e:
            logging.error(f"Error handling security checkpoint: {str(e)}")
            return False

    def fetch(self) -> List[dict]:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-site-isolation-trials'
                ]
            )
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720},
                locale="en-US",
                timezone_id="America/New_York"
            )
            
            page = context.new_page()
            
            try:
                # Step 1: Go to login page
                logging.info("Navigating to LinkedIn login page...")
                page.goto("https://www.linkedin.com/login")
                self.human_like_delay()
                
                # Step 2: Fill login form
                logging.info("Filling in credentials...")
                page.fill("#username", self.email)
                self.human_like_delay()
                page.fill("#password", self.password)
                self.human_like_delay()
                
                # Step 3: Click login button
                logging.info("Clicking login button...")
                page.click("button[type=submit]")
                
                # Step 4: Handle security check if needed
                if not self.handle_security_check(page):
                    raise Exception("Failed to handle security checkpoint")
                
                # Step 5: Wait for successful login
                page.wait_for_load_state("networkidle", timeout=60000)
                
                # Step 6: Verify login success
                if "feed" not in page.url:
                    logging.error(f"Login failed, current page: {page.url}")
                    browser.close()
                    return []
                
                logging.info("Login successful")
                
                # Step 7: Search page
                logging.info(f"Searching for: {self.keyword}")
                search_url = f"https://www.linkedin.com/search/results/people/?keywords={self.keyword}&origin=GLOBAL_SEARCH_HEADER"
                page.goto(search_url)
                self.human_like_delay()
                
                # Step 8: Wait for search results
                page.wait_for_selector("div.entity-result__content", timeout=60000)
                
                # Step 9: Scrape cards
                cards = page.query_selector_all("div.entity-result__content")[:20]
                leads = []
                
                logging.info(f"Found {len(cards)} results")
                
                for card in cards:
                    try:
                        name = card.query_selector("span[dir='ltr']").inner_text()
                        headline = card.query_selector("div.entity-result__primary-subtitle").inner_text()
                        company = card.query_selector("div.entity-result__secondary-subtitle").inner_text()
                        profile_url = card.query_selector("a.app-aware-link").get_attribute("href")
                        external_id = profile_url.split("/")[-2]
                        
                        leads.append(dict(
                            source="salesnav",
                            external_id=external_id,
                            city=None,
                            title=headline,
                            body="",
                            contact_name=name,
                            email=None,
                            phone=None,
                            rate=None,
                            posted_at=datetime.utcnow()
                        ))
                    except Exception as e:
                        logging.warning(f"Failed to parse card: {e}")
                        continue
                
                return leads
                
            except Exception as e:
                logging.error(f"Error during execution: {str(e)}")
                return []
            finally:
                try:
                    browser.close()
                except:
                    pass

if __name__ == "__main__":
    logging.info("Testing SalesNav plugin...")
    if not os.getenv("LI_EMAIL") or not os.getenv("LI_PASS"):
        logging.error("LinkedIn credentials not set in environment variables")
    else:
        plugin = Plugin()
        try:
            leads = plugin.fetch()
            logging.info(f"Found {len(leads)} leads")
            for lead in leads[:3]:  # Print first 3 leads as sample
                logging.info(f"Lead: {lead['contact_name']} - {lead['title']}")
        except Exception as e:
            logging.error(f"Error testing plugin: {str(e)}")
