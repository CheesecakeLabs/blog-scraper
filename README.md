# Cheesecake Blog Scraper

This project is a PoC to create a vector database from content scrapped from web pages. Here we
use [ChromaDB](https://docs.trychroma.com/) as the vector database technology and
the [BAAI/bge-large-zh-v1.5](https://huggingface.co/BAAI/bge-large-zh) embedding model, available on HuggingFace
website.

### How to install

To install the project is recommended to use python 3.11 and a virtual environment:

```shell
virtualenv -p python3.11 venv
source venv/bin/activate
pip install -r requirements.txt --no-cache 
```

If one is using a PC with ARM architecture, is important to set the architecture during dependencies installation.

```shell
arch -arm64 pip install -r requirements.txt --no-cache 
```

### How to run

`python main.py -verbose -store_on_database -continue_scrapping`

The `main.py` script has 3 important flags: that help to understand what is happening.

1. `-verbose`: (default is False) Print information about the process of scrapping pages, creating embeddings and store
   data into de database.
2. `-store_on_database`: (default is False) Force the scraper to store content and embeddings into de database.
3. `-continue_scrapping`: (default is False) Force the scrapper to visit new blog page links found inside the scrapped
   page. This is a recursive process.

### Analysing the database

After run the main script and hydrate the database we can check the data in two ways.

1. run `test_queries.py` and check the related answers.
2. Use the [TensorFlow Project](https://projector.tensorflow.org/) to analyse the vectors and try to identify
   inconsistencies. Run the script `tsv-formatter.py` and load the files embedding.tsv and metadata.tsv in the TensorFlow Project page. 

### TODOs

There are some knowing issues in this project where improvements are welcome.

1. There are a few duplicated entries on the database. Which can mean that the scraper is visiting the same page more
   than once

For example, the following URLs were found in pages links, both are different, but they point to the same content:

https://cheesecakelabs.com/blog/blog/css-architecture-first-steps/

https://cheesecakelabs.com/blog/css-architecture-first-steps/

2. The total number of visited pages is about 165, but today exist about 231 pages with english content in the blog. So
   it is necessary to reach the remaining ones.
