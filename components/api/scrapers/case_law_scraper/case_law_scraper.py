"""
This script scrapes case law from the Dutch judiciary website and converts it to Markdown format.

Please note that this script does not format the case law texts into json. That was done manually.
"""

from json import dump
from os import getcwd
from pathlib import Path

from bs4 import BeautifulSoup
from markdownify import MarkdownConverter
from requests import Session

CASE_LAWS = [
    "https://uitspraken.rechtspraak.nl/details?id=ECLI:NL:RVS:2017:2211",
    "https://uitspraken.rechtspraak.nl/details?id=ECLI:NL:RVS:2021:153",
]

MAIN_PAGE_ELEMENTS = [
    "rnl-details printthis ng-star-inserted",
    "rnl-detail-uitspraaktekst printthis ng-star-inserted",
]


def main():
    for i in [1, 2]:
        file_path = (
            getcwd()
            / Path(__file__).parent.parent
            / "laws"
            / "case_law"
            / f"raw_html_0{i}.html"
        )

        with open(file_path, "r") as f:
            html = f.read()

        soup = BeautifulSoup(html, "html.parser")
        converter = MarkdownConverter()

        output_path = (
            getcwd()
            / Path(__file__).parent.parent
            / "laws"
            / "case_law"
            / f"markdown_output_0{i}.md"
        )

        with open(output_path, "w") as f:
            dump(converter.convert(soup.prettify()), f)


if __name__ == "__main__":
    main()
