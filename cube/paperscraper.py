import re
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


# ============================================================
# CONFIG
# ============================================================

START_YEAR = 2010
END_YEAR = 2025

BASE_DIR = Path("papers")

SUBJECT = "Physical Sciences"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(X11; Linux x86_64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/140.0 Safari/537.36"
    )
}


# ============================================================
# KNOWN DBE ARCHIVE PAGES
# ============================================================

ARCHIVE_PAGES = {

    2025: [
        "https://www.education.gov.za/"
        "Curriculum/NationalSeniorCertificate%28NSC%29Examinations/"
        "2025NovemberExamPapers.aspx"
    ],

    2024: [
        "https://www.education.gov.za/"
        "2024NSCNovemberpastpapers.aspx"
    ],

    2023: [
        "https://www.education.gov.za/"
        "2023NSCNovemberpastpapers.aspx"
    ],

    2022: [
        "https://www.education.gov.za/"
        "Curriculum/NationalSeniorCertificate%28NSC%29Examinations/"
        "2022NovemberExams.aspx"
    ],

    2021: [
        "https://www.education.gov.za/"
        "Curriculum/NationalSeniorCertificate%28NSC%29Examinations/"
        "2021NSCNovemberExaminations.aspx"
    ],

    2020: [
        "https://www.education.gov.za/"
        "Curriculum/NationalSeniorCertificate%28NSC%29Examinations/"
        "2020NSCandSCExaminationPapersNovember.aspx"
    ],

    2019: [
        "https://www.education.gov.za/"
        "Curriculum/NationalSeniorCertificate%28NSC%29Examinations/"
        "2019NSCExaminationPapers.aspx"
    ],

    2018: [
        "https://www.education.gov.za/"
        "2018NSCNovemberpastpapers.aspx"
    ],

    2017: [
        "https://www.education.gov.za/"
        "Curriculum/NationalSeniorCertificate%28NSC%29Examinations/"
        "2017NSCNovemberpastpapers.aspx"
    ],

    2016: [
        "https://www.education.gov.za/"
        "Curriculum/NationalSeniorCertificate%28NSC%29Examinations/"
        "2016NSCNovemberpastpapers.aspx"
    ],

    2015: [
        "https://www.education.gov.za/"
        "Curriculum/NationalSeniorCertificate%28NSC%29Examinations/"
        "PastExamPapers/2015NovemberNSCExamPapers1/"
        "tabid/979/ItemId/12797/Default.aspx"
    ],

    2014: [
        "https://www.education.gov.za/"
        "Curriculum/NationalSeniorCertificate%28NSC%29Examinations/"
        "PastExamPapers/2014NSCNovemberExaminationPapers.aspx"
    ],

    2013: [
        "https://www.education.gov.za/"
        "Curriculum/NationalSeniorCertificate%28NSC%29Examinations/"
        "PastExamPapers/2013NSCNovemberExaminationPapers.aspx"
    ],

    2012: [
        "https://www.education.gov.za/"
        "Curriculum/NationalSeniorCertificate%28NSC%29Examinations/"
        "PastExamPapers/2012NSCNovemberExaminationPapers.aspx"
    ],

    2011: [
        "https://www.education.gov.za/"
        "Curriculum/NationalSeniorCertificate%28NSC%29Examinations/"
        "PastExamPapers/2011NSCNovemberExaminationPapers.aspx"
    ],

    2010: [
        "https://www.education.gov.za/"
        "Curriculum/NationalSeniorCertificate%28NSC%29Examinations/"
        "PastExamPapers/2010NSCNovemberExaminationPapers.aspx"
    ],
}


# ============================================================
# HTTP
# ============================================================

session = requests.Session()
session.headers.update(HEADERS)


def get_page(url: str):

    print(f"  Opening: {url}")

    response = session.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    return response.text


# ============================================================
# FIND PHYSICAL SCIENCES SECTION
# ============================================================

def find_physical_sciences_section(soup):

    text = soup.get_text(
        " ",
        strip=True
    )

    index = text.lower().find(
        SUBJECT.lower()
    )

    if index == -1:
        return None

    # Find a heading containing Physical Sciences
    for heading in soup.find_all(
        ["h1", "h2", "h3", "h4", "h5", "h6"]
    ):

        if SUBJECT.lower() in heading.get_text(
            " ",
            strip=True
        ).lower():

            return heading

    return None


# ============================================================
# CLASSIFY DOCUMENT
# ============================================================

