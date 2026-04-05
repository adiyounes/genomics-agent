from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
from agent import run_research_agent

load_dotenv() #reads .env and puts vars into os.environ

app = FastAPI(title="Genomics Reasearch Agent")

#Allow the React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    gene_name: str
    condition_name: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/research")
async def research(request: ResearchRequest):
    if not request.gene_name.strip() or not request.condition_name.strip():
        raise HTTPException(status_code=422, detail="gene_name and condition_name are required")
    
    result = await run_research_agent(
        gene_name=request.gene_name.strip(),
        condition_name=request.condition_name.strip(),
    )

    if not result['success'] and result['error']:
        raise HTTPException(status_code=500, detail=result['error'])
    
    return result