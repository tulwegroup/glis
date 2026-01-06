"""
Statute Database - Layer 3

Comprehensive database of Ghana statutes and legislation.
Indexed for fast search and retrieval with section-level granularity.

Features:
- Ghana Constitution and major Acts
- Section-level indexing
- Cross-references and related statutes
- Amendment tracking
- Full-text search
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import json
import os

try:
    from whoosh.fields import Schema, TEXT, ID, KEYWORD, STORED
    from whoosh.index import create_in
    from whoosh.qparser import QueryParser
    HAS_WHOOSH = True
except ImportError:
    HAS_WHOOSH = False


class StatuteType(Enum):
    """Types of legislation"""
    CONSTITUTION = "constitution"
    ACT = "act"
    REGULATION = "regulation"
    INSTRUMENT = "instrument"
    LEGISLATIVE_INSTRUMENT = "legislative_instrument"
    COMMON_LAW = "common_law"


class AmendmentType(Enum):
    """Types of amendments"""
    AMENDMENT = "amendment"
    REPEAL = "repeal"
    SUBSTITUTION = "substitution"
    INSERTION = "insertion"


@dataclass
class Statute:
    """Individual statute or legislation"""
    statute_id: str  # e.g., "CONSTITUTION_1992", "ACT_29_1960"
    title: str
    statute_type: StatuteType
    year_enacted: int
    year_amended: Optional[int] = None
    full_title: str = ""
    short_title: str = ""
    description: str = ""
    sections: Dict[str, str] = field(default_factory=dict)  # section_number -> text
    related_statutes: List[str] = field(default_factory=list)
    amendments: List[Dict[str, Any]] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    is_current: bool = True
    repealed_by: Optional[str] = None
    repealed_date: Optional[str] = None

    @property
    def full_citation(self) -> str:
        """Generate full citation format"""
        if self.statute_type == StatuteType.CONSTITUTION:
            return f"Constitution of the Republic of Ghana, 1992"
        elif self.statute_type == StatuteType.ACT:
            return f"Act {self.statute_id.split('_')[-1]} of {self.year_enacted}"
        else:
            return f"{self.statute_type.value.upper()} {self.year_enacted}"

    def get_section(self, section_number: str) -> Optional[str]:
        """Retrieve specific section"""
        return self.sections.get(section_number)

    def search_sections(self, query: str) -> List[Tuple[str, str]]:
        """Search sections by keyword"""
        results = []
        query_lower = query.lower()
        
        for section_num, section_text in self.sections.items():
            if query_lower in section_text.lower():
                results.append((section_num, section_text))
        
        return results


@dataclass
class StatuteSection:
    """Individual section of a statute"""
    statute_id: str
    section_number: str
    heading: str
    text: str
    subsections: Dict[str, str] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    related_sections: List[str] = field(default_factory=list)
    case_citations: List[str] = field(default_factory=list)  # Cases interpreting this


@dataclass
class Amendment:
    """Amendment to statute"""
    amendment_id: str
    statute_id: str
    amending_statute: str  # Act number that amended
    amendment_type: AmendmentType
    effective_date: str
    description: str
    affected_sections: List[str] = field(default_factory=list)
    original_text: Optional[str] = None
    amended_text: Optional[str] = None


class GhanaStatuteDatabase:
    """Database of Ghana legislation"""

    def __init__(self, data_dir: str = "data/statutes"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.statutes: Dict[str, Statute] = {}
        self.index_by_statute_type: Dict[StatuteType, List[str]] = {}
        self.index_by_keyword: Dict[str, Set[str]] = {}
        self.amendments: List[Amendment] = []
        
        # Initialize full-text search if available
        self.search_index = None
        if HAS_WHOOSH:
            self._initialize_search_index()
        
        # Load Ghana statutes
        self._load_ghana_statutes()

    def _initialize_search_index(self):
        """Initialize Whoosh full-text search index"""
        try:
            schema = Schema(
                statute_id=ID(stored=True),
                title=TEXT(stored=True),
                content=TEXT(stored=True),
                statute_type=KEYWORD(stored=True),
                year=STORED()
            )
            
            index_path = os.path.join(self.data_dir, "whoosh_index")
            os.makedirs(index_path, exist_ok=True)
            self.search_index = create_in(index_path, schema)
        except:
            self.search_index = None

    def _load_ghana_statutes(self) -> None:
        """Load Ghana statute database"""
        
        # Constitution of Ghana 1992
        self._add_statute(Statute(
            statute_id="CONSTITUTION_1992",
            title="Constitution of the Republic of Ghana, 1992",
            statute_type=StatuteType.CONSTITUTION,
            year_enacted=1992,
            short_title="Constitution",
            description="The supreme law of Ghana establishing government structure, fundamental rights, and legal framework",
            keywords=["constitution", "fundamental rights", "government", "presidency", "parliament", "judiciary"],
            sections={
                "CHAPTER 1": "Sovereignty of the people",
                "CHAPTER 2": "Citizenship",
                "CHAPTER 3": "Fundamental rights and freedoms",
                "ARTICLE 12": "Protection of fundamental rights",
                "ARTICLE 13": "Application for enforcement of fundamental rights",
                "ARTICLE 19": "Right to life",
                "ARTICLE 21": "Equality and freedom from discrimination",
                "ARTICLE 33": "Access to information",
            }
        ))
        
        # Ghana Evidence Act
        self._add_statute(Statute(
            statute_id="ACT_29_1960",
            title="Evidence Act",
            statute_type=StatuteType.ACT,
            year_enacted=1960,
            short_title="Evidence Act, 1960",
            description="Governs rules of evidence in civil and criminal proceedings in Ghana",
            keywords=["evidence", "admissibility", "witness", "documents", "proof"],
            sections={
                "1": "Rules of evidence",
                "2": "Oral and documentary evidence",
                "3": "Examination of witnesses",
                "PART I": "Relevant facts",
                "PART II": "On whom the burden of proof lies",
                "PART III": "On the standard of proof",
            }
        ))
        
        # High Court (Civil Procedure) Rules
        self._add_statute(Statute(
            statute_id="HIGH_COURT_RULES",
            title="High Court (Civil Procedure) Rules",
            statute_type=StatuteType.INSTRUMENT,
            year_enacted=2004,
            short_title="C.I. 47",
            description="Procedural rules for civil cases in Ghana High Court",
            keywords=["civil procedure", "pleadings", "discovery", "trial"],
            sections={
                "ORDER 1": "General principles",
                "ORDER 3": "Parties",
                "ORDER 4": "Pleadings",
                "ORDER 5": "Discovery",
                "ORDER 10": "Interlocutory applications",
                "ORDER 13": "Judgment and orders",
            }
        ))
        
        # Matrimonial Causes Act
        self._add_statute(Statute(
            statute_id="MATRIMONIAL_CAUSES_ACT_1971",
            title="Matrimonial Causes Act",
            statute_type=StatuteType.ACT,
            year_enacted=1971,
            short_title="Matrimonial Causes Act, 1971",
            description="Governs marriage, divorce, and family property in Ghana",
            keywords=["marriage", "divorce", "family property", "custody", "maintenance"],
            sections={
                "1": "Jurisdiction",
                "2": "Grounds for divorce",
                "3": "Separation",
                "10": "Matrimonial property",
                "15": "Custody of children",
                "20": "Maintenance",
            }
        ))
        
        # Sales of Goods Act
        self._add_statute(Statute(
            statute_id="SALES_OF_GOODS_ACT_1962",
            title="Sales of Goods Act",
            statute_type=StatuteType.ACT,
            year_enacted=1962,
            short_title="Sales of Goods Act, 1962",
            description="Governs sale of goods transactions in Ghana",
            keywords=["sale of goods", "contract", "title", "condition", "warranty"],
            sections={
                "1": "Sale of goods",
                "12": "Implied terms",
                "13": "Sale by description",
                "14": "Satisfactory quality",
                "15": "Fitness for purpose",
                "20": "Transfer of property",
            }
        ))
        
        # Labour Act
        self._add_statute(Statute(
            statute_id="LABOUR_ACT_2003",
            title="Labour Act",
            statute_type=StatuteType.ACT,
            year_enacted=2003,
            short_title="Labour Act, 2003",
            description="Governs employment relationships, conditions of service, and worker protection in Ghana",
            keywords=["employment", "termination", "wages", "leave", "safety"],
            sections={
                "1": "Definitions",
                "3": "Conditions of service",
                "15": "Termination of employment",
                "20": "Wages",
                "25": "Annual leave",
                "32": "Safety and health",
            }
        ))
        
        # Criminal Code
        self._add_statute(Statute(
            statute_id="CRIMINAL_CODE_1960",
            title="Criminal Code",
            statute_type=StatuteType.ACT,
            year_enacted=1960,
            short_title="Criminal Code, 1960 (NRCD 16)",
            description="Defines criminal offences and penalties in Ghana",
            keywords=["criminal", "offence", "punishment", "theft", "fraud", "assault"],
            sections={
                "1": "Preliminary",
                "2": "General principles of criminal responsibility",
                "50": "Attempt",
                "100": "Theft",
                "120": "Fraud",
                "133": "Assault",
            }
        ))
        
        # Companies Act
        self._add_statute(Statute(
            statute_id="COMPANIES_ACT_2019",
            title="Companies Act",
            statute_type=StatuteType.ACT,
            year_enacted=2019,
            short_title="Companies Act, 2019",
            description="Governs incorporation, management, and winding up of companies in Ghana",
            keywords=["company", "incorporation", "directors", "shareholders", "winding up"],
            sections={
                "1": "Preliminary",
                "10": "Incorporation of companies",
                "150": "Directors' duties",
                "200": "Shareholders' rights",
                "300": "Winding up",
            }
        ))
        
        # Property Law - Land Title Registration Law
        self._add_statute(Statute(
            statute_id="LAND_TITLE_REGISTRATION_LAW",
            title="Land Title Registration Law",
            statute_type=StatuteType.INSTRUMENT,
            year_enacted=2000,
            short_title="C.I. 1963",
            description="Governs registration and transfer of title to land in Ghana",
            keywords=["property", "land", "title", "registration", "transfer"],
            sections={
                "1": "Preliminary",
                "10": "Title to land",
                "20": "Registration of title",
                "30": "Transfer of land",
            }
        ))
        
        # Add family law - Customary Law elements
        self._add_statute(Statute(
            statute_id="INTESTATE_SUCCESSION_LAW",
            title="Intestate Succession Law",
            statute_type=StatuteType.INSTRUMENT,
            year_enacted=1985,
            short_title="P.N.D.C.L. 111",
            description="Governs succession to property on death without a will in Ghana",
            keywords=["succession", "intestate", "inheritance", "customary law"],
            sections={
                "1": "Application",
                "2": "Succession rights",
                "3": "Spouse rights",
                "4": "Children rights",
            }
        ))

    def _add_statute(self, statute: Statute) -> None:
        """Add statute to database"""
        self.statutes[statute.statute_id] = statute
        
        # Index by type
        if statute.statute_type not in self.index_by_statute_type:
            self.index_by_statute_type[statute.statute_type] = []
        self.index_by_statute_type[statute.statute_type].append(statute.statute_id)
        
        # Index by keywords
        for keyword in statute.keywords:
            if keyword not in self.index_by_keyword:
                self.index_by_keyword[keyword] = set()
            self.index_by_keyword[keyword].add(statute.statute_id)

    def search_by_title(self, query: str) -> List[Statute]:
        """Search statutes by title"""
        results = []
        query_lower = query.lower()
        
        for statute in self.statutes.values():
            if query_lower in statute.title.lower() or query_lower in statute.short_title.lower():
                results.append(statute)
        
        return results

    def search_by_keyword(self, keyword: str) -> List[Statute]:
        """Search statutes by keyword"""
        keyword_lower = keyword.lower()
        statute_ids = self.index_by_keyword.get(keyword_lower, set())
        
        return [self.statutes[sid] for sid in statute_ids if sid in self.statutes]

    def search_sections(self, query: str) -> List[Tuple[str, str, str]]:
        """Search statute sections across all statutes
        Returns: list of (statute_id, section_number, section_text)
        """
        results = []
        query_lower = query.lower()
        
        for statute_id, statute in self.statutes.items():
            matches = statute.search_sections(query)
            for section_num, section_text in matches:
                results.append((statute_id, section_num, section_text))
        
        return results

    def get_statute(self, statute_id: str) -> Optional[Statute]:
        """Retrieve statute by ID"""
        return self.statutes.get(statute_id)

    def get_statute_by_title(self, title: str) -> Optional[Statute]:
        """Get statute by exact title"""
        for statute in self.statutes.values():
            if statute.title.lower() == title.lower() or statute.short_title.lower() == title.lower():
                return statute
        return None

    def get_related_statutes(self, statute_id: str) -> List[Statute]:
        """Get statutes related to given statute"""
        statute = self.get_statute(statute_id)
        if not statute:
            return []
        
        related = []
        for related_id in statute.related_statutes:
            if related_id in self.statutes:
                related.append(self.statutes[related_id])
        
        return related

    def get_section(self, statute_id: str, section_number: str) -> Optional[Tuple[str, str]]:
        """Get specific section from statute
        Returns: (statute_title, section_text)
        """
        statute = self.get_statute(statute_id)
        if not statute:
            return None
        
        section_text = statute.get_section(section_number)
        if section_text:
            return (statute.title, section_text)
        
        return None

    def get_statutes_by_type(self, statute_type: StatuteType) -> List[Statute]:
        """Get all statutes of given type"""
        statute_ids = self.index_by_statute_type.get(statute_type, [])
        return [self.statutes[sid] for sid in statute_ids if sid in self.statutes]

    def interpret_statute(self, statute_id: str, section_number: str) -> Optional[Dict[str, Any]]:
        """Get statute section with interpretation guide"""
        statute = self.get_statute(statute_id)
        if not statute:
            return None
        
        section_text = statute.get_section(section_number)
        if not section_text:
            return None
        
        return {
            'statute_id': statute_id,
            'statute_title': statute.title,
            'section_number': section_number,
            'section_text': section_text,
            'statute_type': statute.statute_type.value,
            'year_enacted': statute.year_enacted,
            'related_sections': [],  # Would be populated from references
            'case_interpretations': [],  # Would link to case law
        }

    def list_all_statutes(self) -> List[Dict[str, Any]]:
        """Get summary of all statutes"""
        return [
            {
                'statute_id': s.statute_id,
                'title': s.title,
                'short_title': s.short_title,
                'type': s.statute_type.value,
                'year_enacted': s.year_enacted,
                'is_current': s.is_current,
            }
            for s in self.statutes.values()
        ]

    def export_statute(self, statute_id: str, format: str = "json") -> Optional[str]:
        """Export statute in various formats"""
        statute = self.get_statute(statute_id)
        if not statute:
            return None
        
        if format == "json":
            return json.dumps(asdict(statute), indent=2, default=str)
        elif format == "text":
            text = f"{statute.title}\n"
            text += f"Year Enacted: {statute.year_enacted}\n\n"
            for section_num, section_text in statute.sections.items():
                text += f"{section_num}: {section_text}\n\n"
            return text
        
        return None

    def add_statute(
        self,
        statute_id: str,
        title: str,
        statute_type: StatuteType,
        year_enacted: int,
        sections: Dict[str, str],
        keywords: List[str]
    ) -> Statute:
        """Add new statute to database"""
        statute = Statute(
            statute_id=statute_id,
            title=title,
            statute_type=statute_type,
            year_enacted=year_enacted,
            sections=sections,
            keywords=keywords
        )
        
        self._add_statute(statute)
        return statute


# Global instance
_database: Optional[GhanaStatuteDatabase] = None


def get_statute_database() -> GhanaStatuteDatabase:
    """Get or create statute database singleton"""
    global _database
    if _database is None:
        _database = GhanaStatuteDatabase()
    return _database


if __name__ == "__main__":
    # Test statute database
    db = get_statute_database()
    
    print("Ghana Statute Database Test")
    print("=" * 50)
    
    # List all statutes
    print("\nAll Statutes:")
    for statute in db.list_all_statutes():
        print(f"- {statute['title']} ({statute['year_enacted']})")
    
    # Search by title
    print("\nSearch for 'Labour':")
    results = db.search_by_title("Labour")
    for statute in results:
        print(f"  - {statute.title}")
    
    # Search by keyword
    print("\nSearch for 'employment':")
    results = db.search_by_keyword("employment")
    for statute in results:
        print(f"  - {statute.title}")
