import httpx
from datetime import datetime

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

def build_query(gene_name: str, condition_name: str, refined: bool = False) -> str:
    year = datetime.now().year
    date_range = f"{year - 3}:{year}[PDAT]"

    if not refined:
        return(
            f"{gene_name}[Gene Name] AND "
            f"{condition_name}[MeSH Terms] AND "
            f"{date_range}"
        )
    else:
        return(
            f"({gene_name}[Title/Abstract] OR {gene_name}[Gene Name]) AND "
            f"({condition_name}[Title/Abstract] OR {condition_name}[MeSH Terms]) AND "
            f"{date_range}"
        )
    
async def search_pubmed(
   gene_name: str,
   condition_name: str,
   max_results: int=5,
   refined: bool = False,
) -> dict:
    
    query = build_query(gene_name, condition_name, refined=refined)

    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmod": "json",
        "sort": "relevance",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(ESEARCH_URL, params=params)
            response.raise_for_status()

        data = response.json()
        result_data = data.get("esearchresult",{})

        pmids = result_data.get("idlist", [])
        total_found = int(result_data.get("count",0))

        return {
            "query": query,
            "pmids": pmids,
            "total_found": total_found,
            "error": None,
        }
    
    except httpx.TimeoutException:
        return {
            "query": query,
            "pmids": [],
            "total_found": 0,
            "error": "PubMed request timed out after 15 seconds.",
        }
    
    except httpx.HTTPStatusError as e:
        return {
            "query": query,
            "pmids": [],
            "total_found": 0,
            "error": f"PubMed returned HTTP {e.response.status_code}.",
        }
    
    except Exception as e:
        return {
            "query": query,
            "pmids": pmids,
            "total_found": total_found,
            "error": f"Unexpected error: {str(e)}",
        }