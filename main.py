import sys
from datetime import datetime

from scraper import CheesecakeBlogScraper


def main():
    verbose, store_on_database, continue_scrapping = get_flags()
    start_time = datetime.now()
    url_to_visit = "https://cheesecakelabs.com/blog/building-custom-ui-controls-xcodes/"

    scraper = CheesecakeBlogScraper(store_on_database=store_on_database)
    scraper.visit_page(
        url_to_visit,
        continue_scrapping=continue_scrapping,
        verbose=verbose,
    )

    end_time = datetime.now()
    print(f"Visited {len(scraper.visited_links)} links")
    print(f"{scraper.database_index} documents inserted into the database")
    print(f"Start time: {start_time}")
    print(f"End time: {end_time}")
    print(f"Duration: {end_time - start_time}")


def get_flags():
    verbose = "-verbose" in sys.argv
    store_on_database = "-store_on_database" in sys.argv
    continue_scrapping = "-continue_scrapping" in sys.argv
    return verbose, store_on_database, continue_scrapping


if __name__ == "__main__":
    main()
