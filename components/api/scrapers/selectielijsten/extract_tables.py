from pathlib import Path

import camelot
import pandas as pd
import pdfplumber
from tabulate import tabulate


def extract_tables_from_pdf(pdf_path: str, start_page: int = 0, end_page: int = None):
    """
    Extract tables from a PDF file using pdfplumber.
    """
    with pdfplumber.open(pdf_path) as pdf:
        # pages_to_extract = [4]  # List of pages to extract tables from (0-indexed)
        pages_to_extract = range(
            start_page, end_page
        )  # List of pages to extract tables from (0-indexed)
        for page_number in pages_to_extract:
            page = pdf.pages[page_number]
            tables = page.extract_tables()
            for page_number in pages_to_extract:
                page = pdf.pages[page_number]
                tables = page.extract_tables()
                for table in tables:
                    df = pd.DataFrame(table)  # Convert to Pandas DataFrame
                    # df['Page'] = page_number + 1  # Add a column with the page number (1-indexed)

                with open(f"output_page{page_number+1}.md", "w") as f:
                    f.write(df.to_markdown(index=False))
                    f.write("\n\n")


def extract_tables_camelot(pdf_path: str, output_md: str):
    """
    Extract tables from a PDF using Camelot and save them as Markdown.
    """
    tables = camelot.read_pdf(pdf_path, pages="4,12,13,14")  # Specify pages

    for i, table in enumerate(tables):
        df = table.df  # Convert table to Pandas DataFrame
        # df["Page"] = tables[i].page  # Add page number

        # Convert DataFrame to Markdown
        markdown_table = tabulate(
            df, headers="keys", tablefmt="github", showindex=False
        )
        # Save the markdown output to a file
        with open(f"{output_md}_table_{i+1}.md", "w") as f:
            f.write(markdown_table)
            f.write("\n\n")

    print(f"Extracted {len(tables)} tables and saved as markdown.")


if __name__ == "__main__":
    pdf_path = Path("pdfs/waterschappen.pdf")
    extract_tables_from_pdf(pdf_path, 12, 50)
    # output_md = "output"
    # extract_tables_camelot(pdf_path, output_md)
