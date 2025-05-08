# from playwright.sync_api import sync_playwright
# import csv
# import time
# import logging
# from datetime import datetime

# logging.basicConfig(level=logging.INFO)

# def save_emails_to_csv(email_data, filename="extracted_emails.csv"):
#     with open(filename, mode='w', newline='', encoding='utf-8') as file:
#         writer = csv.writer(file)
#         writer.writerow(['Email'])
#         for email in email_data:
#             writer.writerow([email])

# def run_plugin():
#     with sync_playwright() as p:
#         browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
#         context = browser.contexts[0]

#         # Step 1: Find the GMO dashboard tab
#         dashboard_page = None
#         for page in context.pages:
#             if "growmeorganic.com/dashboard/b2b/features/my-lists" in page.url:
#                 dashboard_page = page
#                 break

#         if not dashboard_page:
#             logging.error("❌ GMO dashboard tab not found. Please open it manually and rerun.")
#             return

#         logging.info("✅ GMO dashboard tab found. Bringing it to front and extracting data...")
#         dashboard_page.bring_to_front()

#         # Step 2: Click "View the data" button if needed
#         try:
#             dashboard_page.wait_for_selector("text='View the data'", timeout=10000)
#             dashboard_page.click("text='View the data'")
#             time.sleep(3)
#         except:
#             logging.info("ℹ️ 'View the data' not found or already on data page.")

#         # Step 3: Wait for table and extract data
#         dashboard_page.wait_for_selector("table", timeout=15000)
#         rows = dashboard_page.query_selector_all("table tr")
#         email_data = []

#         for row in rows[1:]:  # skip header
#             cols = row.query_selector_all("td")
#             if len(cols) >= 1:
#                 email = cols[0].inner_text().strip()
#                 if email:
#                     email_data.append(email)

#         logging.info(f"✅ Extracted {len(email_data)} emails. Saving to CSV...")
#         save_emails_to_csv(email_data)
#         logging.info("✅ Done. Emails saved to 'extracted_emails.csv'.")

# if __name__ == "__main__":
#     run_plugin()


from playwright.sync_api import sync_playwright
import csv
import time
import logging
import os
import subprocess
from datetime import datetime

logging.basicConfig(level=logging.INFO)

def save_data_to_csv(data, filename="extracted_data.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['First Name', 'Last Name', 'Email'])  # Add columns for First and Last Name
        for row in data:
            writer.writerow(row)

def run_plugin():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]

        # Step 1: Find the GMO dashboard tab
        dashboard_page = None
        for page in context.pages:
            if "growmeorganic.com/dashboard/b2b/features/my-lists" in page.url:
                dashboard_page = page
                break

        if not dashboard_page:
            logging.error("❌ GMO dashboard tab not found. Please open it manually and rerun.")
            return

        logging.info("✅ GMO dashboard tab found. Bringing it to front and extracting data...")
        dashboard_page.bring_to_front()

        # Step 2: Click "View the data" button if needed
        try:
            dashboard_page.wait_for_selector("text='View the data'", timeout=10000)
            dashboard_page.click("text='View the data'")
            time.sleep(3)
        except:
            logging.info("ℹ️ 'View the data' not found or already on data page.")

        # Step 3: Wait for table and extract data
        dashboard_page.wait_for_selector("table", timeout=15000)
        rows = dashboard_page.query_selector_all("table tr")
        extracted_data = []

        for row in rows[1:]:  # skip header
            cols = row.query_selector_all("td")
            if len(cols) >= 3:  # Ensure there are at least 3 columns (First Name, Last Name, and Email)
                first_name = cols[4].inner_text().strip()  # Assuming First Name is in the first column
                last_name = cols[6].inner_text().strip()   # Assuming Last Name is in the second column
                email = cols[0].inner_text().strip()       # Assuming Email is in the third column

                # Only add if the data is valid
                if first_name and last_name and email:
                    extracted_data.append([first_name, last_name, email])

        logging.info(f"✅ Extracted {len(extracted_data)} records. Saving to CSV...")
        save_data_to_csv(extracted_data)
        logging.info("✅ Done. Data saved to 'extracted_data.csv'.")

        # Step 4: Wait for 1 minute before sending emails
        # logging.info("⏳ Waiting for 1 minute before sending emails...")
        # time.sleep(60)  # 1-minute delay

        # # Step 5: Run the send_emails.py script from 2 directories behind
        # logging.info("✅ Running send_emails.py script...")
        
        # try:
        #     # Go 2 directories back and run send_emails.py
        #     subprocess.run(['python', '../../send_emails.py'], check=True)
        #     logging.info("✅ send_emails.py script executed successfully!")
        # except subprocess.CalledProcessError as e:
        #     logging.error(f"❌ Error running send_emails.py: {str(e)}")

if __name__ == "__main__":
    run_plugin()










