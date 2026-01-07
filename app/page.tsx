'use client';

import { useState } from 'react';

export default function Home() {
  const [activeTab, setActiveTab] = useState('search');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [caseDetails, setCaseDetails] = useState('');
  const [generating, setGenerating] = useState(false);
  const [generatedBrief, setGeneratedBrief] = useState('');

  // Mock Ghana Statutes Database
  const ghanaStatutes = [
    { id: 1, name: 'Criminal Procedure Code', year: 1960, sections: 50 },
    { id: 2, name: 'Evidence Act', year: 1975, sections: 65 },
    { id: 3, name: 'Matrimonial Causes Act', year: 1971, sections: 45 },
    { id: 4, name: 'Land Act', year: 2000, sections: 80 },
    { id: 5, name: 'Companies Act', year: 2019, sections: 120 },
    { id: 6, name: 'Ghana Labour Act', year: 2003, sections: 60 },
    { id: 7, name: 'Wills Act', year: 1971, sections: 55 },
    { id: 8, name: 'Property Rights Act', year: 2000, sections: 70 },
  ];

  const handleSearchStatutes = (e: React.FormEvent) => {
    e.preventDefault();
    const results = ghanaStatutes.filter(s => 
      s.name.toLowerCase().includes(searchQuery.toLowerCase())
    );
    setSearchResults(results);
  };

  const handleGenerateBrief = async () => {
    if (!caseDetails) {
      alert('Please enter case details');
      return;
    }
    
    setGenerating(true);
    setTimeout(() => {
      setGeneratedBrief(`
CASE BRIEF - FIHR FORMAT

Case Name: ${caseDetails}
Prepared: ${new Date().toLocaleDateString()}

FACTS:
The matter involves a legal dispute regarding property rights and contractual obligations. The parties involved had previously entered into an agreement which has been disputed.

ISSUE:
Whether the defendant breached the terms of the agreement and whether the plaintiff is entitled to damages.

HOLDING:
The court found in favor of the plaintiff, determining that the defendant did indeed breach the material terms of the agreement.

REASONING:
The evidence presented clearly demonstrated that:
1. A valid contract was formed between the parties
2. The defendant failed to perform material obligations
3. The plaintiff suffered damages as a result

REMEDY:
The court awarded damages to the plaintiff in the amount to be assessed by the registrar.

APPLICATION:
This case establishes important precedent regarding contract interpretation in Ghanaian law.
      `);
      setGenerating(false);
    }, 1500);
  };

  const handleGenerateDocument = async (type: string) => {
    setGenerating(true);
    setTimeout(() => {
      setGeneratedBrief(`
${type.toUpperCase()} - GENERATED

Date: ${new Date().toLocaleDateString()}

[Legal document content generated according to Ghanaian legal standards]

This ${type} has been prepared in compliance with Ghana's statutory requirements and best practices. 

Key sections included:
- Header and party identification
- Terms and conditions
- Legal obligations
- Jurisdiction and governing law
- Dispute resolution
- Signature block

Please review and customize for your specific situation.
      `);
      setGenerating(false);
    }, 1500);
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      {/* Header */}
      <header style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', padding: '30px' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <h1 style={{ fontSize: '2.5em', marginBottom: '10px' }}>⚖️ GLIS v2.0</h1>
          <p style={{ fontSize: '1.1em', opacity: 0.95 }}>Ghana Legal Intelligence System - AI-Powered Legal Research</p>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '30px 20px' }}>
        {/* Tabs */}
        <div style={{ 
          display: 'flex', 
          gap: '10px', 
          marginBottom: '30px',
          borderBottom: '2px solid #ddd',
          flexWrap: 'wrap'
        }}>
          {[
            { id: 'search', label: '🔍 Search Statutes' },
            { id: 'brief', label: '📄 Generate Brief' },
            { id: 'documents', label: '📋 Legal Documents' },
            { id: 'strategy', label: '⚡ Strategy Analysis' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                padding: '12px 20px',
                border: 'none',
                background: activeTab === tab.id ? '#667eea' : 'transparent',
                color: activeTab === tab.id ? 'white' : '#667eea',
                cursor: 'pointer',
                fontSize: '1em',
                fontWeight: '500',
                borderBottom: activeTab === tab.id ? '3px solid #667eea' : 'none',
                transition: 'all 0.3s',
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div style={{ background: 'white', borderRadius: '10px', padding: '30px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
          
          {/* Search Statutes */}
          {activeTab === 'search' && (
            <div>
              <h2 style={{ color: '#667eea', marginBottom: '20px' }}>Search Ghana Statutes</h2>
              <form onSubmit={handleSearchStatutes} style={{ marginBottom: '30px' }}>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <input
                    type="text"
                    placeholder="Search statutes (e.g., Criminal Procedure Code, Land Act)..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    style={{
                      flex: 1,
                      padding: '12px',
                      border: '1px solid #ddd',
                      borderRadius: '5px',
                      fontSize: '1em',
                    }}
                  />
                  <button
                    type="submit"
                    style={{
                      padding: '12px 30px',
                      background: '#667eea',
                      color: 'white',
                      border: 'none',
                      borderRadius: '5px',
                      cursor: 'pointer',
                      fontWeight: 'bold',
                    }}
                  >
                    Search
                  </button>
                </div>
              </form>

              {searchResults.length > 0 ? (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#333' }}>Results ({searchResults.length})</h3>
                  <div style={{ display: 'grid', gap: '15px' }}>
                    {searchResults.map(statute => (
                      <div key={statute.id} style={{
                        padding: '15px',
                        border: '1px solid #ddd',
                        borderRadius: '5px',
                        background: '#f9f9f9',
                      }}>
                        <h4 style={{ color: '#667eea', marginBottom: '5px' }}>{statute.name}</h4>
                        <p style={{ color: '#666', margin: '5px 0' }}>Year: {statute.year} | Sections: {statute.sections}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ) : searchQuery && (
                <p style={{ color: '#999' }}>No statutes found. Try searching for: Criminal Procedure Code, Evidence Act, Land Act...</p>
              )}
            </div>
          )}

          {/* Generate Brief */}
          {activeTab === 'brief' && (
            <div>
              <h2 style={{ color: '#667eea', marginBottom: '20px' }}>Generate Case Brief (FIHR Format)</h2>
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>Case Details:</label>
                <textarea
                  placeholder="Enter case name, facts, and key details here..."
                  value={caseDetails}
                  onChange={(e) => setCaseDetails(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '12px',
                    border: '1px solid #ddd',
                    borderRadius: '5px',
                    minHeight: '120px',
                    fontSize: '1em',
                    fontFamily: 'Arial, sans-serif',
                  }}
                />
              </div>
              <button
                onClick={handleGenerateBrief}
                disabled={generating}
                style={{
                  padding: '12px 30px',
                  background: generating ? '#ccc' : '#667eea',
                  color: 'white',
                  border: 'none',
                  borderRadius: '5px',
                  cursor: generating ? 'not-allowed' : 'pointer',
                  fontWeight: 'bold',
                  fontSize: '1em',
                }}
              >
                {generating ? 'Generating...' : 'Generate Brief'}
              </button>

              {generatedBrief && (
                <div style={{
                  marginTop: '30px',
                  padding: '20px',
                  background: '#f0f5ff',
                  borderRadius: '5px',
                  borderLeft: '4px solid #667eea',
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'monospace',
                  fontSize: '0.95em',
                  color: '#333',
                }}>
                  {generatedBrief}
                </div>
              )}
            </div>
          )}

          {/* Legal Documents */}
          {activeTab === 'documents' && (
            <div>
              <h2 style={{ color: '#667eea', marginBottom: '20px' }}>Generate Legal Documents</h2>
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '15px'
              }}>
                {[
                  'Contract',
                  'Deed',
                  'Will',
                  'Memorandum of Understanding',
                  'Power of Attorney',
                  'Affidavit',
                  'Petition',
                  'Application',
                  'Notice',
                  'Settlement Agreement',
                ].map((docType) => (
                  <button
                    key={docType}
                    onClick={() => handleGenerateDocument(docType)}
                    style={{
                      padding: '20px',
                      background: '#f0f5ff',
                      border: '2px solid #667eea',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      fontWeight: 'bold',
                      color: '#667eea',
                      fontSize: '1em',
                      transition: 'all 0.3s',
                    }}
                    onMouseOver={(e) => {
                      e.currentTarget.style.background = '#667eea';
                      e.currentTarget.style.color = 'white';
                    }}
                    onMouseOut={(e) => {
                      e.currentTarget.style.background = '#f0f5ff';
                      e.currentTarget.style.color = '#667eea';
                    }}
                  >
                    {docType}
                  </button>
                ))}
              </div>

              {generatedBrief && (
                <div style={{
                  marginTop: '30px',
                  padding: '20px',
                  background: '#f0f5ff',
                  borderRadius: '5px',
                  borderLeft: '4px solid #667eea',
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'monospace',
                  fontSize: '0.95em',
                  color: '#333',
                }}>
                  {generatedBrief}
                </div>
              )}
            </div>
          )}

          {/* Strategy Analysis */}
          {activeTab === 'strategy' && (
            <div>
              <h2 style={{ color: '#667eea', marginBottom: '20px' }}>Litigation Strategy Analysis</h2>
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>Case Background:</label>
                <textarea
                  placeholder="Describe your case, parties involved, issues, and current stage..."
                  defaultValue={caseDetails}
                  onChange={(e) => setCaseDetails(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '12px',
                    border: '1px solid #ddd',
                    borderRadius: '5px',
                    minHeight: '120px',
                    fontSize: '1em',
                  }}
                />
              </div>
              <button
                onClick={() => {
                  setGenerating(true);
                  setTimeout(() => {
                    setGeneratedBrief(`
LITIGATION STRATEGY ANALYSIS

Case Assessment Date: ${new Date().toLocaleDateString()}

STRENGTHS:
✓ Strong contractual evidence
✓ Precedent supports your position
✓ Witness credibility established

WEAKNESSES:
✗ Procedural compliance issues
✗ Potential jurisdiction challenges

RECOMMENDED STRATEGY:
1. File motion for summary judgment immediately
2. Prepare detailed chronology of events
3. Gather expert testimony on technical matters
4. Negotiate settlement while position is strong

WIN PROBABILITY: 72%

RISK FACTORS:
- Appeal potential
- Cost escalation
- Timeline delays

NEXT STEPS:
1. Prepare pleadings (2 weeks)
2. Serve on defendants (1 week)
3. Respond to replies (3 weeks)
4. Motion hearing (4-6 weeks)

Total Estimated Timeline: 10-12 weeks
Estimated Costs: GHS 15,000 - GHS 25,000
                    `);
                    setGenerating(false);
                  }, 1500);
                }}
                disabled={generating}
                style={{
                  padding: '12px 30px',
                  background: generating ? '#ccc' : '#667eea',
                  color: 'white',
                  border: 'none',
                  borderRadius: '5px',
                  cursor: generating ? 'not-allowed' : 'pointer',
                  fontWeight: 'bold',
                  fontSize: '1em',
                }}
              >
                {generating ? 'Analyzing...' : 'Analyze Strategy'}
              </button>

              {generatedBrief && (
                <div style={{
                  marginTop: '30px',
                  padding: '20px',
                  background: '#f0f5ff',
                  borderRadius: '5px',
                  borderLeft: '4px solid #667eea',
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'monospace',
                  fontSize: '0.95em',
                  color: '#333',
                }}>
                  {generatedBrief}
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer style={{
        background: '#333',
        color: 'white',
        padding: '20px',
        textAlign: 'center',
        marginTop: '50px',
      }}>
        <p>GLIS v2.0 - Ghana Legal Intelligence System | Powered by AI | {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}
