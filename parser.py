from bs4 import BeautifulSoup
import re


def clean_text(val: str) -> str:
    if not val:
        return ""
    return re.sub(r"\s+", " ", val).strip()


