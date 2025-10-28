FROM python:3.12.7

RUN useradd wegwijs
ADD requirements.txt .
RUN pip3 install -r requirements.txt

RUN [ "python3", "-c", "import nltk; nltk.download('stopwords', download_dir='/usr/local/nltk_data')" ]

RUN mkdir /src
COPY src /src
WORKDIR /src

RUN mkdir /scrapers
COPY scrapers /scrapers

RUN mkdir /knowledge-graphs
COPY knowledge-graphs /knowledge-graphs

RUN chown -R wegwijs /src/
RUN chown -R wegwijs /scrapers/
RUN chown -R wegwijs /knowledge-graphs/

USER wegwijs

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

CMD ["gunicorn","-c=gunicorn_conf.py","main:app"]
