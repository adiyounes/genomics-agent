"""
Test the full ReAct agent end to end.
Run from backend/ folder:

    python3 test_agent.py
"""
import asyncio
from dotenv import load_dotenv
load_dotenv()

from agent import run_research_agent

async def main():
    print("\n=== Test 1: Normal case (should succeed first attempt) ===")
    result = await run_research_agent("BRCA1", "breast cancer")
    print(f"\nSuccess:     {result['success']}")
    print(f"Attempts:    {result['attempts']}")
    print(f"Final query: {result['final_query']}")
    print(f"Warning:     {result['warning']}")
    print(f"Error:       {result['error']}")
    print(f"\nSummary:\n{result['summary']}")
    print(f"\nSources: {len(result['sources'])} articles")

    print("\n=== Test 2: Obscure query (should trigger retry) ===")
    result2 = await run_research_agent("TP53", "aging")
    print(f"\nSuccess:  {result2['success']}")
    print(f"Attempts: {result2['attempts']}")
    print(f"Warning:  {result2['warning']}")
    if result2['summary']:
        print(f"\nSummary:\n{result2['summary']}")

asyncio.run(main())