import asyncio
from tools.pubmed_search import search_pubmed
from tools.abstract_fetcher import fetch_abstracts
from tools.summarizer import summarize_abstracts, grade_relevance

MAX_RETRIES = 3

async def run_research_agent(gene_name:str, condition_name:str) -> dict:
    attempt = 0
    last_result = None

    while attempt < MAX_RETRIES:
        attempt += 1
        #broader refined query after the first try
        refined = attempt > 1

        print("[Agent] Acting: searching PubMed...")
        search_result = await search_pubmed(
            gene_name, condition_name,
            max_results=5,
            refined=refined,
        )

        #Observe: TOOL 1
        if search_result["error"]:
            return {
                "success": False,
                "summary": None,
                "sources": [],
                "attempts": attempt,
                "final_query":search_result["query"],
                "warning": None,
                "error": f"Tool 1 failed: {search_result['error']}",
            }
        
        if not search_result["pmids"]:
            if attempt < MAX_RETRIES:
                print("[Agent] observing: no results, retrying with refined query")
                continue
            return {
                "success": False,
                "summary": None,
                "sources": [],
                "attempts": attempt,
                "final_query": search_result["query"],
                "warning": None,
                "error": "PubMed returned no results after all retries.",
            }
        
        print(f"[Agent] observing: found {search_result['total_found']} papers, "
              f"fetching top {len(search_result['pmids'])}...")
        
        #ACT: TOOL 2
        print("[Agent] Acting: fetching abstracts...")
        fetch_result = await fetch_abstracts(search_result["pmids"])

        if fetch_result["error"]:
            return {
                "success": False,
                "summary": None,
                "sources": [],
                "attempts": attempt,
                "final_query": search_result["query"],
                "warning": None,
                "error": f"Tool 2 failed: {fetch_result['error']}",
            }
        
        if not fetch_result['articles']:
            if attempt < MAX_RETRIES:
                print("[Agent] Observing: no abstracts found, retrying...")
                continue
            return {
                "success": False,
                "summary": None,
                "sources": [],
                "attempts": attempt,
                "final_query": search_result["query"],
                "warning": None,
                "error": "No usable abstracts found after all retries.",
            }
        
        print(f"[Agent] observing: retrieved {fetch_result['fetched']} abstracts...")
        

        #ACT: TOOL 3

        print("[Agent] Acting: summarizing with Claude...")
        summary_result= await summarize_abstracts(gene_name,condition_name,fetch_result['articles']
                                            )
        if summary_result['error']:
            return{
                "success": False,
                "summary": None,
                "sources": [],
                "attempts": attempt,
                "final_query": search_result["query"],
                "warning": None,
                "error": f"Tool 3 failed: {summary_result['error']}",
            }
        
        #Observe: relevance check
        print("[Agent] observing: grading relevance...")
        is_relevant = grade_relevance(gene_name,condition_name,summary_result['summary']
                                      )
        last_result = {
            "success": True,
            "summary": summary_result["summary"],
            "sources": summary_result["sources"],
            "attempts": attempt,
            "final_query": search_result["query"],
            "warning": None,
            "error": None,
        }

        if is_relevant:
            print(f"[Agent] Observing: summary is RELEVANT after {attempt} attempts")
            return last_result
        
        print(f"[Agent] Observing: summary is IRRELEVANT"
              f"{'retrying...' if attempt < MAX_RETRIES else 'max retries reached'}")
        
        if last_result:
            last_result["warning"] = (
                f"Results may not be fully relevant after {MAX_RETRIES} attempts "
                "Try a more specific gene or condition"
            )
            return last_result
        
        return {
            "success": False,
            "summary": None,
            "sources": [],
            "attempts": MAX_RETRIES,
            "final_query": "",
            "warning": None,
            "error": "Agent failed to produce a result after all retries.",
        }