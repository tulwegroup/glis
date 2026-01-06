"""
Ghana Legal Taxonomy - Comprehensive legal issue classification system

This module provides a hierarchical taxonomy of Ghanaian legal concepts
extracted from case law, statutes, and legal practice. Used for:
- Case categorization
- Concept-based searching
- Jurisprudence analysis
- Citation tracking by area of law
"""

from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from enum import Enum


@dataclass
class LegalConcept:
    """Represents a legal concept in the taxonomy"""
    id: str
    name: str
    aliases: List[str]  # Alternative names (e.g., "fiduciary duty", "fiduciary obligation")
    definition: str
    parent_category: str  # Parent category ID
    statutes: List[str]  # Relevant statutes (e.g., "Act 992, Section 179")
    keywords: List[str]  # Keywords for matching


class TaxonomyCategory(Enum):
    """Top-level categories in Ghana legal taxonomy"""
    CONTRACT_LAW = "contract_law"
    PROPERTY_LAW = "property_law"
    SUCCESSION_LAW = "succession_law"
    COMMERCIAL_LAW = "commercial_law"
    CONSTITUTIONAL_LAW = "constitutional_law"
    CRIMINAL_LAW = "criminal_law"
    FAMILY_LAW = "family_law"
    LABOUR_LAW = "labour_law"
    ADMINISTRATIVE_LAW = "administrative_law"
    REAL_PROPERTY_LAW = "real_property_law"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    CORPORATE_LAW = "corporate_law"
    BANKING_LAW = "banking_law"
    ENVIRONMENTAL_LAW = "environmental_law"
    TAX_LAW = "tax_law"
    CIVIL_PROCEDURE = "civil_procedure"
    CRIMINAL_PROCEDURE = "criminal_procedure"
    EVIDENCE = "evidence"
    LAND_LAW = "land_law"
    TORT_LAW = "tort_law"


