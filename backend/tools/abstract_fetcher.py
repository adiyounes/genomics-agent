import httpx
from xml.etree import ElementTree as ET

EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

def parse_articles(xml_text: str) -> list[dict]:
    
    root = ET.fromstring(xml_text)
    articles = []

    for article_node in root.findall(".//PubmedArticle"):
        #PMID
        pmid_node = article_node.find(".//PMID")
        pmid = pmid_node.text if pmid_node is not None else "unknown"
        #Title
        title_node = article_node.find(".//ArticleTitle")
        title = title_node.text if title_node is not None else "No title available"
        #removing punctuation
        title = title.strip(".").strip()
        #abstract "some articals have miltiple abstract text, we join all the sections"
        abstract_nodes = article_node.findall(".//AbstractText")
        if abstract_nodes:
            parts = []
            for node in abstract_nodes:
                label = node.get("Label")
                text = node.text or ""
                if label:
                    parts.append(f"{label}: {text}")
                else:
                    parts.append(text)
            abstract = "".join(parts).strip()
        else:
            abstract = None
        #Authors (I only take the first three authors)
        authors =[]
        authors_nodes = article_node.findall(".//Author")
        if authors_nodes:
            for node in authors_nodes[:3]:
                last = node.findtext("LastName","")
                initials = node.findtext("initials","")
                authors.append(f"{last} {initials}".strip())
        if len(authors_nodes) > 3:
            authors.append("et al.")
        author_string = ", ".join(authors)
        #Year
        year = "Unknown year"
        for year_path in [
            ".//JournalIssue/PubDate/Year",
            ".//PubDate/Year",
            ".//DateCompleted/Year",
        ]:
          year_node = article_node.find(year_path)
          if year_node is not None and year_node.text:
              year = year_node.text
              break 
        #Journal
        journal_node = article_node.find(".//Journal/Title")
        journal = journal_node.text if journal_node is not None else "Unknown journal"
        
        #only including articles with an abstract
        if abstract:
            articles.append(
                {
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "authors": author_string,
                "journal":journal,
                "year": year,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                }
            )
    return articles

async def fetch_abstracts(pmids: list[str]) -> dict:
    if not pmids:
        return {
            "articles":[],
            "fetched": 0,
            "error": "No PMIDs provided — Tool 1 may have returned empty results.",
        }
    
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "rettype": "xml",
        "retmode": "xml",
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(EFETCH_URL, params=params)
            response.raise_for_status()
        
        articles = parse_articles(response.text)

        return{
            "articles": articles,
            "fetched": len(articles),
            "error": None,
        }
    except ET.ParseError as e:
        return {
            "articles": [],
            "fetched": 0,
            "error": f"Failed to parse PubMed XML: {str(e)}",
        }
    except httpx.TimeoutException:
        return {
            "articles": [],
            "fetched": 0,
            "error": "PubMed efetch request timed out after 20 seconds.",
        }
    except httpx.HTTPStatusError as e:
        return {
            "articles": [],
            "fetched": 0,
            "error": f"PubMed returned HTTP {e.response.status_code}.",
        }
    except Exception as e:
        return {
            "articles": [],
            "fetched": 0,
            "error": f"Unexpected error: {str(e)}",
        }