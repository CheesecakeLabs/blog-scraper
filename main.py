import os
import sys
from datetime import datetime

from scraper import CheesecakeBlogScraper

from dotenv import load_dotenv

ENVIRONMENT = os.getenv("ENVIRONMENT")
load_dotenv(f"./config/.env.{ENVIRONMENT}")


def main():
    verbose, store_on_database, continue_scrapping = get_flags()
    start_time = datetime.now()
    url_to_visit = "https://cheesecakelabs.com/blog/post-sitemap.xml"

    scraper = CheesecakeBlogScraper(store_on_database=store_on_database)
    scraper.visit_page(
        url_to_visit,
        continue_scrapping=continue_scrapping,
        verbose=verbose,
    )

    end_time = datetime.now()
    print(f"Visited {len(scraper.visited_links)} links")
    total_ingestion = scraper.database_index if store_on_database else 0
    print(f"{total_ingestion} documents inserted into the database")
    print(f"Start time: {start_time}")
    print(f"End time: {end_time}")
    print(f"Duration: {end_time - start_time}")


def get_flags():
    verbose = "-verbose" in sys.argv
    store_on_database = "-store-on-database" in sys.argv
    continue_scrapping = "-continue-scrapping" in sys.argv
    return verbose, store_on_database, continue_scrapping


if __name__ == "__main__":
    main()
