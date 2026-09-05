import React, { useState, useEffect } from 'react';
import { 
  Search, ShieldCheck, AlertTriangle, XCircle, CheckCircle2, 
  Wand2, FileText, Download, TrendingUp, Cpu, Layers, RefreshCw, Code, Check, Link as LinkIcon
} from 'lucide-react';
import BacklinkManager from './components/BacklinkManager';
import { apiFetch } from './api';

export default function App() {
  const [mainTab, setMainTab] = useState('seo'); // 'seo' | 'backlinks'
  const [target, setTarget] = useState('https://example.com');
  const [keyword, setKeyword] = useState('seo optimization');
  const [loading, setLoading] = useState(false);
  const [auditData, setAuditData] = useState(null);
  const [history, setHistory] = useState([]);
  const [activeModal, setActiveModal] = useState(null); // { type: 'diff'|'snippet', data: ... }
  const [fixLoading, setFixLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  // Load audit history
  const fetchHistory = async (targetUrl) => {
    try {
      const { ok, data } = await apiFetch(`/api/history?target=${encodeURIComponent(targetUrl || '')}`);
      if (ok && Array.isArray(data)) {
        setHistory(data);
      }
    } catch (e) {
      console.error("History fetch error", e);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleAudit = async (e) => {
    if (e) e.preventDefault();
    if (!target.trim()) return;

    setLoading(true);
    try {
      const { ok, status, data } = await apiFetch('/api/audit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target: target.trim(), keyword: keyword.trim() }),
      });
      if (ok && data.success) {
        setAuditData(data);
        fetchHistory(target.trim());
      } else {
        const errMsg = data.detail || data.error || (status ? `HTTP ${status} server error` : 'Unknown error');
        alert(`Audit failed: ${errMsg}`);
      }
    } catch (err) {
      alert(`Network error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleApplyFix = async (checkId) => {
    setFixLoading(true);
    try {
      const isLocal = auditData?.target_type === 'file';
      const payload = isLocal 
        ? { file_path: auditData.target, check_id: checkId, keyword: keyword }
        : { check_id: checkId, keyword: keyword };

      const { ok, data } = await apiFetch('/api/fix', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (ok && data.success) {
        if (isLocal && data.diff) {
          setActiveModal({ type: 'diff', data: data });
          // Re-run audit to show updated score
          handleAudit();
        } else {
          setActiveModal({ type: 'snippet', data: data.fix_details });
        }
      } else {
        alert(`Fix execution failed: ${data.detail || 'Could not apply fix.'}`);
      }
    } catch (err) {
      alert(`Error applying fix: ${err.message}`);
    } finally {
      setFixLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981';
    if (score >= 50) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div style={{ minHeight: '100vh', paddingBottom: '60px' }}>
      {/* Top Navbar */}
      <header style={{ borderBottom: '1px solid var(--border-color)', background: '#090d16', padding: '16px 32px' }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'var(--primary-gradient)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Cpu color="#fff" size={24} />
            </div>
            <div>
              <h1 style={{ fontSize: '18px', fontWeight: 800, color: '#fff', letterSpacing: '-0.5px' }}>
                LOCAL AGENTIC <span style={{ color: '#818cf8' }}>SEO ANALYZER & BACKLINK ENGINE</span>
              </h1>
              <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Autonomous On-Page Audit, In-Place Fixes & Backlink Manager</p>
            </div>
          </div>
          
          {/* Main Mode Toggle Buttons */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <button 
              className={`tab-btn ${mainTab === 'seo' ? 'active' : ''}`}
              onClick={() => setMainTab('seo')}
            >
              <Cpu size={16} /> On-Page SEO Analyzer
            </button>
            <button 
              className={`tab-btn ${mainTab === 'backlinks' ? 'active' : ''}`}
              onClick={() => setMainTab('backlinks')}
            >
              <LinkIcon size={16} /> Backlink Manager & Reports
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main style={{ maxWidth: '1280px', margin: '32px auto 0', padding: '0 24px' }}>
        
        {mainTab === 'backlinks' ? (
          <BacklinkManager />
        ) : (
          <>
            {/* Input Control Card */}
            <section className="glass-card" style={{ marginBottom: '32px' }}>
              <form onSubmit={handleAudit} style={{ display: 'grid', gridTemplateColumns: '2fr 1fr auto', gap: '16px', alignItems: 'center' }}>
                <div>
                  <label style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '6px', display: 'block' }}>
                    TARGET URL OR LOCAL HTML FILE PATH
                  </label>
                  <div style={{ position: 'relative' }}>
                    <Search size={18} color="#64748b" style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)' }} />
                    <input 
                      type="text" 
                      className="input-field" 
                      style={{ paddingLeft: '42px' }}
                      placeholder="https://example.com or C:\path\to\index.html"
                      value={target}
                      onChange={(e) => setTarget(e.target.value)}
                    />
                  </div>
                </div>

                <div>
                  <label style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '6px', display: 'block' }}>
                    PRIMARY TARGET KEYWORD
                  </label>
                  <input 
                    type="text" 
                    className="input-field"
                    placeholder="e.g. on-page seo guide"
                    value={keyword}
                    onChange={(e) => setKeyword(e.target.value)}
                  />
                </div>

                <div style={{ alignSelf: 'end' }}>
                  <button type="submit" className="btn-primary" disabled={loading} style={{ width: '100%', height: '45px', justifyContent: 'center' }}>
                    {loading ? <RefreshCw className="animate-spin" size={18} /> : <Wand2 size={18} />}
                    {loading ? 'Agent Auditing...' : 'RUN AGENT AUDIT'}
                  </button>
                </div>
              </form>
            </section>

            {/* Dashboard Results Section */}
            {auditData && (
              <div style={{ display: 'grid', gap: '32px' }}>
                
                {/* Overview & Score Card */}
                <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '24px' }}>
                  
                  {/* Overall Score Circle */}
                  <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
                    <h3 style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '16px' }}>
                      Overall SEO Score
                    </h3>
                    <div 
                      className="score-circle"
                      style={{ 
                        border: `8px solid ${getScoreColor(auditData.overall_score)}`,
                        color: getScoreColor(auditData.overall_score),
                        boxShadow: `0 0 25px ${getScoreColor(auditData.overall_score)}33`
                      }}
                    >
                      {auditData.overall_score}
                    </div>
                    <div style={{ marginTop: '16px' }}>
                      <span style={{ fontSize: '13px', color: '#e2e8f0', fontWeight: 600 }}>
                        Page Type: <span style={{ color: '#818cf8', textTransform: 'uppercase' }}>{auditData.page_type}</span>
                      </span>
                    </div>
                  </div>

                  {/* Agent Planner Summary & Category Breakdown */}
                  <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                        <Cpu size={18} color="#818cf8" />
                        <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#fff' }}>Agent Planner Strategy</h3>
                      </div>
                      <p style={{ fontSize: '14px', color: '#cbd5e1', background: '#0f172a', padding: '12px 16px', borderRadius: '10px', borderLeft: '4px solid #818cf8', marginBottom: '20px' }}>
                        {auditData.planner_summary}
                      </p>
                    </div>

                    <div>
                      <h4 style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '12px' }}>
                        Category Breakdown
                      </h4>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '12px' }}>
                        {Object.entries(auditData.category_scores || {}).map(([cat, score]) => (
                          <div key={cat} style={{ background: '#0f172a', padding: '10px 14px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
                            <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>{cat}</div>
                            <div style={{ fontSize: '18px', fontWeight: 800, color: getScoreColor(score), marginTop: '4px' }}>
                              {score} / 100
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                </div>

                {/* Keyword Research & SERP Insights Card */}
                {auditData.keyword_research && auditData.keyword_research.keyword && (
                  <section className="glass-card">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
                      <TrendingUp size={20} color="#34d399" />
                      <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Keyword Research & SERP Intelligence</h3>
                      <span style={{ fontSize: '11px', background: '#064e3b', color: '#6ee7b7', padding: '2px 8px', borderRadius: '12px', fontWeight: 600 }}>Free Pytrends + Google Autosuggest</span>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px' }}>
                      
                      {/* Autosuggest */}
                      <div style={{ background: '#0f172a', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
                        <h4 style={{ fontSize: '13px', fontWeight: 700, color: '#38bdf8', marginBottom: '10px' }}>Google Autosuggest Ideas</h4>
                        <ul style={{ fontSize: '13px', color: '#cbd5e1', listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                          {(auditData.keyword_research.autosuggest || []).slice(0, 6).map((term, i) => (
                            <li key={i} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                              <span style={{ color: '#38bdf8' }}>•</span> {term}
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* PAA Questions */}
                      <div style={{ background: '#0f172a', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
                        <h4 style={{ fontSize: '13px', fontWeight: 700, color: '#a78bfa', marginBottom: '10px' }}>People Also Ask (PAA)</h4>
                        <ul style={{ fontSize: '12px', color: '#cbd5e1', listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                          {(auditData.keyword_research.paa_questions || []).slice(0, 4).map((q, i) => (
                            <li key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '6px' }}>
                              <span style={{ color: '#a78bfa' }}>?</span> {q}
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* KD Proxy & Interest */}
                      <div style={{ background: '#0f172a', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                        <div>
                          <h4 style={{ fontSize: '13px', fontWeight: 700, color: '#f43f5e', marginBottom: '8px' }}>Keyword Difficulty Proxy</h4>
                          <div style={{ fontSize: '24px', fontWeight: 800, color: '#f43f5e' }}>
                            {auditData.keyword_research.difficulty_proxy} / 100
                          </div>
                          <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>Calculated via exact match density / search volume ratio</p>
                        </div>
                        <div>
                          <span style={{ fontSize: '12px', color: '#cbd5e1', fontWeight: 600 }}>Avg 12M Trend Interest: </span>
                          <strong style={{ color: '#10b981' }}>{auditData.keyword_research.avg_interest}</strong>
                        </div>
                      </div>

                    </div>
                  </section>
                )}

                {/* Comprehensive SEO Checks Table */}
                <section className="glass-card">
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <Layers size={20} color="#818cf8" />
                      <h3 style={{ fontSize: '18px', fontWeight: 700 }}>On-Page SEO Checklist & Autonomous Fixes</h3>
                    </div>
                    <a 
                      href={`/api/export/markdown/${auditData.audit_id || 1}`}
                      target="_blank"
                      rel="noreferrer"
                      className="btn-secondary"
                    >
                      <Download size={14} /> Export Markdown Report
                    </a>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    {auditData.checks.map((chk) => (
                      <div key={chk.id} style={{ background: '#0f172a', borderRadius: '12px', border: '1px solid var(--border-color)', padding: '16px 20px' }}>
                        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '16px' }}>
                          <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                              {chk.status === 'pass' && <span className="badge-pass"><CheckCircle2 size={12}/> PASS</span>}
                              {chk.status === 'warn' && <span className="badge-warn"><AlertTriangle size={12}/> WARNING</span>}
                              {chk.status === 'fail' && <span className="badge-fail"><XCircle size={12}/> FAIL</span>}
                              <h4 style={{ fontSize: '15px', fontWeight: 700, color: '#fff' }}>{chk.name}</h4>
                              <span style={{ fontSize: '11px', color: 'var(--text-muted)', background: '#1e293b', padding: '2px 8px', borderRadius: '6px' }}>{chk.category}</span>
                            </div>
                            <p style={{ fontSize: '13px', color: '#cbd5e1', marginBottom: '8px' }}>{chk.message}</p>
                            {chk.recommendation && (
                              <p style={{ fontSize: '12px', color: '#94a3b8', fontStyle: 'italic' }}>
                                💡 <strong>Recommendation:</strong> {chk.recommendation}
                              </p>
                            )}
                          </div>

                          {chk.fixable && chk.status !== 'pass' && (
                            <button 
                              onClick={() => handleApplyFix(chk.id)}
                              className="btn-secondary"
                              disabled={fixLoading}
                              style={{ borderColor: '#818cf8', color: '#a5b4fc', whiteSpace: 'nowrap' }}
                            >
                              <Wand2 size={14} /> {auditData.target_type === 'file' ? 'Apply In-Place Fix' : 'Generate Fix Snippet'}
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </section>

              </div>
            )}
          </>
        )}

      </main>

      {/* Fix Modal / Diff Viewer */}
      {activeModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '24px' }}>
          <div className="glass-card" style={{ maxWidth: '800px', width: '100%', maxHeight: '85vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#fff' }}>
                {activeModal.type === 'diff' ? 'Unified File Diff (In-Place Fix Applied)' : 'Autonomous Fix Recommendation'}
              </h3>
              <button onClick={() => setActiveModal(null)} className="btn-secondary">Close</button>
            </div>

            {activeModal.type === 'diff' ? (
              <div>
                <p style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '12px' }}>
                  Backup created at: <code style={{ color: '#38bdf8' }}>{activeModal.data.backup_path}</code>
                </p>
                <pre className="diff-view">{activeModal.data.diff || 'File updated successfully.'}</pre>
              </div>
            ) : (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>SUGGESTED CODE SNIPPET</span>
                  <button onClick={() => copyToClipboard(activeModal.data.suggested_code)} className="btn-secondary">
                    {copied ? <Check size={14} color="#10b981" /> : <Code size={14} />}
                    {copied ? 'Copied!' : 'Copy Code'}
                  </button>
                </div>
                <pre className="diff-view">{activeModal.data.suggested_code}</pre>
                
                {activeModal.data.critique && (
                  <div style={{ marginTop: '16px', background: '#0f172a', padding: '12px', borderRadius: '8px', borderLeft: '4px solid #10b981' }}>
                    <h5 style={{ fontSize: '12px', fontWeight: 700, color: '#10b981' }}>Self-Critique Engine Status</h5>
                    <p style={{ fontSize: '12px', color: '#cbd5e1', marginTop: '4px' }}>
                      {activeModal.data.critique.valid ? '✅ Passed character limits & keyword checks.' : '⚠️ Critique warning: ' + (activeModal.data.critique.feedback || []).join(' ')}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

    </div>
  );
}
