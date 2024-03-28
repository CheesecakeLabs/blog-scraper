FROM python:3.11-slim
ENV DEPLOY_STAGE=local
WORKDIR /usr/src/app

COPY . .
RUN pip install --no-cache-dir -r ./config/requirements.txt


ENTRYPOINT [ "python", "main.py", "-verbose", "-continue-scrapping", "-store-on-database"]
