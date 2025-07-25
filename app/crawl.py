import os
import time
import spacy
import random
from datetime import datetime

from settings.settings import (
    logging, GNEWS_OUTPUT_FILE
)
from packages.utils import three_month_range
from packages.google_news_crawler import GoogleNewsCrawler
from packages.mongodb_inserter import MongoDBInserter
from constants.gnews_search_keywords import SEARCH_KEYWORDS
from constants.gnews_negative_keywords import EXCLUDE_TERMS
from constants.gnews_languages import SEARCH_LANGS

def main():
    start_year = 2015
    start_month = 1
    end_date = datetime.now()

    ndjson_file = GNEWS_OUTPUT_FILE
    storage_mode = "mongo"  # or "ndjson"

    if storage_mode == "ndjson" and os.path.exists(ndjson_file):
        os.remove(ndjson_file)

    nlp = spacy.load('en_core_web_sm')
    crawler = GoogleNewsCrawler(nlp=nlp)
    mongo_inserter = MongoDBInserter() if storage_mode == "mongo" else None

    try:
        for lang_short, lang_code in SEARCH_LANGS:
            logging.info(f"--- Starting crawl for language: {lang_short} ({lang_code}) ---")
            search_keywords = SEARCH_KEYWORDS.get(lang_short, [])
            negative_keywords = EXCLUDE_TERMS.get(lang_short, [])
            if not search_keywords:
                logging.warning(f"  Skipping {lang_short}: No search keywords provided.")
                continue
            for keyword in search_keywords:
                logging.info(f"--- Searching for: {keyword} ---")
                current_start = datetime(start_year, start_month, 1)
                for month_start, month_end in three_month_range(current_start, end_date):
                    start_str = month_start.strftime("%m/%d/%Y")
                    end_str = month_end.strftime("%m/%d/%Y")
                    logging.info(f"  {start_str} to {end_str}")
                    try:
                        crawler.crawl_google_news(
                            keyword=keyword,
                            start_date=start_str,
                            end_date=end_str,
                            negative_keywords=negative_keywords,
                            language_code=lang_code,
                            lang_short=lang_short,
                            max_pages=10,
                            ndjson_file=ndjson_file if storage_mode == "ndjson" else None,
                            mongo_inserter=mongo_inserter,
                            storage_mode=storage_mode
                        )
                    except Exception as e:
                        logging.error(f"    Error: {e}")
                    time.sleep(random.uniform(2, 5))
    finally:
        crawler.close()
        if mongo_inserter:
            mongo_inserter.close()

    if storage_mode == "mongo":
        if mongo_inserter and mongo_inserter.collection:
            logging.info(f"Results saved to MongoDB collection: {mongo_inserter.collection.name}")
        else:
            logging.warning("MongoDB collection was not initialized properly.")
    else:
        logging.info(f"Finished! Results saved to {ndjson_file}")

if __name__ == "__main__":
    main()