import os
import time
import random
import ndjson
import dateparser
import urllib.parse

# selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

# Importing the base URL from settings
from settings.settings import GNEWS_BASE_URL
from settings.settings import logging

from packages.utils import get_url_vecid

class GoogleNewsCrawler:
    def __init__(self, nlp=None):
        self.driver = self.init_driver()
        self.nlp = nlp

    def init_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        return webdriver.Chrome(options=chrome_options)

    def build_search_query(self, keyword, negative_keywords):
        exclude_str = " ".join(f"-{term}" for term in negative_keywords)
        return f"{keyword} {exclude_str}".strip()

    def build_search_url(
        self, 
        keyword, 
        start_date, 
        end_date, 
        negative_keywords, 
        language_code=None
    ):
        query = self.build_search_query(keyword, negative_keywords)
        query_encoded = urllib.parse.quote_plus(query)
        url = (
            f"{GNEWS_BASE_URL}"
            f"q={query_encoded}"
            f"&tbs=cdr:1,cd_min:{start_date},cd_max:{end_date}"
            f"&tbm=nws"
        )
        if language_code:
            url += f"&lr={language_code}"
        return url

    def crawl_google_news(
        self, 
        keyword, 
        start_date, 
        end_date, 
        negative_keywords, 
        language_code=None, 
        lang_short="en", 
        max_pages=10, 
        ndjson_file=None,
        mongo_inserter=None,
        storage_mode="mongo"
    ):
        search_url = self.build_search_url(keyword, start_date, end_date, negative_keywords, language_code)
        self.driver.get(search_url)
        time.sleep(random.uniform(2, 5))
        all_results = []
        page_num = 1
        while True:
            articles = self.driver.find_elements(By.XPATH, "//div[@class='SoaBEf']")
            for article in articles:
                try:
                    title = article.find_element(By.XPATH, ".//div/div[@class='SoAPf']/div[contains(@class, 'n0jPhd')]").text
                    url = article.find_element(By.XPATH, ".//div/a[@class='WlydOe']").get_attribute("href")
                    snippet = article.find_element(By.XPATH, ".//div/div[@class='SoAPf']/div[contains(@class, 'GI74Re')]").text
                    published_date = article.find_element(By.XPATH, ".//div/div[@class='SoAPf']/div[contains(@class, 'OSrXXb')]").text
                    parsed_date = dateparser.parse(published_date)
                    
                    if parsed_date:
                        published_date = parsed_date.strftime('%Y-%m-%d')
                    else:
                        published_date = ""
                        
                    # ------- Generate vecID here -------
                    if self.nlp and url:
                        vecID = get_url_vecid(url, self.nlp)
                    else:
                        vecID = None
                        
                    all_results.append({
                        "vecID": vecID,
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "published_date": published_date,
                        "keyword": keyword,
                        "language": lang_short,
                        "crawl_flag": False
                    })
                except Exception as e:
                    logging.error(f"      Error extracting article data: {e}")
                    continue
                
            # Save results page by page to MongoDB or NDJSON for robustness
            if all_results:
                if storage_mode == "mongo" and mongo_inserter:
                    mongo_inserter.insert_document_list(all_results, page_num=page_num)
                elif storage_mode == "ndjson" and ndjson_file:
                    self.append_ndjson(ndjson_file, all_results)
                else:
                    logging.warning(f"  No storage method selected or configured!")
                all_results = []
                
            try:
                next_button = self.driver.find_element(By.ID, "pnnext")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(random.uniform(1.2, 2.8))
                next_button.click()
                page_num += 1
                time.sleep(random.uniform(2, 5))
                if page_num > max_pages:
                    break
            except NoSuchElementException:
                logging.info("    No more pages to crawl.")
                break
        logging.info(f"    Finished date range for {keyword}: {start_date} - {end_date}")

    def append_ndjson(self, filename, data):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "a", encoding='utf-8') as f:
            writer = ndjson.writer(f)
            for item in data:
                writer.writerow(item)

    def close(self):
        self.driver.quit()