import json
from os import makedirs, path
from pathlib import Path

if __name__ == "__main__":
    print("Dividing law articles...")
    json_file: str = "law_articles.json"
    with open(Path(__file__).parent / json_file, "r") as f:
        law_articles = json.load(f)

    for law_name, articles in law_articles.items():
        for article_number, article in articles.items():

            _article_number: str = article_number.strip(".")

            article_file: str = f"laws/articles/{law_name}_{_article_number}.json"

            with open(Path(__file__).parent.parent / article_file, "w") as f:
                json.dump(article, f, indent=2)
    print("Finished dividing law articles.")