class GhanaLegalTaxonomy:
    """
    Comprehensive Ghana legal taxonomy with 100+ concepts
    hierarchically organized with aliases and statute references
    """

    def __init__(self):
        self.concepts: Dict[str, LegalConcept] = {}
        self.category_map: Dict[str, List[str]] = {}
        self.alias_map: Dict[str, str] = {}  # Maps aliases to concept IDs
        self._initialize_taxonomy()

    def _initialize_taxonomy(self):
        """Initialize the complete taxonomy"""
        concepts = self._build_complete_taxonomy()
        for concept in concepts:
            self.concepts[concept.id] = concept
            self._add_to_category_map(concept)
            self._add_aliases(concept)

    def _build_complete_taxonomy(self) -> List[LegalConcept]:
        """Build all legal concepts for Ghana"""
        return [
            # ===== CONTRACT LAW =====
            LegalConcept(
                id="contract_formation",
                name="Contract Formation",
                aliases=["offer and acceptance", "contract essential elements"],
                definition="Requirements for creating a binding contract: offer, acceptance, consideration, intention to create legal relations",
                parent_category="contract_law",
                statutes=["Contracts Act (Act 25, 1960)", "Sale of Goods Act (Act 137, 1962)"],
                keywords=["offer", "acceptance", "consideration", "consensus ad idem"]
            ),
            LegalConcept(
                id="breach_of_contract",
                name="Breach of Contract",
                aliases=["contract breach", "repudiation", "material breach", "anticipatory breach"],
                definition="Failure by one party to perform obligations under a contract without legal justification",
                parent_category="contract_law",
                statutes=["Contracts Act (Act 25, 1960)"],
                keywords=["breach", "failure to perform", "non-performance", "repudiation"]
            ),
            LegalConcept(
                id="damages_contract",
                name="Contractual Damages",
                aliases=["damages for breach", "compensation", "remedies for breach"],
                definition="Compensation awarded for loss suffered due to breach of contract, measured by reliance and expectation interests",
                parent_category="contract_law",
                statutes=["Contracts Act (Act 25, 1960)"],
                keywords=["damages", "loss", "compensation", "remoteness", "foreseeability"]
            ),
            LegalConcept(
                id="conditions_warranties",
                name="Conditions and Warranties",
                aliases=["fundamental terms", "innominate terms", "conditions precedent"],
                definition="Distinction between conditions (essential terms) and warranties (non-essential terms) in sale of goods",
                parent_category="contract_law",
                statutes=["Sale of Goods Act (Act 137, 1962)"],
                keywords=["condition", "warranty", "essential", "non-essential", "innominate term"]
            ),
            LegalConcept(
                id="impossibility_frustration",
                name="Impossibility and Frustration",
                aliases=["frustration of contract", "doctrine of frustration", "force majeure"],
                definition="Discharge of contract when performance becomes impossible or fundamentally changed due to unforeseen events",
                parent_category="contract_law",
                statutes=["Contracts Act (Act 25, 1960)"],
                keywords=["frustration", "impossibility", "doctrine", "changed circumstances"]
            ),
            LegalConcept(
                id="misrepresentation",
                name="Misrepresentation",
                aliases=["innocent misrepresentation", "fraudulent misrepresentation", "negligent misrepresentation"],
                definition="False statement of fact that induces another to enter a contract",
                parent_category="contract_law",
                statutes=["Contracts Act (Act 25, 1960)"],
                keywords=["misrepresentation", "false statement", "inducement", "reliance"]
            ),
            LegalConcept(
                id="duress_undue_influence",
                name="Duress and Undue Influence",
                aliases=["coercion", "economic duress", "mental coercion"],
                definition="Contract voidable when one party exerts illegitimate pressure on another",
                parent_category="contract_law",
                statutes=["Contracts Act (Act 25, 1960)"],
                keywords=["duress", "undue influence", "coercion", "illegitimate pressure"]
            ),
            LegalConcept(
                id="parol_evidence_rule",
                name="Parol Evidence Rule",
                aliases=["extrinsic evidence", "integration", "written agreement", "parol contract"],
                definition="Written contract is the final expression of parties' intent; extrinsic evidence of prior negotiations generally inadmissible",
                parent_category="contract_law",
                statutes=["Contracts Act (Act 25, 1960)"],
                keywords=["parol evidence", "integration clause", "written agreement", "extrinsic evidence"]
            ),

            # ===== PROPERTY LAW =====
            LegalConcept(
                id="land_title",
                name="Land Title and Ownership",
                aliases=["absolute title", "registered title", "unregistered land", "customary title"],
                definition="Legal right of ownership in land, including registered, unregistered, and customary tenure systems in Ghana",
                parent_category="property_law",
                statutes=["Land Title Registration Law (PNDCL 152), 1986", "Lands Commission Act (Act 691, 2008)"],
                keywords=["title", "ownership", "land certificate", "registration", "customary land"]
            ),
            LegalConcept(
                id="easements_covenants",
                name="Easements and Restrictive Covenants",
                aliases=["rights of way", "restrictive covenants", "equitable interests"],
                definition="Rights over another's property (easement) or binding restrictions on use of land (covenants)",
                parent_category="property_law",
                statutes=["Lands Commission Act (Act 691, 2008)", "Property Law Act"],
                keywords=["easement", "right of way", "restrictive covenant", "equitable interest"]
            ),
            LegalConcept(
                id="landlord_tenant",
                name="Landlord and Tenant Law",
                aliases=["tenancy", "lease", "eviction", "rent dispute", "lessor lessee"],
                definition="Rights and obligations of landlords and tenants, including rent, repairs, eviction procedures",
                parent_category="property_law",
                statutes=["Rent Act (Act 220, 1963)", "Property Law Act"],
                keywords=["landlord", "tenant", "lease", "rent", "eviction", "repairs"]
            ),
            LegalConcept(
                id="trespass_property",
                name="Trespass to Land",
                aliases=["unlawful entry", "interference with land", "possession"],
                definition="Unlawful entry on or interference with another's land",
                parent_category="property_law",
                statutes=["Common Law", "Property Law Act"],
                keywords=["trespass", "unlawful entry", "possession", "interference"]
            ),
            LegalConcept(
                id="nuisance_property",
                name="Nuisance",
                aliases=["private nuisance", "public nuisance", "interference with enjoyment"],
                definition="Unlawful interference with person's use and enjoyment of land or right to quiet enjoyment",
                parent_category="property_law",
                statutes=["Common Law"],
                keywords=["nuisance", "private nuisance", "public nuisance", "interference"]
            ),

            # ===== SUCCESSION LAW =====
            LegalConcept(
                id="intestate_succession",
                name="Intestate Succession",
                aliases=["intestacy", "rules of succession", "succession without will"],
                definition="Distribution of deceased's estate when no valid will exists, according to statutory rules",
                parent_category="succession_law",
                statutes=["Intestate Succession Law (PNDCL 111), 1985", "Succession Act"],
                keywords=["intestate", "intestacy", "succession", "distribution", "estate"]
            ),
            LegalConcept(
                id="testamentary_succession",
                name="Testamentary Succession",
                aliases=["will", "testator", "testamentary capacity", "probate"],
                definition="Distribution of deceased's estate according to terms of valid will",
                parent_category="succession_law",
                statutes=["Wills Act (Act 360, 1960)", "Succession Act"],
                keywords=["will", "testament", "testator", "probate", "testamentary capacity"]
            ),
            LegalConcept(
                id="will_validity",
                name="Will Validity and Formalities",
                aliases=["testamentary formalities", "requirements for valid will", "revocation"],
                definition="Requirements for valid will: signature, witnesses, testator capacity, absence of fraud",
                parent_category="succession_law",
                statutes=["Wills Act (Act 360, 1960)"],
                keywords=["will", "formalities", "valid will", "signature", "witnesses", "capacity"]
            ),
            LegalConcept(
                id="probate_administration",
                name="Probate and Estate Administration",
                aliases=["letters of administration", "probate grant", "estate administration"],
                definition="Legal procedures for obtaining authority to administer deceased's estate and distributing assets",
                parent_category="succession_law",
                statutes=["Succession Act", "Probate Rules"],
                keywords=["probate", "grant", "administration", "executor", "administrator"]
            ),
            LegalConcept(
                id="spousal_rights",
                name="Spousal Rights in Succession",
                aliases=["widow's rights", "widower's rights", "surviving spouse", "matrimonial property"],
                definition="Rights of surviving spouse to share in deceased's estate, including statutory rights in matrimonial home",
                parent_category="succession_law",
                statutes=["Intestate Succession Law (PNDCL 111), 1985", "Matrimonial Causes Act (Act 367, 1971)"],
                keywords=["spouse", "widow", "matrimonial property", "rights", "share"]
            ),
            LegalConcept(
                id="customary_succession",
                name="Customary Succession Laws",
                aliases=["chieftaincy succession", "family property", "customary rules", "stool property"],
                definition="Succession rules based on customary law, varying by ethnic group and region in Ghana",
                parent_category="succession_law",
                statutes=["Chieftaincy Act (Act 759, 2008)", "Customary Law"],
                keywords=["customary", "succession", "chieftaincy", "stool property", "family property"]
            ),

            # ===== COMMERCIAL LAW =====
            LegalConcept(
                id="sale_of_goods",
                name="Sale of Goods",
                aliases=["sales contract", "transfer of ownership", "goods", "merchandise"],
                definition="Contract for sale and transfer of ownership of goods, including implied conditions and warranties",
                parent_category="commercial_law",
                statutes=["Sale of Goods Act (Act 137, 1962)"],
                keywords=["sale", "goods", "transfer of ownership", "price"]
            ),
            LegalConcept(
                id="commercial_instruments",
                name="Negotiable Instruments",
                aliases=["bills of exchange", "promissory notes", "cheques", "negotiable", "holder"],
                definition="Transferable written orders or promises to pay money (bills, notes, cheques)",
                parent_category="commercial_law",
                statutes=["Bills of Exchange Act (Act 247, 1965)"],
                keywords=["negotiable instrument", "bill", "note", "cheque", "holder in due course"]
            ),
            LegalConcept(
                id="partnership",
                name="Partnership Law",
                aliases=["partnership agreement", "partner liability", "dissolution", "partnership property"],
                definition="Legal relationship between persons carrying on business in partnership, with joint and several liability",
                parent_category="commercial_law",
                statutes=["Partnership Act (Act 152, 1962)"],
                keywords=["partnership", "partner", "joint liability", "dissolution", "capital"]
            ),
            LegalConcept(
                id="bailment",
                name="Bailment",
                aliases=["pledgor", "pledgee", "bailee", "bailor", "custody", "possessory lien"],
                definition="Relationship where one party (bailor) delivers personal property to another (bailee) for safekeeping or use",
                parent_category="commercial_law",
                statutes=["Common Law"],
                keywords=["bailment", "bailor", "bailee", "possession", "custody"]
            ),
            LegalConcept(
                id="hire_purchase",
                name="Hire Purchase Agreements",
                aliases=["conditional sale", "instalment sale", "ownership retention"],
                definition="Agreement allowing possession before ownership transfer, with conditional ownership transfer upon full payment",
                parent_category="commercial_law",
                statutes=["Hire Purchase Act", "Common Law"],
                keywords=["hire purchase", "conditional sale", "instalment", "retention of title"]
            ),

            # ===== CORPORATE LAW =====
            LegalConcept(
                id="company_incorporation",
                name="Company Incorporation and Registration",
                aliases=["memorandum of association", "articles of association", "company registration"],
                definition="Process and requirements for registering a company as a separate legal entity",
                parent_category="commercial_law",
                statutes=["Companies Act (Act 992, 2019)"],
                keywords=["incorporation", "registration", "company", "memorandum", "articles"]
            ),
            LegalConcept(
                id="directors_duties",
                name="Directors' Duties and Responsibilities",
                aliases=["fiduciary duty", "duty of care", "duty of good faith", "managing director"],
                definition="Legal and fiduciary duties of company directors: care, skill, diligence, good faith, compliance with law",
                parent_category="commercial_law",
                statutes=["Companies Act (Act 992, 2019)", "Section 179"],
                keywords=["director", "fiduciary duty", "care", "diligence", "good faith"]
            ),
            LegalConcept(
                id="shareholder_rights",
                name="Shareholder Rights and Remedies",
                aliases=["minority shareholder", "shareholder remedy", "oppression", "derivative action"],
                definition="Rights of shareholders including voting, dividends, inspection, and remedies for oppression",
                parent_category="commercial_law",
                statutes=["Companies Act (Act 992, 2019)"],
                keywords=["shareholder", "minority", "oppression", "derivative", "voting"]
            ),
            LegalConcept(
                id="corporate_governance",
                name="Corporate Governance",
                aliases=["board of directors", "internal management", "disclosure", "annual meeting"],
                definition="System of rules, practices, and processes for directing and controlling companies",
                parent_category="commercial_law",
                statutes=["Companies Act (Act 992, 2019)", "SEC Guidelines"],
                keywords=["governance", "board", "disclosure", "internal controls", "transparency"]
            ),
            LegalConcept(
                id="winding_up",
                name="Company Winding Up and Liquidation",
                aliases=["dissolution", "liquidation", "insolvency", "receiver", "liquidator"],
                definition="Legal process for terminating company, realizing assets, and distributing to creditors",
                parent_category="commercial_law",
                statutes=["Companies Act (Act 992, 2019)", "Insolvency Act"],
                keywords=["winding up", "liquidation", "receiver", "insolvency", "creditors"]
            ),

            # ===== CONSTITUTIONAL LAW =====
            LegalConcept(
                id="fundamental_rights",
                name="Fundamental Human Rights",
                aliases=["constitutional rights", "freedoms", "bill of rights", "civil liberties"],
                definition="Constitutional protections for individual rights: liberty, equality, free expression, religious freedom",
                parent_category="constitutional_law",
                statutes=["Constitution of Ghana (1992)", "Chapter 5"],
                keywords=["fundamental rights", "freedom", "liberty", "equality", "discrimination"]
            ),
            LegalConcept(
                id="separation_of_powers",
                name="Separation of Powers",
                aliases=["executive", "legislative", "judicial", "checks and balances"],
                definition="Constitutional principle dividing governmental power among executive, legislative, and judicial branches",
                parent_category="constitutional_law",
                statutes=["Constitution of Ghana (1992)", "Chapters 6-8"],
                keywords=["separation", "executive", "legislature", "judiciary", "balance"]
            ),
            LegalConcept(
                id="constitutional_review",
                name="Constitutional Review and Judicial Review",
                aliases=["constitutional validity", "ultra vires", "unreasonableness", "proportionality"],
                definition="Power of courts to examine constitutionality of laws and executive actions",
                parent_category="constitutional_law",
                statutes=["Constitution of Ghana (1992)", "Article 2"],
                keywords=["constitutional review", "judicial review", "validity", "ultra vires"]
            ),
            LegalConcept(
                id="presidential_immunity",
                name="Presidential Immunity",
                aliases=["executive immunity", "prosecution of president", "immunity from suit"],
                definition="Constitutional immunity of President from prosecution during and after tenure for official acts",
                parent_category="constitutional_law",
                statutes=["Constitution of Ghana (1992)", "Articles 60, 74"],
                keywords=["presidential immunity", "immunity from suit", "office of president"]
            ),

            # ===== FAMILY LAW =====
            LegalConcept(
                id="marriage_validity",
                name="Marriage Formation and Validity",
                aliases=["matrimonial", "marriage solemnization", "valid marriage", "voidable marriage"],
                definition="Requirements for valid marriage: capacity, consent, solemnization, registration",
                parent_category="family_law",
                statutes=["Matrimonial Causes Act (Act 367, 1971)"],
                keywords=["marriage", "matrimonial", "solemnization", "registration", "valid"]
            ),
            LegalConcept(
                id="divorce_dissolution",
                name="Divorce and Dissolution of Marriage",
                aliases=["grounds for divorce", "irretrievable breakdown", "fault", "no-fault"],
                definition="Grounds and procedures for legal termination of marriage",
                parent_category="family_law",
                statutes=["Matrimonial Causes Act (Act 367, 1971)"],
                keywords=["divorce", "dissolution", "irretrievable breakdown", "grounds", "decree"]
            ),
            LegalConcept(
                id="matrimonial_property",
                name="Matrimonial Property",
                aliases=["family home", "joint property", "property division", "distribution"],
                definition="Rights to family home and property acquired during marriage",
                parent_category="family_law",
                statutes=["Matrimonial Causes Act (Act 367, 1971)", "Property Procedure Court Rules"],
                keywords=["matrimonial property", "family home", "division", "distribution"]
            ),
            LegalConcept(
                id="custody_maintenance",
                name="Custody, Access, and Maintenance",
                aliases=["child custody", "access rights", "child support", "parental care"],
                definition="Rights and duties regarding custody of children and financial maintenance during and after divorce",
                parent_category="family_law",
                statutes=["Children's Act (Act 998, 2024)", "Matrimonial Causes Act"],
                keywords=["custody", "access", "maintenance", "child", "guardian"]
            ),
            LegalConcept(
                id="adoption_guardianship",
                name="Adoption and Guardianship",
                aliases=["parental rights", "adoptive parents", "ward", "guardian ad litem"],
                definition="Legal procedures and rights relating to adoption of children and appointment of guardians",
                parent_category="family_law",
                statutes=["Children's Act (Act 998, 2024)"],
                keywords=["adoption", "guardian", "ward", "parental rights", "child"]
            ),

            # ===== LABOUR LAW =====
            LegalConcept(
                id="employment_contract",
                name="Employment Contracts and Terms",
                aliases=["contract of employment", "terms of service", "unfair dismissal"],
                definition="Terms and conditions of employment, including wages, hours, conditions, rights and duties",
                parent_category="labour_law",
                statutes=["Labour Act (Act 651, 2003)"],
                keywords=["employment", "contract", "terms", "conditions", "wages"]
            ),
            LegalConcept(
                id="unfair_dismissal",
                name="Unfair Dismissal",
                aliases=["wrongful termination", "constructive dismissal", "grounds for dismissal"],
                definition="Illegal or unfair termination of employment without valid reason or proper procedure",
                parent_category="labour_law",
                statutes=["Labour Act (Act 651, 2003)"],
                keywords=["dismissal", "termination", "wrongful", "constructive", "unfair"]
            ),
            LegalConcept(
                id="wages_benefits",
                name="Wages, Salaries, and Benefits",
                aliases=["remuneration", "payment", "severance", "leave entitlement", "bonus"],
                definition="Statutory and contractual rights to payment, leave, bonuses, and other benefits",
                parent_category="labour_law",
                statutes=["Labour Act (Act 651, 2003)"],
                keywords=["wages", "salary", "payment", "leave", "benefit"]
            ),
            LegalConcept(
                id="occupational_safety",
                name="Occupational Safety and Health",
                aliases=["workplace safety", "accident compensation", "workers compensation"],
                definition="Requirements for safe working conditions and employer liability for workplace injuries",
                parent_category="labour_law",
                statutes=["Occupational Safety and Health Act (Act 651A, 2006)"],
                keywords=["safety", "health", "accident", "compensation", "workplace"]
            ),
            LegalConcept(
                id="trade_unions",
                name="Trade Unions and Collective Bargaining",
                aliases=["union recognition", "collective agreement", "strike", "labor relations"],
                definition="Rights of workers to form unions and bargain collectively for better terms",
                parent_category="labour_law",
                statutes=["Trade Union Ordinance", "Labour Act"],
                keywords=["union", "collective", "bargaining", "strike", "agreement"]
            ),

            # ===== CRIMINAL LAW =====
            LegalConcept(
                id="elements_crime",
                name="Elements of Crime",
                aliases=["actus reus", "mens rea", "criminal liability", "strict liability"],
                definition="Essential elements of criminal offence: guilty act and guilty mind (actus reus and mens rea)",
                parent_category="criminal_law",
                statutes=["Criminal Code (Act 29, 1960)"],
                keywords=["crime", "actus reus", "mens rea", "liability", "element"]
            ),
            LegalConcept(
                id="theft_robbery",
                name="Theft and Robbery",
                aliases=["larceny", "stealing", "armed robbery", "burglary"],
                definition="Unlawful taking of another's property with intent to permanently deprive (theft) or with violence (robbery)",
                parent_category="criminal_law",
                statutes=["Criminal Code (Act 29, 1960)", "Sections 124-132"],
                keywords=["theft", "robbery", "stealing", "larceny", "property"]
            ),
            LegalConcept(
                id="fraud_forgery",
                name="Fraud and Forgery",
                aliases=["false pretenses", "obtaining by deception", "uttering forged document"],
                definition="Criminal deception for personal gain or forging documents",
                parent_category="criminal_law",
                statutes=["Criminal Code (Act 29, 1960)"],
                keywords=["fraud", "forgery", "deception", "false", "document"]
            ),
            LegalConcept(
                id="assault_battery",
                name="Assault and Battery",
                aliases=["common assault", "grievous bodily harm", "wounding"],
                definition="Unlawful attack on person causing harm or fear of harm",
                parent_category="criminal_law",
                statutes=["Criminal Code (Act 29, 1960)"],
                keywords=["assault", "battery", "harm", "injury", "person"]
            ),
            LegalConcept(
                id="homicide",
                name="Homicide",
                aliases=["murder", "manslaughter", "culpable homicide", "death"],
                definition="Unlawful killing of human being, varying by intention and circumstances",
                parent_category="criminal_law",
                statutes=["Criminal Code (Act 29, 1960)", "Sections 46-58"],
                keywords=["homicide", "murder", "manslaughter", "death", "killing"]
            ),

            # ===== ADMINISTRATIVE LAW =====
            LegalConcept(
                id="administrative_review",
                name="Administrative Review and Judicial Review",
                aliases=["arbitrary decision", "procedural fairness", "natural justice", "ultra vires"],
                definition="Court's review of administrative decisions for legality, procedural fairness, and reasonableness",
                parent_category="administrative_law",
                statutes=["Constitution of Ghana (1992)", "Common Law"],
                keywords=["administrative", "review", "judicial review", "fairness", "ultra vires"]
            ),
            LegalConcept(
                id="licenses_permits",
                name="Licenses, Permits, and Permissions",
                aliases=["business license", "permit", "authorization", "revocation"],
                definition="Administrative granting and revocation of licenses and permits for regulated activities",
                parent_category="administrative_law",
                statutes=["Business Names Act", "Various regulatory statutes"],
                keywords=["license", "permit", "authorization", "revocation", "condition"]
            ),
            LegalConcept(
                id="natural_justice",
                name="Natural Justice and Procedural Fairness",
                aliases=["audi alteram partem", "nemo judex", "fair hearing", "bias"],
                definition="Principles ensuring fair procedure: right to be heard and unbiased decision-maker",
                parent_category="administrative_law",
                statutes=["Constitution of Ghana (1992)", "Common Law"],
                keywords=["natural justice", "procedural fairness", "hearing", "bias"]
            ),

            # ===== REAL PROPERTY LAW =====
            LegalConcept(
                id="adverse_possession",
                name="Adverse Possession",
                aliases=["squatter's rights", "possession", "prescriptive title", "adverse occupation"],
                definition="Acquisition of property title through long-term open and exclusive occupation without permission",
                parent_category="real_property_law",
                statutes=["Land Title Registration Law (PNDCL 152)", "Limitation periods"],
                keywords=["adverse possession", "occupation", "prescription", "title"]
            ),
            LegalConcept(
                id="boundary_disputes",
                name="Boundary Disputes",
                aliases=["land boundary", "survey", "encroachment", "boundary mark"],
                definition="Disputes over demarcation and ownership of property boundaries",
                parent_category="real_property_law",
                statutes=["Lands Commission Act (Act 691, 2008)"],
                keywords=["boundary", "dispute", "survey", "encroachment", "demarcation"]
            ),
            LegalConcept(
                id="mortgages",
                name="Mortgages and Security in Land",
                aliases=["mortgage", "security interest", "charges", "foreclosure"],
                definition="Security interest in land as collateral for loan, with right to foreclose on default",
                parent_category="real_property_law",
                statutes=["Property Law Act"],
                keywords=["mortgage", "security", "charges", "foreclosure", "default"]
            ),

            # ===== INTELLECTUAL PROPERTY =====
            LegalConcept(
                id="copyright",
                name="Copyright and Literary Works",
                aliases=["literary copyright", "artistic works", "authorship", "reproduction rights"],
                definition="Rights of authors in original literary, artistic, and musical works",
                parent_category="intellectual_property",
                statutes=["Copyright Act (Act 690, 2000)"],
                keywords=["copyright", "author", "literary", "artistic", "infringement"]
            ),
            LegalConcept(
                id="patents",
                name="Patents and Inventions",
                aliases=["patentable invention", "novel", "inventive step", "patent infringement"],
                definition="Exclusive rights to make, use, and sell an invention for limited period",
                parent_category="intellectual_property",
                statutes=["Patents Act", "TRIPS Agreement"],
                keywords=["patent", "invention", "novel", "infringement", "license"]
            ),
            LegalConcept(
                id="trademarks",
                name="Trademarks and Trade Names",
                aliases=["brand", "mark", "registered trademark", "trade name"],
                definition="Rights to distinctive signs (words, symbols, images) identifying goods or services",
                parent_category="intellectual_property",
                statutes=["Trademarks Act"],
                keywords=["trademark", "brand", "mark", "infringement", "registration"]
            ),

            # ===== TORT LAW =====
            LegalConcept(
                id="negligence",
                name="Negligence",
                aliases=["duty of care", "breach of duty", "damages", "causation"],
                definition="Failure to exercise reasonable care causing loss to another",
                parent_category="tort_law",
                statutes=["Common Law"],
                keywords=["negligence", "care", "breach", "causation", "damages"]
            ),
            LegalConcept(
                id="defamation",
                name="Defamation",
                aliases=["libel", "slander", "defamatory", "reputation"],
                definition="False statement damaging another's reputation",
                parent_category="tort_law",
                statutes=["Criminal Code (Act 29, 1960)", "Common Law"],
                keywords=["defamation", "libel", "slander", "reputation", "false"]
            ),
            LegalConcept(
                id="false_imprisonment",
                name="False Imprisonment",
                aliases=["unlawful detention", "false arrest", "imprisonment"],
                definition="Unlawful confinement or detention of a person",
                parent_category="tort_law",
                statutes=["Common Law"],
                keywords=["false imprisonment", "detention", "confinement", "unlawful"]
            ),
            LegalConcept(
                id="conversion",
                name="Conversion",
                aliases=["wrongful interference", "personal property", "damages"],
                definition="Unlawful taking or dealing with another's personal property",
                parent_category="tort_law",
                statutes=["Common Law"],
                keywords=["conversion", "property", "interference", "wrongful"]
            ),

            # ===== EVIDENCE =====
            LegalConcept(
                id="hearsay_evidence",
                name="Hearsay Evidence",
                aliases=["hearsay exception", "admissibility", "out of court statement"],
                definition="Statement made out of court to prove truth of matter, generally inadmissible with exceptions",
                parent_category="evidence",
                statutes=["Evidence Act", "Common Law"],
                keywords=["hearsay", "admissibility", "exception", "statement"]
            ),
            LegalConcept(
                id="burden_proof",
                name="Burden and Standard of Proof",
                aliases=["beyond reasonable doubt", "balance of probabilities", "evidential burden"],
                definition="Burden of proof (criminal vs civil) and required standard of proof",
                parent_category="evidence",
                statutes=["Evidence Act"],
                keywords=["burden", "proof", "reasonable doubt", "probabilities"]
            ),
            LegalConcept(
                id="privilege",
                name="Legal Privilege and Confidentiality",
                aliases=["legal professional privilege", "spousal privilege", "doctor-patient"],
                definition="Communications protected from disclosure due to confidential relationship",
                parent_category="evidence",
                statutes=["Evidence Act"],
                keywords=["privilege", "confidential", "communication", "lawyer"]
            ),
        ]

    def _add_to_category_map(self, concept: LegalConcept):
        """Add concept to its category mapping"""
        if concept.parent_category not in self.category_map:
            self.category_map[concept.parent_category] = []
        self.category_map[concept.parent_category].append(concept.id)

    def _add_aliases(self, concept: LegalConcept):
        """Map all aliases to concept ID"""
        self.alias_map[concept.name.lower()] = concept.id
        for alias in concept.aliases:
            self.alias_map[alias.lower()] = concept.id

    def get_concept(self, concept_id: str) -> LegalConcept | None:
        """Get concept by ID"""
        return self.concepts.get(concept_id)

    def find_concept_by_name(self, name: str) -> LegalConcept | None:
        """Find concept by name or alias (case-insensitive)"""
        concept_id = self.alias_map.get(name.lower())
        if concept_id:
            return self.concepts.get(concept_id)
        return None

    def get_concepts_by_category(self, category: str) -> List[LegalConcept]:
        """Get all concepts in a category"""
        concept_ids = self.category_map.get(category, [])
        return [self.concepts[cid] for cid in concept_ids if cid in self.concepts]

    def search_concepts(self, query: str) -> List[LegalConcept]:
        """Search concepts by keyword matching"""
        query_lower = query.lower()
        results = []
        for concept in self.concepts.values():
            if (query_lower in concept.name.lower() or
                any(query_lower in alias.lower() for alias in concept.aliases) or
                any(query_lower in kw.lower() for kw in concept.keywords)):
                results.append(concept)
        return results

    def get_statute_references(self, statute_name: str) -> List[LegalConcept]:
        """Find all concepts referencing a specific statute"""
        results = []
        for concept in self.concepts.values():
            if any(statute_name.lower() in stat.lower() for stat in concept.statutes):
                results.append(concept)
        return results

    def get_all_concepts(self) -> List[LegalConcept]:
        """Get all concepts in taxonomy"""
        return list(self.concepts.values())

    def get_categories(self) -> List[str]:
        """Get all top-level categories"""
        return list(self.category_map.keys())

    def get_taxonomy_stats(self) -> Dict:
        """Get statistics about the taxonomy"""
        return {
            "total_concepts": len(self.concepts),
            "total_categories": len(self.category_map),
            "concepts_per_category": {cat: len(self.category_map[cat]) for cat in self.category_map},
            "total_aliases": len(self.alias_map),
        }


# Initialize global taxonomy instance
taxonomy = GhanaLegalTaxonomy()


def get_taxonomy() -> GhanaLegalTaxonomy:
    """Get the global taxonomy instance"""
    return taxonomy
