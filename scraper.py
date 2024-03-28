import re
import chromadb
import requests

from datetime import datetime
from pprint import pprint
from bs4 import BeautifulSoup
from termcolor import colored, cprint
from embeddings.embedding_functions import AWSEmbeddingFunction
from chromadb.config import Settings

import os


class CheesecakeBlogScraper:
    def __init__(
            self,
            store_on_database: bool = False,
    ):
        self.url_index = 0
        self.database_index = 1
        self.store_on_database = store_on_database
        self.visited_links = []
        self.urls_to_visit = []
        CHROMA_AUTH_CREDENTIALS = os.getenv("CHROMA_AUTH_CREDENTIALS")
        CHROMADB_HOST = os.getenv("CHROMADB_HOST")
        CHROMADB_PORT = os.getenv("CHROMADB_PORT")
        CHROMADB_COLLECTION_NAME = os.getenv("CHROMADB_COLLECTION_NAME")

        if store_on_database:
            self.client = chromadb.HttpClient(
                host=CHROMADB_HOST,
                port=CHROMADB_PORT,
                settings=Settings(
                    chroma_client_auth_provider="chromadb.auth.token.TokenAuthClientProvider",
                    chroma_client_auth_token_transport_header="X_CHROMA_TOKEN",
                    chroma_client_auth_credentials=CHROMA_AUTH_CREDENTIALS,
                ),
            )
            # Uncomment this line if you want to delete the collection and start from scratch
            # self.client.delete_collection(name="cheesecake-blog-aws")
            self.collection = self.client.get_or_create_collection(
                name=CHROMADB_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
                embedding_function=AWSEmbeddingFunction(),
            )
            cprint("ChromaDB initialized.", "yellow", attrs=["bold"])

    def visit_page(
            self,
            url: str,
            continue_scrapping: bool = True,
            verbose: bool = False,
    ):
        if not self.has_url_in(url, self.visited_links):
            if verbose:
                header_str = colored("Visiting: ", "yellow", attrs=["bold"])
                cprint(header_str, end="")
                print(url)

                header_str = colored("Time: ", "yellow", attrs=["bold"])
                cprint(header_str, end="")
                print(datetime.now())

            response = requests.get(url)
            is_xml = url.split(".")[-1] == "xml"
            if is_xml:
                bs = BeautifulSoup(response.text, "lxml-xml")
            else:
                bs = BeautifulSoup(response.text, "lxml")
            title = self.get_page_title(bs, verbose)
            publishing_date = self.get_page_publishing_date(bs, verbose)
            paragraphs = self.get_page_text(bs, verbose)

            if self.store_on_database and len(paragraphs) > 0:
                if verbose:
                    cprint("Creating metadata...", "yellow", attrs=["bold"])

                metadata = [
                    dict(
                        url=url,
                        title=title,
                        publishing_date=(
                            publishing_date.isoformat() if publishing_date else ""
                        ),
                    )
                    for i in range(len(paragraphs))
                ]
                index_limit = len(paragraphs) + self.database_index
                ids = [str(i) for i in range(self.database_index, index_limit)]
                self.database_index += len(paragraphs)
                self.save(paragraphs, ids, metadata, verbose)

            if continue_scrapping:
                self.parse_blog_pages_links(bs, is_xml, url)

                if self.url_index < len(self.urls_to_visit):
                    self.visit_page(
                        self.urls_to_visit[self.url_index], continue_scrapping, verbose
                    )

    @staticmethod
    def get_page_title(bs: BeautifulSoup, verbose: bool = False) -> str:
        if bs.find("h1") is None:
            return ""
        title = bs.find("h1").text
        if verbose:
            header_str = colored("Title: ", "yellow", attrs=["bold"])
            cprint(header_str, end="")
            print(title)
        return title

    @staticmethod
    def get_page_publishing_date(
            bs: BeautifulSoup, verbose: bool = False
    ) -> datetime | None:
        divs = bs.find_all("div")
        for div in divs:
            if div.get("class") is not None and "publication-info" in div.get("class"):
                parsed_date = re.findall(r"([A-Z]\w* \d*, \d*)", div.text)
                publishing_date = datetime.strptime(parsed_date[0], "%b %d, %Y")
                if verbose:
                    header_str = colored("Publishing date: ", "yellow", attrs=["bold"])
                    cprint(header_str, end="")
                    print(publishing_date)
                return publishing_date
        return None

    @staticmethod
    def get_page_text(bs: BeautifulSoup, verbose: bool = False) -> list[str]:
        plain_paragraph_list = []
        paragraph = ""
        count = 1
        if bs.p is None:
            return plain_paragraph_list
        for sibling in bs.p.next_siblings:
            if sibling.name in ["p", "ul"]:
                paragraph += sibling.text
                count += 1
            if sibling.name in ["h1", "h2", "h3"] or count == 3:
                if (
                        paragraph != ""
                        and len(paragraph) > 80
                        and "https://" not in paragraph
                ):
                    paragraph.replace("\t", "  ")
                    plain_paragraph_list.append(paragraph)
                paragraph = ""
                count = 1

        if verbose:
            header_str = colored("Parsed paragraphs: ", "yellow", attrs=["bold"])
            cprint(header_str, end="")
            pprint(len(plain_paragraph_list))

        return plain_paragraph_list

    def save(
            self,
            documents: list[str],
            ids: list[str],
            metadata: list[dict],
            verbose: bool = False,
    ):
        if verbose:
            cprint("Saving into database...\n", "yellow", attrs=["bold"])

        self.collection.upsert(
            documents=documents,
            ids=ids,
            metadatas=metadata,
        )

    @staticmethod
    def has_url_in(url, url_list):
        visited = False
        url_split = url.split("/")
        page_title = url_split[-1] if url_split[-1] != "" else url_split[-2]
        for registered_url in url_list:
            visited = page_title in registered_url.split("/")
            if visited:
                break
        return visited

    def parse_blog_pages_links(self, bs: BeautifulSoup, is_xml: bool, url: str):
        if is_xml:
            unparsed_links = bs.find_all("loc")
            re_pattern = r">https://cheesecakelabs.com/blog/.*?<"
        else:
            unparsed_links = bs.find_all("a")
            re_pattern = r'"https://cheesecakelabs.com/blog/.*?"'
        for unparsed_link in unparsed_links:
            parsed = re.findall(re_pattern, str(unparsed_link))

            # Filter pages that we don't want the scraper to visit
            filters = []
            if len(parsed) > 0:
                parsed = parsed[0].replace('"', "")
                parsed = parsed.replace(">", "")
                parsed = parsed.replace("<", "")
                parsed = parsed.split("#", 1)[0]
                filters.append(not self.has_url_in(parsed, self.urls_to_visit))
                filters.append(parsed.find("category") == -1)
                filters.append(parsed.find("services") == -1)
                filters.append(parsed.find("autor") == -1)
                filters.append(parsed.find("wp-content") == -1)
                filters.append(parsed.find("portfolio") == -1)
                filters.append(parsed.find("br") == -1)
                filters.append(parsed.find(".png") == -1)
                filters.append(parsed.find(".jpg") == -1)
                filters.append(parsed.find(".gif") == -1)
                filters.append(
                    parsed
                    not in [
                        "https://cheesecakelabs.com/blog/",
                        "https://cheesecakelabs.com/blog/br/",
                        "https://cheesecakelabs.com/blog/blog/",
                        "https://cheesecakelabs.com/blog/contact/",
                        "https://cheesecakelabs.com/blog/br/carreiras/",
                        "https://cheesecakelabs.com/blog/br/contato/",
                        "https://cheesecakelabs.com/blog/careers/",
                    ]
                )

                if all(filters):
                    self.urls_to_visit.append(parsed)

        self.visited_links.append(url)
        self.url_index += 1
