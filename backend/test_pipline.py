import asyncio
from dotenv import load_dotenv

load_dotenv()

from tools.pubmed_search import search_pubmed
from tools.abstract_fetcher import fetch_abstracts
from tools.summarizer import summarize_abstracts, grade_relevance

GENE = "BRCA1"
CONDITION = "breast cancer"

async def main():
    print("=" * 60)
    print(f"Testing pipeline: {GENE} + {CONDITION}")
    print("=" * 60)

    #TOOL_1

    print("\n[Tool 1] Searching PubMed...")
    search_result = await search_pubmed(GENE,CONDITION,max_results=5)

    if search_result["error"]:
        print(f"ERROR: {search_result['error']}")
        return
    
    print(f"  Query:       {search_result['query']}")
    print(f"  Total found: {search_result['total_found']} papers on PubMed")
    print(f"  Fetching:    {search_result['pmids']}")

    #TOOL_2

    print("\n[Tool 2] Fetching abstracts...")
    fetch_result = await fetch_abstracts(search_result["pmids"])
    print(f"  Raw fetch error: {fetch_result['error']}")

    if fetch_result["error"]:
        print(f"  ERROR: {fetch_result['error']}")
        return
 
    print(f"  Abstracts retrieved: {fetch_result['fetched']}")
    for article in fetch_result["articles"]:
        print(f"\n  - {article['title']}")
        print(f"    {article['authors']} | {article['journal']} ({article['year']})")
        print(f"    {article['url']}")
 
    #TOOL_3

    print("\n[Tool 3] Summarising with Claude...")
    summary_result = await summarize_abstracts(GENE, CONDITION, fetch_result["articles"])
 
    if summary_result["error"]:
        print(f"  ERROR: {summary_result['error']}")
        return
 
    print("\n  Summary:")
    for line in summary_result["summary"].splitlines():
        print(f"  {line}")

    #Relevance check

    print("\n[Relevance check] Grading summary...")
    is_relevant = grade_relevance(GENE, CONDITION, summary_result["summary"])
    print(f"  Result: {'RELEVANT ✓' if is_relevant else 'IRRELEVANT ✗ — agent would retry'}")
 
    print("\n" + "=" * 60)
    print("Pipeline test complete.")
    print("=" * 60)
 
 
asyncio.run(main())