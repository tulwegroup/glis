"""
Semantic Search Endpoint for GLIS v4.0
RAG-powered legal question answering
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from reasoning.vector_store import vector_store, initialize_vector_store
import os

router = APIRouter(prefix="/api/search", tags=["search"])

# Initialize vector store on startup
if vector_store is None:
    initialize_vector_store()

class SemanticSearchRequest(BaseModel):
    query: str
    include_customary_law: bool = True

class SemanticSearchResponse(BaseModel):
    answer: str
    sources: list
    relevant_statutes: list
    customary_law_context: str = None
    practical_advice: str = None
    confidence_score: float

@router.post("/semantic", response_model=SemanticSearchResponse)
async def semantic_search(request: SemanticSearchRequest):
    """
    AI-powered semantic search of Ghana law
    Answers legal questions using RAG (Retrieval Augmented Generation)
    """
    try:
        # 1. Retrieve relevant documents from vector store
        search_results = vector_store.semantic_search(request.query, k=5)
        
        if not search_results:
            raise HTTPException(
                status_code=404,
                detail="No relevant legal documents found"
            )
        
        # 2. Build context from retrieved documents
        context = "\n\n".join([
            f"[{result['metadata'].get('title', 'Unknown')}]\n{result['content']}"
            for result in search_results
        ])
        
        # 3. Filter for customary law if requested
        customary_context = ""
        if request.include_customary_law:
            customary_results = [
                r for r in search_results 
                if r['metadata'].get('type') == 'customary'
            ]
            if customary_results:
                customary_context = "\n\n".join([
                    f"[{r['metadata'].get('ethnic_group', 'Customary')} Law]\n{r['content']}"
                    for r in customary_results
                ])
        
        # 4. Generate answer using GPT-4
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.2,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        prompt = ChatPromptTemplate.from_template("""
        You are an expert Ghanaian legal advisor. A lawyer has asked this question:
        
        QUESTION: {query}
        
        Here are relevant Ghana laws and legal principles:
        
        {context}
        
        {customary_section}
        
        Please provide:
        1. A clear, concise answer
        2. Citation to specific laws/principles
        3. Practical application for Ghana
        4. Any relevant customary law considerations
        5. Limitations or caveats
        
        Use professional legal language but explain clearly for practicing lawyers.
        """)
        
        customary_section = f"\n\nRELEVANT CUSTOMARY LAW:\n{customary_context}" if customary_context else ""
        
        chain = prompt | llm | StrOutputParser()
        
        answer = chain.invoke({
            "query": request.query,
            "context": context,
            "customary_section": customary_section
        })
        
        # 5. Extract sources
        sources = [
            {
                "title": r['metadata'].get('title'),
                "year": r['metadata'].get('year'),
                "type": r['metadata'].get('type'),
                "relevance": round(r['relevance_score'], 2)
            }
            for r in search_results
        ]
        
        # 6. Compile response
        return SemanticSearchResponse(
            answer=answer,
            sources=sources,
            relevant_statutes=[
                s['title'] for s in sources 
                if s['type'] == 'statute'
            ],
            customary_law_context=customary_context if customary_context else None,
            practical_advice=f"This analysis is based on {len(sources)} Ghana law sources and may require specific legal counsel for your situation.",
            confidence_score=sum(r['relevance_score'] for r in search_results) / len(search_results)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
