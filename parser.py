from bs4 import BeautifulSoup
import re


def clean_text(val: str) -> str:
    if not val:
        return ""
    return re.sub(r"\s+", " ", val).strip()


def parse_job_cards(html: str) -> list[dict]:
    """Extracts basic job metadata cards from the search fragment HTML."""
    if not html or not html.strip():
        return []

    soup = BeautifulSoup(html, "lxml")
    cards = []

    for item in soup.find_all("li"):
        link_elem = item.find("a", class_=re.compile(r"base-card__full-link|job-search-card__url-link"))
        if not link_elem:
            # guest results sometimes put link right inside the card title
            link_elem = item.find("a")
        
        if not link_elem or not link_elem.get("href"):
            continue

        href = link_elem.get("href", "").split("?")[0]
        job_id = None
        m = re.search(r"-([0-9]{8,12})$", href)
        if m:
            job_id = m.group(1)
        else:
            # fallback to urn check in card
            entity_urn = item.find("div", {"data-entity-urn": True})
            if entity_urn:
                urn_val = entity_urn.get("data-entity-urn", "")
                if "jobPosting:" in urn_val:
                    job_id = urn_val.split("jobPosting:")[-1]

        if not job_id:
            continue

        title_tag = item.find("h3", class_=re.compile(r"base-search-card__title|job-search-card__title"))
        title = clean_text(title_tag.text) if title_tag else ""

        company_tag = item.find("h4", class_=re.compile(r"base-search-card__subtitle|job-search-card__subtitle"))
        company = clean_text(company_tag.text) if company_tag else ""

        location_tag = item.find("span", class_=re.compile(r"job-search-card__location"))
        location = clean_text(location_tag.text) if location_tag else ""

        date_tag = item.find("time")
        posted_date = date_tag.get("datetime", "").strip() if date_tag else ""

        cards.append({
            "job_id": job_id,
            "title": title,
            "company": company,
            "location": location,
            "posted_date": posted_date,
            "url": href,
        })

    return cards


def parse_job_detail(html: str) -> dict:
    if not html or not html.strip():
        return {}

    soup = BeautifulSoup(html, "lxml")
    body_elem = soup.find("div", class_=re.compile(r"show-more-less-html__markup|description__text"))
    if not body_elem:
        body_elem = soup.find("section", class_=re.compile(r"show-more-less-html"))

    criteria = {}
    for crit_item in soup.find_all("li", class_=re.compile(r"description__job-criteria-item")):
        header = crit_item.find("h3")
        val = crit_item.find("span")
        if header and val:
            k = clean_text(header.text).lower().replace(" ", "_")
            criteria[k] = clean_text(val.text)

    description = ""
    if body_elem:
        # strip script and style tags
        for s in body_elem(["script", "style"]):
            s.decompose()
        description = body_elem.get_text(separator="\n", strip=True)

    return {
        "description": description,
        "seniority_level": criteria.get("seniority_level", ""),
        "employment_type": criteria.get("employment_type", ""),
        "job_function": criteria.get("job_function", ""),
        "industries": criteria.get("industries", ""),
    }