def classify_document(text: str):

    text = re.sub(
        r"\s+",
        " ",
        text.lower()
    ).strip()

    # Ignore Afrikaans-only papers.
    # Physical Sciences memos on DBE are often combined
    # English & Afrikaans, so those are allowed.

    if "paper 1" in text:

        if "afrikaans" in text and "english" not in text:
            return None

        return "paper1"

    if "paper 2" in text:

        if "afrikaans" in text and "english" not in text:
            return None

        return "paper2"

    if "memo 1" in text:

        if "afrikaans" in text and "english" not in text:
            return None

        return "memo1"

    if "memo 2" in text:

        if "afrikaans" in text and "english" not in text:
            return None

        return "memo2"

    return None


# ============================================================
# FIND DOWNLOAD LINKS
# ============================================================

def find_documents(html: str, page_url: str):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    heading = find_physical_sciences_section(
        soup
    )

    if heading is None:

        print(
            "  Could not locate Physical Sciences section."
        )

        return {}

    results = {}

    # --------------------------------------------------------
    # The DBE pages normally place the subject links after
    # the Physical Sciences heading.
    # --------------------------------------------------------

    for element in heading.find_all_next(
        limit=150
    ):

        # Stop when another major subject heading begins.
        if (
            element.name in ["h1", "h2"]
            and element is not heading
        ):
            break

        if element.name != "a":
            continue

        href = element.get(
            "href"
        )

        if not href:
            continue

        label = element.get_text(
            " ",
            strip=True
        )

        document_type = classify_document(
            label
        )

        if document_type is None:
            continue

        absolute_url = urljoin(
            page_url,
            href
        )

        # Don't overwrite the first valid link.
        if document_type not in results:

            results[document_type] = {
                "label": label,
                "url": absolute_url
            }

    return results


# ============================================================
# DOWNLOAD
# ============================================================

def download_file(
    year: int,
    document_type: str,
    url: str
):

    year_dir = BASE_DIR / str(year)

    year_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = f"{document_type}.pdf"

    destination = year_dir / filename

    if destination.exists():

        print(
            f"    Already exists: {destination}"
        )

        return True

    print(
        f"    Downloading {document_type}:"
    )

    print(
        f"    {url}"
    )

    try:

        response = session.get(
            url,
            timeout=60
        )

        response.raise_for_status()

        content_type = response.headers.get(
            "Content-Type",
            ""
        ).lower()

        data = response.content

        # ----------------------------------------------------
        # Basic validation.
        # ----------------------------------------------------

        if not data.startswith(b"%PDF"):

            print(
                "    WARNING: response does not "
                "look like a PDF."
            )

            print(
                f"    Content-Type: {content_type}"
            )

            return False

        destination.write_bytes(
            data
        )

        print(
            f"    Saved: {destination}"
        )

        return True

    except Exception as e:

        print(
            f"    ERROR: {e}"
        )

        return False


# ============================================================
# PROCESS YEAR
# ============================================================

def process_year(year: int):

    print()
    print("=" * 60)
    print(f"YEAR: {year}")
    print("=" * 60)

    urls = ARCHIVE_PAGES.get(
        year,
        []
    )

    if not urls:

        print(
            "No archive URL configured."
        )

        return

    documents = {}

    for page_url in urls:

        try:

            html = get_page(
                page_url
            )

            found = find_documents(
                html,
                page_url
            )

            documents.update(
                found
            )

            if found:
                break

        except Exception as e:

            print(
                f"  Failed page: {e}"
            )

    if not documents:

        print(
            "  No Physical Sciences documents found."
        )

        return

    print()
    print("  Documents found:")

    for document_type, info in documents.items():

        print(
            f"    {document_type}: "
            f"{info['label']}"
        )

    print()

    for document_type in [
        "paper1",
        "paper2",
        "memo1",
        "memo2"
    ]:

        if document_type not in documents:

            print(
                f"    MISSING: {document_type}"
            )

            continue

        download_file(
            year,
            document_type,
            documents[document_type]["url"]
        )

        time.sleep(
            0.5
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("NSC PHYSICAL SCIENCES DOWNLOADER")
    print("=" * 60)
    print()
    print(
        f"Years: {START_YEAR} - {END_YEAR}"
    )
    print(
        "Source: South African Department of "
        "Basic Education"
    )
    print()

    BASE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    for year in range(
        START_YEAR,
        END_YEAR + 1
    ):

        process_year(
            year
        )

        time.sleep(
            1
        )

    print()
    print("=" * 60)
    print("DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()