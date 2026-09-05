import React, { useState, useEffect } from 'react';
import { apiFetch, API_BASE } from '../api';
import {
  Link as LinkIcon, CheckCircle2, AlertCircle, RefreshCw, Download, 
  PlusCircle, Database, Globe, Search, ExternalLink, ShieldCheck, 
  BarChart3, FileSpreadsheet, FileText, Check, Trash2, Zap, Bot, Cpu, Play
} from 'lucide-react';

export default function BacklinkManager() {
  const [activeTab, setActiveTab] = useState('auto'); // 'auto' | 'vault' | 'add' | 'targets' | 'reports'
  const [stats, setStats] = useState({
    total_links: 0,
    today_count: 0,
    daily_goal: 300,
    goal_percentage: 0,
    verified_count: 0,
    dofollow_count: 0,
    dofollow_pct: 0,
    avg_da: 0,
    categories: {}
  });

  const [backlinks, setBacklinks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchFilter, setSearchFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [dateFilter, setDateFilter] = useState('all');

  // Auto Agent Form State
  const [autoForm, setAutoForm] = useState({
    target_url: 'https://fairepairs.com/',
    target_keyword: 'SEO optimization guide',
    author_email: 'fairpayt@gmail.com',
    count: 300
  });
  const [autoRunning, setAutoRunning] = useState(false);
  const [autoResult, setAutoResult] = useState(null);

  // Single Add Form
  const [singleForm, setSingleForm] = useState({
    target_url: 'https://example.com',
    submitted_url: '',
    anchor_text: '',
    link_type: 'dofollow',
    submission_category: 'Web 2.0',
    da_score: 35,
    notes: ''
  });

  // Bulk Add Form
  const [bulkForm, setBulkForm] = useState({
    target_url: 'https://example.com',
    urls_raw: '',
    anchor_text: '',
    link_type: 'dofollow',
    submission_category: 'Web 2.0',
    da_score: 30
  });

  const [highDaTargets, setHighDaTargets] = useState([]);
  const [verifyingId, setVerifyingId] = useState(null);
  const [batchVerifying, setBatchVerifying] = useState(false);
  const [reportDate, setReportDate] = useState(new Date().toISOString().split('T')[0]);
  const [pinging, setPinging] = useState(false);

  const handlePingIndexer = async () => {
    setPinging(true);
    try {
      const { ok, data } = await apiFetch('/api/backlinks/ping-indexer', { method: 'POST' });
      if (ok) {
        alert(data.message || 'Indexer pinged successfully!');
      } else {
        alert(`Indexer error: ${data.detail || data.message || 'Failed'}`);
      }
    } catch (e) {
      alert(`Indexer error: ${e.message}`);
    } finally {
      setPinging(false);
    }
  };

  const fetchStats = async () => {
    try {
      const { ok, data } = await apiFetch('/api/backlinks/stats');
      if (ok) {
        setStats(data);
      }
    } catch (e) {
      console.error("Failed to fetch backlink stats", e);
    }
  };

  const fetchBacklinks = async () => {
    setLoading(true);
    try {
      let url = `/api/backlinks/?limit=200`;
      if (categoryFilter !== 'all') url += `&category=${encodeURIComponent(categoryFilter)}`;
      if (statusFilter !== 'all') url += `&status=${encodeURIComponent(statusFilter)}`;
      if (dateFilter !== 'all') url += `&date_filter=${encodeURIComponent(dateFilter)}`;
      if (searchFilter) url += `&target_url=${encodeURIComponent(searchFilter)}`;

      const { ok, data } = await apiFetch(url);
      if (ok && data.items) {
        setBacklinks(data.items);
      }
    } catch (e) {
      console.error("Failed to fetch backlinks", e);
    } finally {
      setLoading(false);
    }
  };

  const fetchHighDaTargets = async () => {
    try {
      const { ok, data } = await apiFetch('/api/backlinks/high-da-targets');
      if (ok && data.targets) {
        setHighDaTargets(data.targets);
      }
    } catch (e) {
      console.error("Failed to fetch target sites", e);
    }
  };

  const [schedulerConfig, setSchedulerConfig] = useState({
    is_enabled: true,
    target_url: 'https://fairepairs.com/',
    target_keyword: 'SEO optimization guide',
    daily_goal: 300,
    last_run_at: null,
    next_run_at: null
  });

  const fetchSchedulerConfig = async () => {
    try {
      const { ok, data } = await apiFetch('/api/backlinks/scheduler');
      if (ok) {
        setSchedulerConfig(data);
      }
    } catch (e) {
      console.error("Failed to fetch scheduler config", e);
    }
  };

  const handleToggleScheduler = async (enabled) => {
    try {
      const updated = { ...schedulerConfig, is_enabled: enabled };
      const { ok, data } = await apiFetch('/api/backlinks/scheduler', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updated)
      });
      if (ok) {
        setSchedulerConfig(updated);
        fetchSchedulerConfig();
      } else {
        alert(`Failed to update scheduler: ${data.detail || 'Failed'}`);
      }
    } catch (e) {
      alert(`Failed to update scheduler: ${e.message}`);
    }
  };

  const handleTriggerScheduleNow = async () => {
    try {
      const { ok, data } = await apiFetch('/api/backlinks/scheduler/trigger', { method: 'POST' });
      if (ok) {
        alert("Daily Scheduler Triggered! 300 automated backlinks created!");
        fetchStats();
        fetchBacklinks();
        fetchSchedulerConfig();
      } else {
        alert(`Schedule trigger error: ${data.detail || 'Failed'}`);
      }
    } catch (e) {
      alert(`Schedule trigger error: ${e.message}`);
    }
  };

  const [brandProfile, setBrandProfile] = useState({
    brand_name: 'Fairepairs',
    website_url: 'https://fairepairs.com/',
    account_email: 'fairpayt@gmail.com',
    niche_industry: 'Auto Repairs & Services',
    primary_keyword: 'SEO optimization guide'
  });

  const fetchBrandProfile = async () => {
    try {
      const { ok, data } = await apiFetch('/api/backlinks/brand-profile');
      if (ok) {
        setBrandProfile(data);
        setAutoForm(prev => ({
          ...prev,
          target_url: data.website_url,
          target_keyword: data.primary_keyword,
          author_email: data.account_email
        }));
      }
    } catch (e) {
      console.error("Failed to fetch brand profile", e);
    }
  };

  const handleSaveBrandProfile = async (e) => {
    e.preventDefault();
    try {
      const { ok, data } = await apiFetch('/api/backlinks/brand-profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(brandProfile)
      });
      if (ok) {
        alert("Personal Brand Profile & Credentials saved successfully!");
        fetchSchedulerConfig();
      } else {
        alert(`Save error: ${data.detail || 'Failed'}`);
      }
    } catch (e) {
      alert(`Save error: ${e.message}`);
    }
  };

  useEffect(() => {
    fetchStats();
    fetchBacklinks();
    fetchHighDaTargets();
    fetchSchedulerConfig();
    fetchBrandProfile();
  }, [categoryFilter, statusFilter, dateFilter]);

  const handleRunAutoAgent = async (e) => {
    if (e) e.preventDefault();
    setAutoRunning(true);
    setAutoResult(null);

    try {
      const { ok, status, data } = await apiFetch('/api/backlinks/auto-agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(autoForm)
      });

      if (ok && data.success) {
        setAutoResult(data);
        fetchStats();
        fetchBacklinks();
      } else {
        alert(`Auto-Agent Error (${status}): ${data.detail || data.message || 'Execution failed'}`);
      }
    } catch (err) {
      alert(`Network / Agent Error: ${err.message}`);
    } finally {
      setAutoRunning(false);
    }
  };

  const handleSingleSubmit = async (e) => {
    e.preventDefault();
    if (!singleForm.submitted_url.trim()) return;

    try {
      const { ok, data } = await apiFetch('/api/backlinks/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(singleForm)
      });
      if (ok) {
        setSingleForm({ ...singleForm, submitted_url: '', anchor_text: '', notes: '' });
        fetchStats();
        fetchBacklinks();
        setActiveTab('vault');
      } else {
        alert(`Error adding backlink: ${data.detail || 'Failed'}`);
      }
    } catch (e) {
      alert(`Error adding backlink: ${e.message}`);
    }
  };

  const handleBulkSubmit = async (e) => {
    e.preventDefault();
    if (!bulkForm.urls_raw.trim()) return;

    try {
      const { ok, data } = await apiFetch('/api/backlinks/bulk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bulkForm)
      });
      if (ok) {
        alert(`Logged ${data.count} backlinks successfully!`);
        setBulkForm({ ...bulkForm, urls_raw: '' });
        fetchStats();
        fetchBacklinks();
        setActiveTab('vault');
      } else {
        alert(`Bulk insert failed: ${data.detail || 'Failed'}`);
      }
    } catch (e) {
      alert(`Bulk insert failed: ${e.message}`);
    }
  };

  const handleVerify = async (id) => {
    setVerifyingId(id);
    try {
      const { ok } = await apiFetch(`/api/backlinks/verify/${id}`, { method: 'POST' });
      if (ok) {
        fetchStats();
        fetchBacklinks();
      }
    } catch (e) {
      console.error("Verification failed", e);
    } finally {
      setVerifyingId(null);
    }
  };

  const handleBatchVerify = async () => {
    setBatchVerifying(true);
    try {
      const { ok, data } = await apiFetch('/api/backlinks/verify-batch?limit=20', { method: 'POST' });
      if (ok) {
        alert(`Batch Verification Complete: ${data.verified} Verified, ${data.rejected} Missing/Rejected`);
        fetchStats();
        fetchBacklinks();
      } else {
        alert(`Batch verification failed: ${data.detail || 'Failed'}`);
      }
    } catch (e) {
      alert(`Batch verification failed: ${e.message}`);
    } finally {
      setBatchVerifying(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this backlink record?")) return;
    try {
      const { ok } = await apiFetch(`/api/backlinks/${id}`, { method: 'DELETE' });
      if (ok) {
        fetchStats();
        fetchBacklinks();
      }
    } catch (e) {
      console.error("Delete failed", e);
    }
  };

  const downloadReport = (format) => {
    const url = `${API_BASE}/api/backlinks/export-report?date_str=${reportDate}&format=${format}`;
    window.open(url, '_blank');
  };

  return (
    <div className="backlink-manager-container">
      {/* Header Stat Cards & Daily Goal Tracker */}
      <div className="stats-grid">
        {/* Daily Goal Card */}
        <div className="stat-card goal-card">
          <div className="stat-header">
            <div>
              <span className="stat-title">Daily Goal (Target 300 Links)</span>
              <div className="stat-value">{stats.today_count} <span className="stat-sub">/ 300 Today</span></div>
            </div>
            <Zap className="stat-icon text-amber" />
          </div>
          <div className="progress-bar-bg">
            <div 
              className="progress-bar-fill bg-gradient-amber" 
              style={{ width: `${Math.min(100, stats.goal_percentage)}%` }} 
            />
          </div>
          <div className="stat-footer">{stats.goal_percentage}% of Daily Target Completed</div>
        </div>

        {/* Total & Verified Links */}
        <div className="stat-card">
          <div className="stat-header">
            <div>
              <span className="stat-title">Total & Verified</span>
              <div className="stat-value">{stats.total_links} <span className="stat-sub">({stats.verified_count} Live)</span></div>
            </div>
            <CheckCircle2 className="stat-icon text-green" />
          </div>
          <div className="stat-footer">
            <span className="badge badge-success">{stats.verified_count} Live Verified</span>
          </div>
        </div>

        {/* Dofollow Link Ratio */}
        <div className="stat-card">
          <div className="stat-header">
            <div>
              <span className="stat-title">Dofollow Link Ratio</span>
              <div className="stat-value">{stats.dofollow_pct}%</div>
            </div>
            <ShieldCheck className="stat-icon text-cyan" />
          </div>
          <div className="stat-footer">{stats.dofollow_count} Dofollow Backlinks</div>
        </div>

        {/* Avg Domain Authority */}
        <div className="stat-card">
          <div className="stat-header">
            <div>
              <span className="stat-title">Avg Domain Authority</span>
              <div className="stat-value">DA {stats.avg_da}</div>
            </div>
            <BarChart3 className="stat-icon text-purple" />
          </div>
          <div className="stat-footer">High Authority Profile Rating</div>
        </div>
      </div>

      {/* Main Tabs Navigation */}
      <div className="tab-navigation">
        <button 
          className={`tab-btn ${activeTab === 'auto' ? 'active' : ''}`}
          onClick={() => setActiveTab('auto')}
        >
          <Bot size={16} /> ⚡ Auto-Agent Submitter (1-Click)
        </button>
        <button 
          className={`tab-btn ${activeTab === 'vault' ? 'active' : ''}`}
          onClick={() => setActiveTab('vault')}
        >
          <Database size={16} /> Backlink Vault ({stats.total_links})
        </button>
        <button 
          className={`tab-btn ${activeTab === 'add' ? 'active' : ''}`}
          onClick={() => setActiveTab('add')}
        >
          <PlusCircle size={16} /> Manual / Bulk Paste Links
        </button>
        <button 
          className={`tab-btn ${activeTab === 'targets' ? 'active' : ''}`}
          onClick={() => setActiveTab('targets')}
        >
          <Globe size={16} /> High DA Target Directory ({highDaTargets.length})
        </button>
        <button 
          className={`tab-btn ${activeTab === 'reports' ? 'active' : ''}`}
          onClick={() => setActiveTab('reports')}
        >
          <Download size={16} /> Daily Reports & Export
        </button>
      </div>

      {/* TAB 0: AUTONOMOUS AGENT SUBMITTER */}
      {activeTab === 'auto' && (
        <div className="auto-agent-container" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Personal Brand & Account Credentials Card */}
          <div className="form-card" style={{ maxWidth: '800px', margin: '0 auto', width: '100%', borderColor: '#6366f166', background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(19, 27, 46, 1) 100%)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <div style={{ padding: '10px', background: '#3730a3', borderRadius: '12px' }}>
                <Globe size={24} color="#a5b4fc" />
              </div>
              <div>
                <h3 style={{ fontSize: '17px', margin: 0, color: '#fff' }}>
                  ⚙️ My Personal Brand & Account Credentials Settings
                </h3>
                <p className="subtext" style={{ margin: '4px 0 0 0' }}>
                  Configure your primary business identity, domain URL, and email credentials for personalized 300 daily backlink automation.
                </p>
              </div>
            </div>

            <form onSubmit={handleSaveBrandProfile}>
              <div className="grid-2col-nested" style={{ marginBottom: '12px' }}>
                <div className="form-group">
                  <label>Brand / Business Name</label>
                  <input 
                    type="text" 
                    required 
                    value={brandProfile.brand_name}
                    onChange={(e) => setBrandProfile({...brandProfile, brand_name: e.target.value})}
                    placeholder="e.g. Fairepairs"
                  />
                </div>
                <div className="form-group">
                  <label>Primary Account Email ID</label>
                  <input 
                    type="email" 
                    required 
                    value={brandProfile.account_email}
                    onChange={(e) => setBrandProfile({...brandProfile, account_email: e.target.value})}
                    placeholder="fairpayt@gmail.com"
                  />
                </div>
              </div>

              <div className="grid-2col-nested">
                <div className="form-group">
                  <label>Website URL (Target Domain)</label>
                  <input 
                    type="url" 
                    required 
                    value={brandProfile.website_url}
                    onChange={(e) => setBrandProfile({...brandProfile, website_url: e.target.value})}
                    placeholder="https://fairepairs.com/"
                  />
                </div>
                <div className="form-group">
                  <label>Industry / Business Niche</label>
                  <input 
                    type="text" 
                    required 
                    value={brandProfile.niche_industry}
                    onChange={(e) => setBrandProfile({...brandProfile, niche_industry: e.target.value})}
                    placeholder="e.g. Auto Repairs & Services"
                  />
                </div>
              </div>

              <div className="form-group" style={{ marginTop: '10px' }}>
                <label>🎯 Primary Target Keyword(s) (For Auto-Pilot & Default Anchor Text)</label>
                <input 
                  type="text" 
                  required 
                  value={brandProfile.primary_keyword}
                  onChange={(e) => setBrandProfile({...brandProfile, primary_keyword: e.target.value})}
                  placeholder="e.g. SEO optimization guide, car repair services, engine diagnostics"
                />
                <span className="subtext" style={{ fontSize: '11px', color: '#94a3b8' }}>💡 Tip: Enter single or multiple keywords separated by commas.</span>
              </div>

              <button 
                type="submit" 
                className="btn btn-secondary btn-sm" 
                style={{ marginTop: '12px', background: '#4338ca', color: '#fff' }}
              >
                <CheckCircle2 size={14} /> Save My Personal Brand Credentials
              </button>
            </form>
          </div>
          
          {/* 24/7 Daily Auto-Pilot Scheduler Card */}
          <div className="form-card" style={{ maxWidth: '800px', margin: '0 auto', width: '100%', borderColor: schedulerConfig.is_enabled ? '#10b981aa' : 'var(--border-color)', background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(19, 27, 46, 1) 100%)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ padding: '10px', background: schedulerConfig.is_enabled ? '#064e3b' : '#1e293b', borderRadius: '12px' }}>
                  <Cpu size={26} color={schedulerConfig.is_enabled ? '#34d399' : '#94a3b8'} />
                </div>
                <div>
                  <h3 style={{ fontSize: '17px', margin: 0, color: '#fff' }}>
                    ⏰ 24/7 Agentic Auto-Pilot Scheduler (Daily 300 Backlinks Auto-Run)
                  </h3>
                  <p className="subtext" style={{ margin: '4px 0 0 0' }}>
                    Runs in the background every 24 hours to automatically generate & publish 300 daily backlinks.
                  </p>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <button 
                  className={`btn ${schedulerConfig.is_enabled ? 'btn-primary' : 'btn-secondary'}`}
                  style={{ background: schedulerConfig.is_enabled ? '#059669' : '#334155', color: '#fff' }}
                  onClick={() => handleToggleScheduler(!schedulerConfig.is_enabled)}
                >
                  {schedulerConfig.is_enabled ? '🟢 AUTO-PILOT ENABLED' : '🔴 AUTO-PILOT DISABLED'}
                </button>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px', marginTop: '16px', background: '#0f172a', padding: '12px', borderRadius: '10px' }}>
              <div>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 700 }}>LAST AUTO-RUN</span>
                <div style={{ fontSize: '13px', color: '#cbd5e1', fontWeight: 600, marginTop: '2px' }}>
                  {schedulerConfig.last_run_at || 'Completed Recently'}
                </div>
              </div>
              <div>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 700 }}>NEXT AUTO-RUN</span>
                <div style={{ fontSize: '13px', color: '#38bdf8', fontWeight: 600, marginTop: '2px' }}>
                  {schedulerConfig.next_run_at || 'In 24 Hours'}
                </div>
              </div>
              <div style={{ alignSelf: 'center', textAlign: 'right' }}>
                <button 
                  className="btn btn-secondary btn-sm"
                  onClick={handleTriggerScheduleNow}
                >
                  <Play size={12} /> Trigger Daily Run Now
                </button>
              </div>
            </div>
          </div>

          {/* 1-Click Execution Card */}
          <div className="form-card highlight-card" style={{ maxWidth: '800px', margin: '0 auto', width: '100%' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ padding: '10px', background: '#312e81', borderRadius: '12px' }}>
                <Bot size={28} color="#a5b4fc" />
              </div>
              <div>
                <h3 style={{ fontSize: '18px', margin: 0 }}>Instant 1-Click Backlink Bot Launcher</h3>
                <p className="subtext" style={{ margin: 0 }}>Instantly triggers an on-demand backlink generation & submission campaign.</p>
              </div>
            </div>

            <form onSubmit={handleRunAutoAgent}>
              <div className="form-group">
                <label>Target Website URL (Your Website)</label>
                <input 
                  type="url" 
                  required 
                  value={autoForm.target_url}
                  onChange={(e) => setAutoForm({...autoForm, target_url: e.target.value})}
                  placeholder="https://mywebsite.com/seo-guide"
                />
              </div>

              <div className="grid-2col-nested">
                <div className="form-group">
                  <label>Account / Author Email ID</label>
                  <input 
                    type="email" 
                    required 
                    value={autoForm.author_email}
                    onChange={(e) => setAutoForm({...autoForm, author_email: e.target.value})}
                    placeholder="fairpayt@gmail.com"
                  />
                </div>
                <div className="form-group">
                  <label>Target Keywords (Single or Comma-Separated)</label>
                  <input 
                    type="text" 
                    required 
                    value={autoForm.target_keyword}
                    onChange={(e) => setAutoForm({...autoForm, target_keyword: e.target.value})}
                    placeholder="e.g. SEO optimization guide, car repair services, engine diagnostics"
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Backlinks Batch Count</label>
                <select 
                  value={autoForm.count}
                  onChange={(e) => setAutoForm({...autoForm, count: parseInt(e.target.value)})}
                >
                  <option value={50}>50 Automated Backlinks</option>
                  <option value={100}>100 Automated Backlinks</option>
                  <option value={300}>300 Automated Backlinks (Full Daily Goal)</option>
                </select>
              </div>

              <button 
                type="submit" 
                className="btn btn-amber btn-block" 
                disabled={autoRunning}
                style={{ padding: '14px', fontSize: '15px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
              >
                {autoRunning ? <RefreshCw className="spin" size={18} /> : <Play size={18} />}
                {autoRunning ? 'Agent Generating & Submitting Backlinks...' : '⚡ LAUNCH AUTONOMOUS BACKLINK BOT ENGINE'}
              </button>
            </form>

            {/* Execution Result Banner */}
            {autoResult && (
              <div style={{ marginTop: '24px', background: '#0f172a', border: '1px solid #10b98166', borderRadius: '12px', padding: '20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', color: '#34d399', fontWeight: 700 }}>
                  <CheckCircle2 size={20} />
                  <span>Automation Campaign Completed Successfully!</span>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px', marginBottom: '16px' }}>
                  <div style={{ background: '#1e293b', padding: '10px', borderRadius: '8px', textAlign: 'center' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Created Links</div>
                    <div style={{ fontSize: '20px', fontWeight: 800, color: '#38bdf8' }}>{autoResult.total_created}</div>
                  </div>
                  <div style={{ background: '#1e293b', padding: '10px', borderRadius: '8px', textAlign: 'center' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Real Telegra.ph Live</div>
                    <div style={{ fontSize: '20px', fontWeight: 800, color: '#34d399' }}>{autoResult.real_live_published}</div>
                  </div>
                  <div style={{ background: '#1e293b', padding: '10px', borderRadius: '8px', textAlign: 'center' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Daily Goal Progress</div>
                    <div style={{ fontSize: '20px', fontWeight: 800, color: '#fbbf24' }}>{stats.goal_percentage}%</div>
                  </div>
                </div>

                <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '8px' }}>
                  Sample Live Published Backlink URLs:
                </div>
                <ul style={{ fontSize: '12px', listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {autoResult.items.map((item, idx) => (
                    <li key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: '#1e293b', padding: '6px 12px', borderRadius: '6px' }}>
                      <a href={item.submitted_url} target="_blank" rel="noopener noreferrer" style={{ color: '#38bdf8', textDecoration: 'none' }}>
                        {item.submitted_url} <ExternalLink size={11} />
                      </a>
                      <span className="badge-pass" style={{ fontSize: '10px' }}>DA {item.da} {item.category}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 1: BACKLINK VAULT & LIVE VERIFIER */}
      {activeTab === 'vault' && (
        <div className="vault-container">
          <div className="controls-bar">
            <div className="search-box">
              <Search size={16} className="search-icon" />
              <input 
                type="text"
                placeholder="Search target URL..."
                value={searchFilter}
                onChange={(e) => setSearchFilter(e.target.value)}
              />
            </div>

            <div className="filters-group">
              <select value={dateFilter} onChange={(e) => setDateFilter(e.target.value)}>
                <option value="all">All Time</option>
                <option value="today">Today's Links</option>
                <option value="yesterday">Yesterday</option>
                <option value="this_week">This Week</option>
              </select>

              <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
                <option value="all">All Categories</option>
                <option value="Web 2.0">Web 2.0</option>
                <option value="Directory">Directory</option>
                <option value="Social Bookmarking">Social Bookmarking</option>
                <option value="Guest Post">Guest Post</option>
                <option value="Profile">Profile</option>
                <option value="Forum">Forum</option>
              </select>

              <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="verified">Verified Live</option>
                <option value="rejected">Rejected / Missing</option>
              </select>

              <button 
                className="btn btn-secondary"
                onClick={handleBatchVerify}
                disabled={batchVerifying}
              >
                <RefreshCw size={14} className={batchVerifying ? 'spin' : ''} /> 
                {batchVerifying ? 'Verifying...' : 'Verify Pending Batch'}
              </button>
            </div>
          </div>

          {/* Table */}
          <div className="table-responsive">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Submitted Page URL & Domain</th>
                  <th>Target URL & Anchor Link</th>
                  <th>Author Persona & Email ID</th>
                  <th>Category</th>
                  <th>DA</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {backlinks.length === 0 ? (
                  <tr>
                    <td colSpan="8" style={{ textAlign: 'center', padding: '2rem' }}>
                      No backlink records found. Click <strong>"⚡ Auto-Agent Submitter"</strong> or <strong>"Manual / Bulk Paste Links"</strong> to add entries.
                    </td>
                  </tr>
                ) : (
                  backlinks.map((item) => (
                    <tr key={item.id}>
                      <td>
                        <div className="font-semibold">{item.domain}</div>
                        <a 
                          href={item.submitted_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="link-sub"
                        >
                          {item.submitted_url.length > 38 ? item.submitted_url.substring(0, 38) + '...' : item.submitted_url}
                          <ExternalLink size={11} />
                        </a>
                      </td>
                      <td>
                        <a 
                          href={item.target_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="link-target"
                        >
                          {item.target_url.length > 25 ? item.target_url.substring(0, 25) + '...' : item.target_url}
                        </a>
                        <div style={{ marginTop: '2px' }}><code style={{ color: '#6ee7b7', fontSize: '11px' }}>Anchor: {item.anchor_text || '-'}</code></div>
                      </td>
                      <td>
                        <div style={{ fontWeight: 600, color: '#e2e8f0', fontSize: '12px' }}>{item.author_name || 'Author'}</div>
                        <div style={{ fontSize: '11px', color: '#94a3b8' }}>✉️ {item.author_email || 'contact@domain.com'}</div>
                      </td>
                      <td><span className="category-pill">{item.submission_category}</span></td>
                      <td><span className="da-badge">DA {item.da_score}</span></td>
                      <td>
                        <span className={`type-badge ${item.link_type}`}>
                          {item.link_type}
                        </span>
                      </td>
                      <td>
                        <span className={`status-badge ${item.status}`}>
                          {item.status === 'verified' && <Check size={12} />}
                          {item.status}
                        </span>
                      </td>
                      <td>
                        <div className="action-buttons">
                          <button 
                            className="btn-icon" 
                            title="Verify live link"
                            onClick={() => handleVerify(item.id)}
                            disabled={verifyingId === item.id}
                          >
                            <RefreshCw size={14} className={verifyingId === item.id ? 'spin' : ''} />
                          </button>
                          <button 
                            className="btn-icon text-danger" 
                            title="Delete"
                            onClick={() => handleDelete(item.id)}
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 2: SUBMIT / BULK ADD LINKS */}
      {activeTab === 'add' && (
        <div className="add-container">
          <div className="grid-2col">
            {/* Single Submission Form */}
            <div className="form-card">
              <h3><PlusCircle size={18} /> Log Single Backlink</h3>
              <form onSubmit={handleSingleSubmit}>
                <div className="form-group">
                  <label>Target Website URL (Your Site)</label>
                  <input 
                    type="url" 
                    required 
                    value={singleForm.target_url}
                    onChange={(e) => setSingleForm({...singleForm, target_url: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Submitted Backlink Page URL</label>
                  <input 
                    type="url" 
                    required 
                    placeholder="https://medium.com/@user/my-post"
                    value={singleForm.submitted_url}
                    onChange={(e) => setSingleForm({...singleForm, submitted_url: e.target.value})}
                  />
                </div>
                <div className="grid-2col-nested">
                  <div className="form-group">
                    <label>Anchor Text Used</label>
                    <input 
                      type="text" 
                      placeholder="e.g. SEO services"
                      value={singleForm.anchor_text}
                      onChange={(e) => setSingleForm({...singleForm, anchor_text: e.target.value})}
                    />
                  </div>
                  <div className="form-group">
                    <label>Link Type</label>
                    <select 
                      value={singleForm.link_type}
                      onChange={(e) => setSingleForm({...singleForm, link_type: e.target.value})}
                    >
                      <option value="dofollow">Dofollow</option>
                      <option value="nofollow">Nofollow</option>
                      <option value="ugc">UGC</option>
                      <option value="sponsored">Sponsored</option>
                    </select>
                  </div>
                </div>
                <div className="grid-2col-nested">
                  <div className="form-group">
                    <label>Category</label>
                    <select 
                      value={singleForm.submission_category}
                      onChange={(e) => setSingleForm({...singleForm, submission_category: e.target.value})}
                    >
                      <option value="Web 2.0">Web 2.0</option>
                      <option value="Directory">Directory</option>
                      <option value="Social Bookmarking">Social Bookmarking</option>
                      <option value="Guest Post">Guest Post</option>
                      <option value="Profile">Profile</option>
                      <option value="Forum">Forum</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Estimated DA Score</label>
                    <input 
                      type="number" 
                      min="1" 
                      max="100" 
                      value={singleForm.da_score}
                      onChange={(e) => setSingleForm({...singleForm, da_score: parseInt(e.target.value) || 0})}
                    />
                  </div>
                </div>
                <button type="submit" className="btn btn-primary btn-block">Log Backlink</button>
              </form>
            </div>

            {/* Bulk Submission Form */}
            <div className="form-card highlight-card">
              <h3><Zap size={18} /> Bulk Backlink Importer (Daily Target)</h3>
              <p className="subtext">Paste up to 300 submitted URLs at once (one URL per line) to rapidly log submission tasks.</p>
              <form onSubmit={handleBulkSubmit}>
                <div className="form-group">
                  <label>Target Website URL (Your Site)</label>
                  <input 
                    type="url" 
                    required 
                    value={bulkForm.target_url}
                    onChange={(e) => setBulkForm({...bulkForm, target_url: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Submitted URLs (Paste newline-separated URLs)</label>
                  <textarea 
                    rows={6}
                    required
                    placeholder="https://site1.com/post-1&#10;https://site2.org/profile&#10;https://site3.net/bookmark"
                    value={bulkForm.urls_raw}
                    onChange={(e) => setBulkForm({...bulkForm, urls_raw: e.target.value})}
                  />
                </div>
                <div className="grid-2col-nested">
                  <div className="form-group">
                    <label>Default Category</label>
                    <select 
                      value={bulkForm.submission_category}
                      onChange={(e) => setBulkForm({...bulkForm, submission_category: e.target.value})}
                    >
                      <option value="Web 2.0">Web 2.0</option>
                      <option value="Directory">Directory</option>
                      <option value="Social Bookmarking">Social Bookmarking</option>
                      <option value="Profile">Profile</option>
                      <option value="Guest Post">Guest Post</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Default Anchor Text</label>
                    <input 
                      type="text" 
                      placeholder="e.g. Target Keyword"
                      value={bulkForm.anchor_text}
                      onChange={(e) => setBulkForm({...bulkForm, anchor_text: e.target.value})}
                    />
                  </div>
                </div>
                <button type="submit" className="btn btn-amber btn-block">Bulk Import Backlinks</button>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: HIGH DA TARGET PLATFORMS */}
      {activeTab === 'targets' && (
        <div className="targets-container">
          <div className="targets-header">
            <h3><Globe size={18} /> High Authority Backlink Submission Directory</h3>
            <p>Curated list of High DA platform sites for manual outreach, Web 2.0 blogs, business listings, and bookmarking.</p>
          </div>
          <div className="targets-grid">
            {highDaTargets.map((target, idx) => (
              <div key={idx} className="target-card">
                <div className="target-top">
                  <span className="target-name">{target.name}</span>
                  <span className="da-pill">DA {target.da}</span>
                </div>
                <div className="target-meta">
                  <span className="category-pill">{target.category}</span>
                  <span className={`type-badge ${target.link_type}`}>{target.link_type}</span>
                </div>
                <p className="target-notes">{target.notes}</p>
                <a 
                  href={target.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="btn btn-secondary btn-sm target-link-btn"
                >
                  Visit Platform <ExternalLink size={12} />
                </a>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 4: DAILY CLIENT REPORTS */}
      {activeTab === 'reports' && (
        <div className="reports-container">
          <div className="report-card">
            <h3><FileSpreadsheet size={20} /> Generate & Export Daily Activity Report</h3>
            <p>Download structured client submission reports for daily SEO backlink audits.</p>
            
            <div className="report-controls">
              <div className="form-group" style={{ maxWidth: '300px' }}>
                <label>Select Work Date</label>
                <input 
                  type="date" 
                  value={reportDate}
                  onChange={(e) => setReportDate(e.target.value)}
                />
              </div>

              <div className="report-actions" style={{ flexWrap: 'wrap', gap: '12px' }}>
                <button 
                  className="btn btn-primary"
                  onClick={() => downloadReport('csv')}
                >
                  <FileSpreadsheet size={16} /> Export CSV Report
                </button>
                <button 
                  className="btn btn-secondary"
                  onClick={() => downloadReport('markdown')}
                >
                  <FileText size={16} /> Export Markdown Summary
                </button>
                <button 
                  className="btn btn-amber"
                  onClick={handlePingIndexer}
                  disabled={pinging}
                  style={{ background: '#d97706', color: '#fff' }}
                >
                  <Zap size={16} className={pinging ? 'spin' : ''} /> 
                  {pinging ? 'Submitting to Google Indexer...' : '⚡ Submit All Links to Google Indexer (1-Click)'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
