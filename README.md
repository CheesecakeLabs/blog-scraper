# Cheesecake Blog Scraper

This project is a PoC to create a vector database from content scrapped from web pages. Here we
use [ChromaDB](https://docs.trychroma.com/) as the vector database technology and
the [Amazon Titan](https://aws.amazon.com/bedrock/titan/) embedding model, but the project also
support [BAAI/bge-large-zh-v1.5](https://huggingface.co/BAAI/bge-large-zh), available on HuggingFace
website.

### How to install

To install the project is recommended to use python 3.11 and a virtual environment:

```shell
virtualenv -p python3.11 venv
source venv/bin/activate
make setup-dev 
```

If one is using a computer with ARM architecture, is important to set the architecture during dependencies installation.

```shell
make setup-dev-arm64
```

### How to run

Firstly, set up the environment variables by copying the `config/.env.example` file and
creating `config/.env.development`. The following variables are crucial to connect to AWS Bedrock service if running
with AWS embedding model.

```
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_SESSION_TOKEN=
```

#### On Docker container

To run the scraper app inside a Docker container just run the following command:

```shell
make docker-start
```

#### locally

To run locally we still need to run ChromaDB on a container before starting the scraper app.

```shell
make docker-start-db
python main.py -verbose -store_on_database -continue_scrapping

```

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
   inconsistencies. Run the script `tsv-formatter.py` and load the files embedding.tsv and metadata.tsv in the
   TensorFlow Project page.

TODO:

1. Fix scraper logs
2. Make scraper container run automatically
