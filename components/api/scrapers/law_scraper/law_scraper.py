from datetime import datetime
from itertools import count
from json import dump
from os import makedirs, path
from pathlib import Path
from re import search

from bs4 import BeautifulSoup, Tag
from markdownify import MarkdownConverter
from models import LawArticle, LawChapter, LawInfo
from pandas import read_csv
from requests import Session


class LawInfoScraper:
    def __init__(self, law_urls_file: str):
        self.law_urls_file: Path = Path(__file__).parent / law_urls_file
        self.session: Session = Session()
        self.converter: MarkdownConverter = MarkdownConverter()
        self.law_chapters: dict[str, dict[str, str]] = {}
        self.law_articles: dict[str, dict[str, str]] = {}
        self.date = datetime.now().strftime("%Y-%m-%d")

    def _read_laws_to_dict(self) -> dict:
        law_urls = read_csv(self.law_urls_file)
        return law_urls.to_dict(orient="index")

    def _get_law_info(self) -> dict[str, LawInfo]:
        laws_metadata = self._read_laws_to_dict()
        laws: dict[str, LawInfo] = {}

        for law in laws_metadata:
            laws[laws_metadata[law]["title"]] = LawInfo(
                id=laws_metadata[law]["id"],
                title=laws_metadata[law]["title"],
                description=laws_metadata[law]["description"],
                url=laws_metadata[law]["url"],
            )
        return laws

    def get_law(self, law: LawInfo) -> BeautifulSoup:
        response = self.session.get(law.url)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup

    def _get_chapter_id_and_title(self, chapter: Tag, i: int) -> tuple[str, str]:
        try:
            chapter_h3 = chapter.find("h3")
            if not chapter_h3:
                chapter_id = f"unknown_id_{i}"
                chapter_title = ""
            else:
                chapter_id = chapter_h3["id"]
                chapter_title = chapter_h3.text
                return chapter_id, chapter_title
        except KeyError:
            chapter_id = f"unknown_id_{i}"
            chapter_title = "unknown_title"

        return chapter_id, chapter_title

    def _get_chapter_content(self, chapter: Tag) -> str:
        return self.converter.convert(chapter.prettify())

    def _get_chapter_url(self, chapter: Tag) -> str:
        try:
            url = str(chapter.find(class_="popuppermanentelink")["href"])
        except KeyError:
            return "unknown_url"
        return url

    def get_law_chapters(self, law: BeautifulSoup, law_name: str) -> dict[str, str]:
        chapters_dict: dict[str, str] = {}

        chapters = law.find_all(
            class_="article__header--law article__header--law--chapter"
        )
        for i, chapter_html in enumerate(chapters):

            chapter_id, chapter_title = self._get_chapter_id_and_title(chapter_html, i)
            chapter_url = self._get_chapter_url(chapter_html)
            chapter_body = self._get_chapter_content(chapter_html)

            chapters_dict[chapter_title] = LawChapter(
                id=i,
                law_name=law_name,
                chapter_id=chapter_id,
                title=chapter_title,
                body=chapter_body,
                url="".join(["https://wetten.overheid.nl", chapter_url]),
                date=self.date,
            ).model_dump()
        return chapters_dict

    def _get_article_number_from_title(self, article_title: str) -> str:
        res = search(r"\s(\d+(\.?(\d+)?\.?(\w)?\.?))\s", article_title)
        try:
            return str(res.groups()[0])
        except:
            return "unknown_article_number"

    def _get_article_id_title_and_number(self, article: Tag, i: int) -> tuple[str, str]:
        try:
            article_h4 = article.find("h4")
            if not article_h4:
                article_id = f"unknown_id_{i}"
                article_title = ""
                article_number = ""
            else:
                article_id = article_h4["id"]
                article_title = article_h4.text
                article_number = self._get_article_number_from_title(article_title)
                return article_id, article_title, article_number
        except KeyError:
            article_id = f"unknown_id_{i}"
            article_title = "unknown_title"
            article_number = ""

        return article_id, article_title, article_number

    def _get_article_content(self, article: Tag, article_title: str) -> str:
        try:
            article.find(
                "ul",
                {"aria-label": f"Lijst met mogelijke acties voor {article_title}."},
            ).decompose()
        except AttributeError:
            return self.converter.convert(article.prettify())
        return self.converter.convert(article.prettify())

    def _get_article_url(self, article: Tag) -> str:
        try:
            url = article.find(class_="popuppermanentelink")["href"]
        except KeyError:
            return "unknown_url"
        return url

    def get_law_articles(
        self, law: BeautifulSoup, law_name: str
    ) -> dict[str, LawArticle]:
        article_dict: dict[str, str] = {}

        articles = law.find_all(class_="artikel")

        count = 0

        for article in articles:
            if not 'div class="artikel" id="Hoofdstuk' in str(article):
                continue
            count += 1

            article_id, article_title, article_number = (
                self._get_article_id_title_and_number(article, count)
            )

            article_url = self._get_article_url(article)
            article_body = self._get_article_content(article, article_title)

            article_dict[article_number] = LawArticle(
                id=count,
                law_name=law_name,
                article_id=article_id,
                article_number=article_number,
                title=article_title,
                body=article_body,
                url="".join(["https://wetten.overheid.nl", article_url]),
                date=self.date,
            ).model_dump()
        return article_dict

    def save_law_articles(self) -> None:
        print("Saving law articles...")
        if not path.exists(Path(__file__).parent.parent / "laws/articles"):
            makedirs(Path(__file__).parent.parent / "laws/articles")
        dump(
            self.law_articles,
            open(Path(__file__).parent / "law_articles.json", "w"),
            indent=2,
        )
        print("Finished saving law articles.")

    def run(self) -> None:
        print("Running law scraper...")
        self.law_info: dict[str, LawInfo] = self._get_law_info()
        laws: dict[str, BeautifulSoup] = {}

        for law_name, law in self.law_info.items():
            laws[law_name] = self.get_law(law)
            self.law_chapters[law_name] = self.get_law_chapters(
                laws[law_name], law_name
            )
            self.law_articles[law_name] = self.get_law_articles(
                laws[law_name], law_name
            )

        print("Finished scraping laws.")


if __name__ == "__main__":
    # TODO: Use argparser to pass the law_urls_file, but default to "law_urls.csv"
    scraper = LawInfoScraper("law_urls.csv")
    scraper.run()
    scraper.save_law_articles()
