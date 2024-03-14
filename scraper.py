import re
import chromadb
import requests

from datetime import datetime
from pprint import pprint
from typing import Union, List
from numpy import ndarray
from torch import Tensor
from bs4 import BeautifulSoup
from termcolor import colored, cprint
from embedding import EmbeddingModel


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

        if store_on_database:
            self.client = chromadb.PersistentClient(path="./chromadb")
            # Uncomment this line if you want to delete the collection and start from scratch
            # self.client.delete_collection(name=f"cheesecake-blog")
            self.collection = self.client.get_or_create_collection(
                name=f"cheesecake-blog"
            )
            cprint("ChromaDB initialized.", "yellow", attrs=["bold"])

    def visit_page(
            self,
            url: str,
            continue_scrapping: bool = True,
            verbose: bool = False,
    ):
        if url not in self.visited_links:
            if verbose:
                header_str = colored("Visiting: ", "yellow", attrs=["bold"])
                cprint(header_str, end="")
                print(url, flush=True)

            response = requests.get(url)
            bs = BeautifulSoup(response.text, "html.parser")
            title = self.get_page_title(bs, verbose)
            publishing_date = self.get_page_publishing_date(bs, verbose)
            paragraphs = self.get_page_text(bs, verbose)

            if self.store_on_database:
                embeddings = self.get_embeddings(paragraphs, verbose)
                if len(embeddings) > 0:
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
                    index_limit = len(embeddings) + self.database_index
                    ids = [str(i) for i in range(self.database_index, index_limit)]
                    self.database_index += len(embeddings)
                    self.save(paragraphs, ids, embeddings, metadata, verbose)

            if continue_scrapping:
                self.parse_blog_pages_links(bs, url)

                if self.url_index < len(self.urls_to_visit):
                    self.visit_page(
                        self.urls_to_visit[self.url_index], continue_scrapping, verbose
                    )

    @staticmethod
    def get_page_title(bs: BeautifulSoup, verbose: bool = False) -> str:
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
        unparsed_text = bs.find_all("p")
        for unparsed_paragraph in unparsed_text:
            plain_paragraph_str = (
                unparsed_paragraph.text
            )  # Get the text content of the paragraph
            if len(plain_paragraph_str) > 50:
                plain_paragraph_list.append(plain_paragraph_str)

        if verbose:
            header_str = colored("Parsed paragraphs: ", "yellow", attrs=["bold"])
            cprint(header_str, end="")
            pprint(len(plain_paragraph_str))
        return plain_paragraph_list

    @staticmethod
    def get_embeddings(paragraphs: list[str], verbose: bool = False):
        embedding_model = EmbeddingModel()
        if verbose:
            cprint("Calculating text embeddings...", "yellow", attrs=["bold"])
        embeddings = embedding_model.get_embedding(paragraphs)
        if verbose:
            cprint(f"Embeddings length: {len(embeddings)}", "yellow", attrs=["bold"])
        return embeddings

    def save(
            self,
            documents: list[str],
            ids: list[str],
            embeddings: Union[List[Tensor], ndarray, Tensor],
            metadata: list[dict],
            verbose: bool = False,
    ):
        if verbose:
            cprint("Saving into database...", "yellow", attrs=["bold"])

        self.collection.upsert(
            documents=documents,
            ids=ids,
            embeddings=embeddings,
            metadatas=metadata,
        )

    def parse_blog_pages_links(self, bs: BeautifulSoup, url: str):
        unparsed_links = bs.find_all("a")
        for unparsed_link in unparsed_links:
            parsed = re.findall(
                r'"https://cheesecakelabs.com/blog/.*?"', str(unparsed_link)
            )

            # Filter pages that we don't want the scraper to visit
            filters = []
            if len(parsed) > 0:
                parsed = parsed[0].replace('"', "")
                filters.append(parsed not in self.urls_to_visit)
                filters.append(parsed.find("category") == -1)
                filters.append(parsed.find("services") == -1)
                filters.append(parsed.find("autor") == -1)
                filters.append(parsed.find("br") == -1)
                filters.append(
                    parsed
                    not in [
                        "https://cheesecakelabs.com/blog/",
                        "https://cheesecakelabs.com/blog/br/",
                        "https://cheesecakelabs.com/blog/blog/",
                        "https://cheesecakelabs.com/blog/br/contact/",
                        "https://cheesecakelabs.com/blog/br/carreiras/",
                        "https://cheesecakelabs.com/blog/br/contato/",
                        "https://cheesecakelabs.com/blog/careers/",
                    ]
                )

                if all(filters):
                    self.urls_to_visit.append(parsed)

        self.visited_links.append(url)
        self.url_index += 1
