import os
import anthropic


# reading ANTHROPIC_API_KEY from the environment
client = anthropic.Anthropic()

MODEL = "claude-sonnet-4-20250514"

def _build_summary_prompt(
        gene_name: str,
        condition_name: str,
        articles: list[dict],
) -> str:
    
    articles_text = ""
    for i, articles in enumerate(articles,1):
        articles_text += f"""
                            --- Paper {i} ---
                            Title: {article['title']}
                            Authors: {article['authors']}
                            Journal: {article['journal']} ({article['year']})
                            PMID: {article['pmid']}
                            Abstract: {article['abstract']}
                            """
        return f"""
                    You are a biomedical research assistant. Your job is to summarise recent
                    findings for a clinical genomics application.

                    The user wants to know about the latest research on the gene {gene_name.upper()}
                    in relation ro {condition_name}.

                    Here are {len(articles)} recent papers from PubMed

                    {articles_text}

                    Your task:
                    1. Read all abstracts carefully
                    2. Identify the most important and clinically relevant findings
                    3. Write a summary of 3-5 bullet points

                    Rules you must follow:
                    -Each bullet point must start with a dash and a space:"- "
                    -Each bullet point should be 1-2 sentences, specific and informative
                    -include the PMID reference at the end of each bullet in parentheses, like
                    :(PMID:31257864)
                    -Focus on findings, not methodology
                    -Use plain language, avoid excessive jargon 
                    -If papers have conflicting findings, mention this
                    -Do not include any text before the first bullet point or after the last one

                    Exemple of correct format:
                    -  BRCA1 pathogenic variants are associated with a 72% lifetime risk of
                    riple-negative breast cancer, significantly higher than the general
                    opulation risk of 12%. (PMID: 38901234)
                    - Combining polygenic risk scores with BRCA1 status improves risk stratification
                     and supports more personalised screening intervals. (PMID: 38756432)
"""
    
async def summarize_abstracts(
        gene_name: str,
        condition_name: str,
        articles: list[dict],
) -> dict:

    if not articles:
        return {
            "summary": None,
            "sources": [],
            "error": "No articles to summarise",
        }
    
    prompt = build_summary_prompt(gene_name, condition_name, articles)

    try:
        response = client.messages.create(
            model= Model,
            max_tokens= 1000,
            messages = [{"role": "user", "content":prompt}]
        )

        summary = response.content[0].text.strip()

        #if Claude didn't return any bullet points for some reason
        if not any(line.startswith("- ") for line in summary.splitlines()):
            return {
                "summary": None,
                "sources": articles,
                "error": "LLM response was not in expected bullet point format"
            }
        
        return{
            "summary": summary,
            "sources": articles,
            "error": None
        }
    
    except anthropic.APIConnectionError:
        return {
            "summary": None,
            "sources": [],
            "error": "Could not connect to Anthropic API.",
        }
    except anthropic.RateLimitError:
        return {
            "summary": None,
            "sources": [],
            "error": "Anthropic API rate limit reached. Try again shortly.",
        }
    except anthropic.APIStatusError as e:
        return {
            "summary": None,
            "sources": [],
            "error": f"Anthropic API error {e.status_code}: {e.message}",
        }
    

def _build_relevance_prompt(
        gene_name: str,
        condition_name: str,
        summary: str,
) ->str:
    
    return f"""
                You are evaluating whether a research summary is relevant to a specific topc.

                Topic: The gene {gene_name.upper()} and its relationship to {condition_name}.
                
                Summary to evaluate:
                {summary}

                Is this summary relevant to the topic above?

                Answer with exactly one word, either RELEVANT or IRRELEVANT.
                Do not explain your reasoning. Do not add punctuation. Just the signle word.
"""




def grade_relevance(
        gene_name: str,
        condition_name: str,
        summary: str,
)-> bool:
    prompt = _build_relevance_prompt(gene_name, condition_name, summary)

    try:
        response=client.messages.create(
            model=MODEL,
            max_tokens=10,
            messages=[{"role": "user", "content": prompt}],
        )

        verdict = response.content[0].text.strip().upper()
        return verdict == "RELEVANT"
    
    except Exception:
        return True