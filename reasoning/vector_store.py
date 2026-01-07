"""
Vector Store for Ghana Legal Knowledge
Ingests statutes, cases, and customary law principles
"""

import os
from typing import List, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma  # Free alternative to Pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pydantic import BaseModel
import json

class LegalDocument(BaseModel):
    """Ghana legal document structure"""
    title: str
    content: str
    document_type: str  # "statute", "case_law", "customary", "guide"
    jurisdiction: str
    year: int
    ethnic_group: Optional[str] = None  # For customary law
    sections: List[str] = []
    relevant_acts: List[str] = []

class GhanaLegalVectorStore:
    def __init__(self, persist_dir: str = "./chroma_db"):
        """Initialize Chroma vector store (free, local alternative to Pinecone)"""
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.vectorstore = Chroma(
            embedding_function=self.embeddings,
            persist_directory=persist_dir,
            collection_name="ghana-legal-knowledge"
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def ingest_ghana_statutes(self):
        """
        Ingest Ghana's key statutes
        CRITICAL: Start with these 20 core statutes
        """
        statutes = [
            # Constitutional Framework
            {
                "title": "The Constitution of the Republic of Ghana, 1992",
                "content": """
                Chapter 1-33: Fundamental rights and freedoms
                Chapter 5: Citizenship
                Chapter 6: State institutions and governance
                Chapter 7: Parliament
                Chapter 8: Executive
                Chapter 9: Judiciary
                Chapter 10: Local Government
                Article 27: Customary law recognition
                Article 265-295: Traditional rule and customary law
                """,
                "document_type": "statute",
                "year": 1992,
                "jurisdiction": "Ghana",
                "relevant_acts": ["All acts must comply with constitution"]
            },
            # Civil Law
            {
                "title": "Contracts Act, NRCD 25 (1960)",
                "content": """
                Governs formation, performance, and breach of contracts
                Key sections:
                - Offer and acceptance
                - Consideration
                - Privity of contract
                - Breach and remedies
                - Unconscionable terms
                Customary law consideration: Traditional contracts remain valid
                """,
                "document_type": "statute",
                "year": 1960,
                "jurisdiction": "Ghana",
                "sections": ["Formation", "Performance", "Breach", "Remedies"]
            },
            # Criminal Law
            {
                "title": "Criminal Procedure Code (NRCD 29)",
                "content": """
                Procedural framework for criminal trials in Ghana
                Key sections:
                - Arrest and bail
                - Indictment
                - Trial procedure
                - Evidence rules
                - Sentencing
                """,
                "document_type": "statute",
                "year": 1960,
                "jurisdiction": "Ghana"
            },
            # Evidence
            {
                "title": "Evidence Act (NRCD 26)",
                "content": """
                Governs admissibility of evidence in Ghana courts
                Key sections:
                - Relevant evidence
                - Hearsay rule exceptions
                - Expert evidence
                - Character evidence
                - Privilege
                Important: Customary law evidence may be admissible
                """,
                "document_type": "statute",
                "year": 1960,
                "jurisdiction": "Ghana"
            },
            # Property Law
            {
                "title": "Property Act (NRCD 28)",
                "content": """
                Governs property rights, transfers, and disputes
                Key sections:
                - Ownership and possession
                - Transfer of property
                - Mortgages
                - Easements
                - Adverse possession
                CRITICAL FOR GHANA: Customary land tenure is primary
                Allodial title (stool/skin) vs individual rights
                """,
                "document_type": "statute",
                "year": 1960,
                "jurisdiction": "Ghana"
            },
            # Succession
            {
                "title": "Intestate Succession Law (PNDCL 111)",
                "content": """
                Governs inheritance when no will exists
                Key sections:
                - Classes of heirs
                - Distribution of estate
                - Administration of estate
                NOTE: Customary law succession still applies in many regions
                """,
                "document_type": "statute",
                "year": 1985,
                "jurisdiction": "Ghana"
            },
            # Family Law
            {
                "title": "Matrimonial Causes Act (NRCD 23)",
                "content": """
                Governs marriage, divorce, and family matters
                Key sections:
                - Grounds for divorce
                - Matrimonial property
                - Custody of children
                - Maintenance
                - Customary marriage recognition
                """,
                "document_type": "statute",
                "year": 1960,
                "jurisdiction": "Ghana"
            },
            # Labor Law
            {
                "title": "Labour Act (Act 651)",
                "content": """
                Governs employment relationships
                Key sections:
                - Contracts of employment
                - Conditions of work
                - Termination
                - Dispute resolution
                - Rights of workers
                """,
                "document_type": "statute",
                "year": 2003,
                "jurisdiction": "Ghana"
            },
        ]
        
        documents = []
        for statute in statutes:
            doc = Document(
                page_content=statute["content"],
                metadata={
                    "title": statute["title"],
                    "type": statute["document_type"],
                    "year": statute["year"],
                    "jurisdiction": statute["jurisdiction"],
                }
            )
            documents.append(doc)
        
        # Split into chunks
        split_docs = self.text_splitter.split_documents(documents)
        
        # Add to vector store
        self.vectorstore.add_documents(split_docs)
        print(f"Ingested {len(split_docs)} statute chunks into vector store")
    
    def ingest_customary_law(self):
        """Ingest Ghana's Customary Law Principles"""
        customary_principles = [
            # Akan/Ashanti Customary Law
            {
                "title": "Akan Customary Law: Land Tenure",
                "content": """
                AKAN (Ashanti/Fante) LAND LAW:
                
                Key Principles:
                1. Stool Land (Public Land)
                   - Owned by stool/skin/clan
                   - Managed by chief/elders
                   - Cannot be individually owned
                   
                2. Family Land
                   - Owned by extended family
                   - Inherited matrilineally (Ashanti) or patrilineally (Fante)
                   - Individual members have usufruct
                   
                3. Individual Land
                   - Created through clearing/farming
                   - Inherits according to family law
                   - Can be pledged/mortgaged
                   
                Land Disputes Resolution:
                - Family head mediation first
                - Chief's court
                - Formal legal system (last resort)
                
                Modern Application:
                - Must be considered alongside Property Act
                - Many land disputes unresolved (dual ownership)
                - Courts recognize stool land primacy
                """,
                "document_type": "customary",
                "year": None,
                "ethnic_group": "Akan",
                "jurisdiction": "Ghana"
            },
            # Ewe Customary Law
            {
                "title": "Ewe Customary Law: Family and Succession",
                "content": """
                EWE CUSTOMARY LAW:
                
                Family Structure:
                1. Patrilineal (father's line) inheritance
                2. Inheritance follows father's family
                3. Widow entitled to support from family
                
                Succession Principles:
                - Youngest son inherits paternal property
                - Eldest son inherits chieftaincy
                - Daughters may inherit mobile property
                - Widow has rights but not ownership
                
                Marriage Customs:
                - Bride price (akpeteshi) essential
                - Family consent required
                - Customary marriage recognized in law
                
                Dispute Resolution:
                - Family elders
                - Clan head
                - Traditional chief court
                
                Legal Status in Ghana:
                - Recognized under Constitution Article 27
                - Applied by regular courts in relevant cases
                - Takes precedence in family matters
                """,
                "document_type": "customary",
                "year": None,
                "ethnic_group": "Ewe",
                "jurisdiction": "Ghana"
            },
            # Ga Customary Law
            {
                "title": "Ga Customary Law: Land and Chieftaincy",
                "content": """
                GA CUSTOMARY LAW (Accra Region):
                
                Land Tenure:
                1. Weku (Family Land)
                   - Collective family ownership
                   - Individual members get parcels
                   - Inherited through father's line
                   
                2. Private Land
                   - Created through personal labor
                   - Fully owned individually
                   - Can be sold or pledged
                   
                Chieftaincy:
                - Lateral succession (brother to brother)
                - Then to deceased brother's son
                - Customary selection process
                
                Special Issues:
                - Dual ownership in Accra (stool + individual)
                - Mixed marriages (customary + statutory)
                - Multiple claims to same land (common)
                
                Practical Application:
                - Many Accra land disputes based on conflicting claims
                - Government land also claims same areas
                - Courts developing standards for recognition
                """,
                "document_type": "customary",
                "year": None,
                "ethnic_group": "Ga",
                "jurisdiction": "Ghana"
            },
        ]
        
        documents = []
        for principle in customary_principles:
            doc = Document(
                page_content=principle["content"],
                metadata={
                    "title": principle["title"],
                    "type": principle["document_type"],
                    "ethnic_group": principle.get("ethnic_group"),
                    "jurisdiction": principle["jurisdiction"],
                }
            )
            documents.append(doc)
        
        split_docs = self.text_splitter.split_documents(documents)
        self.vectorstore.add_documents(split_docs)
        print(f"Ingested {len(split_docs)} customary law chunks into vector store")
    
    def semantic_search(self, query: str, k: int = 5):
        """Search vector store semantically"""
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        
        return [
            {
                "content": doc.page_content,
                "relevance_score": score,
                "metadata": doc.metadata,
            }
            for doc, score in results
        ]
    
    def persist(self):
        """Save vector store to disk"""
        self.vectorstore.persist()


# Initialize on startup
vector_store = None

def initialize_vector_store():
    """Initialize and populate vector store"""
    global vector_store
    vector_store = GhanaLegalVectorStore()
    
    # Ingest statutes
    vector_store.ingest_ghana_statutes()
    
    # Ingest customary law
    vector_store.ingest_customary_law()
    
    # Persist to disk
    vector_store.persist()
    
    print("✅ Vector store initialized with Ghana law knowledge")
