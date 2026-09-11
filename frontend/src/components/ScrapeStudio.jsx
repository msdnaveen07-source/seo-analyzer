import React, { useState } from 'react';
import { 
  FileText, Cpu, Compass, Activity, Copy, Download, Check, Sparkles, RefreshCw, Search, Key
} from 'lucide-react';
import { apiFetch } from '../api';

export default function ScrapeStudio() {
  const [activeTab, setActiveTab] = useState('markdown'); // 'markdown' | 'extract' | 'search' | 'crawl' | 'monitor'
  const [sgaiApiKey, setSgaiApiKey] = useState('');

  // 1. Markdown
  const [mdUrl, setMdUrl] = useState('https://docs.example.com/getting-started');
  const [mdLoading, setMdLoading] = useState(false);
  const [mdResult, setMdResult] = useState(null);
  const [mdCopied, setMdCopied] = useState(false);

  // 2. Extract
  const [extUrl, setExtUrl] = useState('https://news.ycombinator.com');
  const [extPrompt, setExtPrompt] = useState('Extract the top 3 stories with title, points, and author');
  const [extLoading, setExtLoading] = useState(false);
  const [extResult, setExtResult] = useState(null);
  const [extCopied, setExtCopied] = useState(false);

  // 3. Search
  const [srchQuery, setSrchQuery] = useState('sustainable packaging trends 2026');
  const [srchPrompt, setSrchPrompt] = useState('Extract top trends with market size');
  const [srchNum, setSrchNum] = useState(3);
  const [srchGeo, setSrchGeo] = useState('us');
  const [srchLoading, setSrchLoading] = useState(false);
  const [srchResult, setSrchResult] = useState(null);

  // 4. Crawl
  const [crawlUrl, setCrawlUrl] = useState('https://docs.example.com');
  const [crawlLoading, setCrawlLoading] = useState(false);
  const [crawlResult, setCrawlResult] = useState(null);

  // 5. Monitor
  const [monUrl, setMonUrl] = useState('https://example-shop.com/product');
  const [monInterval, setMonInterval] = useState('0 */6 * * *');
  const [monWebhook, setMonWebhook] = useState('https://your-app.com/webhook');
  const [monLoading, setMonLoading] = useState(false);
  const [monResult, setMonResult] = useState(null);

  // Handlers
  const handleMarkdown = async (e) => {
    e.preventDefault();
    setMdLoading(true);
    setMdResult(null);
    try {
      const { ok, data } = await apiFetch('/api/scrape/markdown', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: mdUrl.trim(), sgai_api_key: sgaiApiKey.trim() || undefined })
      });
      if (ok && data.success) setMdResult(data);
      else alert(`Failed: ${data.detail || data.error || 'Conversion error'}`);
    } catch (err) { alert(`Error: ${err.message}`); }
    finally { setMdLoading(false); }
  };

  const handleExtract = async (e) => {
    e.preventDefault();
    setExtLoading(true);
    setExtResult(null);
    try {
      const { ok, data } = await apiFetch('/api/scrape/extract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: extUrl.trim(), prompt: extPrompt.trim(), sgai_api_key: sgaiApiKey.trim() || undefined })
      });
      if (ok && data.success) setExtResult(data);
      else alert(`Failed: ${data.detail || data.error || 'Extraction error'}`);
    } catch (err) { alert(`Error: ${err.message}`); }
    finally { setExtLoading(false); }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setSrchLoading(true);
    setSrchResult(null);
    try {
      const { ok, data } = await apiFetch('/api/scrape/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: srchQuery.trim(),
          prompt: srchPrompt.trim(),
          num_results: parseInt(srchNum, 10),
          location_geocode: srchGeo,
          sgai_api_key: sgaiApiKey.trim() || undefined
        })
      });
      if (ok && data.success) setSrchResult(data);
      else alert(`Search failed: ${data.detail || data.error || 'Check SGAI-APIKEY'}`);
    } catch (err) { alert(`Error: ${err.message}`); }
    finally { setSrchLoading(false); }
  };

  const handleCrawl = async (e) => {
    e.preventDefault();
    setCrawlLoading(true);
    setCrawlResult(null);
    try {
      const { ok, data } = await apiFetch('/api/scrape/crawl', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: crawlUrl.trim(), sgai_api_key: sgaiApiKey.trim() || undefined })
      });
      if (ok && data.success) setCrawlResult(data);
      else alert(`Crawl failed: ${data.detail || data.error || 'Crawl error'}`);
    } catch (err) { alert(`Error: ${err.message}`); }
    finally { setCrawlLoading(false); }
  };

  const handleMonitor = async (e) => {
    e.preventDefault();
    setMonLoading(true);
    setMonResult(null);
    try {
      const { ok, data } = await apiFetch('/api/scrape/monitor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: monUrl.trim(),
          interval: monInterval.trim(),
          webhook_url: monWebhook.trim() || undefined,
          sgai_api_key: sgaiApiKey.trim() || undefined
        })
      });
      if (ok && data.success) setMonResult(data);
      else alert(`Monitor failed: ${data.detail || data.error || 'Monitor error'}`);
    } catch (err) { alert(`Error: ${err.message}`); }
    finally { setMonLoading(false); }
  };

  const copyToClipboard = (text, setCopiedFn) => {
    navigator.clipboard.writeText(text);
    setCopiedFn(true);
    setTimeout(() => setCopiedFn(false), 2000);
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '24px' }}>
      {/* Top Header & Optional API Key input */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: '700', color: '#f3f4f6', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Sparkles style={{ color: '#8b5cf6' }} /> ScrapeGraphAI v2 Suite
          </h1>
          <p style={{ color: '#9ca3af', fontSize: '14px', marginTop: '4px' }}>
            Official ScrapeGraphAI v2 REST API integration (Scrape, Extract, Search, Crawl & Monitor).
          </p>
        </div>

        {/* SGAI API Key input */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: '#1f2937', padding: '8px 14px', borderRadius: '8px', border: '1px solid #374151' }}>
          <Key size={16} color="#8b5cf6" />
          <input
            type="password"
            placeholder="SGAI-APIKEY (Optional)"
            value={sgaiApiKey}
            onChange={(e) => setSgaiApiKey(e.target.value)}
            style={{ border: 'none', background: 'transparent', color: '#f3f4f6', fontSize: '13px', outline: 'none', width: '180px' }}
          />
        </div>
      </div>

      {/* Navigation Tabs */}
      <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid #374151', paddingBottom: '12px', marginBottom: '24px', overflowX: 'auto' }}>
        <button onClick={() => setActiveTab('markdown')} style={{ padding: '10px 16px', borderRadius: '8px', border: 'none', cursor: 'pointer', backgroundColor: activeTab === 'markdown' ? '#8b5cf6' : '#1f2937', color: activeTab === 'markdown' ? '#fff' : '#9ca3af', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <FileText size={16} /> Scrape to Markdown
        </button>
        <button onClick={() => setActiveTab('extract')} style={{ padding: '10px 16px', borderRadius: '8px', border: 'none', cursor: 'pointer', backgroundColor: activeTab === 'extract' ? '#8b5cf6' : '#1f2937', color: activeTab === 'extract' ? '#fff' : '#9ca3af', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Cpu size={16} /> Extract Structured JSON
        </button>
        <button onClick={() => setActiveTab('search')} style={{ padding: '10px 16px', borderRadius: '8px', border: 'none', cursor: 'pointer', backgroundColor: activeTab === 'search' ? '#8b5cf6' : '#1f2937', color: activeTab === 'search' ? '#fff' : '#9ca3af', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Search size={16} /> Search & Extract Trends
        </button>
        <button onClick={() => setActiveTab('crawl')} style={{ padding: '10px 16px', borderRadius: '8px', border: 'none', cursor: 'pointer', backgroundColor: activeTab === 'crawl' ? '#8b5cf6' : '#1f2937', color: activeTab === 'crawl' ? '#fff' : '#9ca3af', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Compass size={16} /> Crawl Site
        </button>
        <button onClick={() => setActiveTab('monitor')} style={{ padding: '10px 16px', borderRadius: '8px', border: 'none', cursor: 'pointer', backgroundColor: activeTab === 'monitor' ? '#8b5cf6' : '#1f2937', color: activeTab === 'monitor' ? '#fff' : '#9ca3af', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Activity size={16} /> Monitor & Webhooks
        </button>
      </div>

      {/* 1. Markdown */}
      {activeTab === 'markdown' && (
        <div style={{ backgroundColor: '#111827', borderRadius: '12px', padding: '24px', border: '1px solid #1f2937' }}>
          <h2 style={{ fontSize: '18px', color: '#f3f4f6', marginBottom: '16px', fontWeight: '600' }}>Convert Webpage to Clean Markdown</h2>
          <form onSubmit={handleMarkdown} style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
            <input type="url" value={mdUrl} onChange={(e) => setMdUrl(e.target.value)} required style={{ flex: 1, padding: '12px 16px', borderRadius: '8px', border: '1px solid #374151', backgroundColor: '#1f2937', color: '#f3f4f6' }} />
            <button type="submit" disabled={mdLoading} style={{ padding: '12px 24px', backgroundColor: '#8b5cf6', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: '600', cursor: mdLoading ? 'not-allowed' : 'pointer' }}>
              {mdLoading ? <RefreshCw className="animate-spin" size={16} /> : <FileText size={16} />} {mdLoading ? 'Scraping...' : 'Scrape Markdown'}
            </button>
          </form>
          {mdResult && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px', color: '#9ca3af', fontSize: '13px' }}>
                <span>Engine: <strong style={{ color: '#8b5cf6' }}>{mdResult.engine}</strong></span>
                <button onClick={() => copyToClipboard(mdResult.markdown, setMdCopied)} style={{ padding: '6px 12px', backgroundColor: '#374151', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
                  {mdCopied ? 'Copied!' : 'Copy Markdown'}
                </button>
              </div>
              <textarea readOnly value={mdResult.markdown} rows={14} style={{ width: '100%', padding: '16px', backgroundColor: '#030712', color: '#e5e7eb', fontFamily: 'monospace', fontSize: '13px', borderRadius: '8px', border: '1px solid #374151' }} />
            </div>
          )}
        </div>
      )}

      {/* 2. Extract */}
      {activeTab === 'extract' && (
        <div style={{ backgroundColor: '#111827', borderRadius: '12px', padding: '24px', border: '1px solid #1f2937' }}>
          <h2 style={{ fontSize: '18px', color: '#f3f4f6', marginBottom: '16px', fontWeight: '600' }}>Extract Structured Data via Natural Language Prompt</h2>
          <form onSubmit={handleExtract} style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '24px' }}>
            <input type="url" value={extUrl} onChange={(e) => setExtUrl(e.target.value)} required placeholder="Target URL" style={{ padding: '12px 16px', borderRadius: '8px', border: '1px solid #374151', backgroundColor: '#1f2937', color: '#f3f4f6' }} />
            <input type="text" value={extPrompt} onChange={(e) => setExtPrompt(e.target.value)} required placeholder="Prompt (e.g. Extract top 3 stories)" style={{ padding: '12px 16px', borderRadius: '8px', border: '1px solid #374151', backgroundColor: '#1f2937', color: '#f3f4f6' }} />
            <button type="submit" disabled={extLoading} style={{ alignSelf: 'flex-start', padding: '12px 24px', backgroundColor: '#8b5cf6', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: '600', cursor: extLoading ? 'not-allowed' : 'pointer' }}>
              {extLoading ? 'Extracting...' : 'Extract Data'}
            </button>
          </form>
          {extResult && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', color: '#9ca3af', fontSize: '13px' }}>
                <span>Engine: <strong style={{ color: '#8b5cf6' }}>{extResult.engine}</strong></span>
                <button onClick={() => copyToClipboard(JSON.stringify(extResult.data, null, 2), setExtCopied)} style={{ padding: '6px 12px', backgroundColor: '#374151', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
                  {extCopied ? 'Copied!' : 'Copy JSON'}
                </button>
              </div>
              <textarea readOnly value={JSON.stringify(extResult.data, null, 2)} rows={14} style={{ width: '100%', padding: '16px', backgroundColor: '#030712', color: '#38bdf8', fontFamily: 'monospace', fontSize: '13px', borderRadius: '8px', border: '1px solid #374151' }} />
            </div>
          )}
        </div>
      )}

      {/* 3. Search */}
      {activeTab === 'search' && (
        <div style={{ backgroundColor: '#111827', borderRadius: '12px', padding: '24px', border: '1px solid #1f2937' }}>
          <h2 style={{ fontSize: '18px', color: '#f3f4f6', marginBottom: '16px', fontWeight: '600' }}>Search Web & Extract Trends (v2 Search API)</h2>
          <form onSubmit={handleSearch} style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '24px' }}>
            <input type="text" value={srchQuery} onChange={(e) => setSrchQuery(e.target.value)} required placeholder="Search Query (e.g. sustainable packaging trends 2026)" style={{ padding: '12px 16px', borderRadius: '8px', border: '1px solid #374151', backgroundColor: '#1f2937', color: '#f3f4f6' }} />
            <input type="text" value={srchPrompt} onChange={(e) => setSrchPrompt(e.target.value)} placeholder="Prompt (e.g. Extract top trends with market size)" style={{ padding: '12px 16px', borderRadius: '8px', border: '1px solid #374151', backgroundColor: '#1f2937', color: '#f3f4f6' }} />
            <div style={{ display: 'flex', gap: '12px' }}>
              <input type="number" value={srchNum} onChange={(e) => setSrchNum(e.target.value)} min={1} max={10} style={{ width: '120px', padding: '12px', borderRadius: '8px', border: '1px solid #374151', backgroundColor: '#1f2937', color: '#f3f4f6' }} />
              <input type="text" value={srchGeo} onChange={(e) => setSrchGeo(e.target.value)} placeholder="Geo (us, uk, in)" style={{ width: '120px', padding: '12px', borderRadius: '8px', border: '1px solid #374151', backgroundColor: '#1f2937', color: '#f3f4f6' }} />
            </div>
            <button type="submit" disabled={srchLoading} style={{ alignSelf: 'flex-start', padding: '12px 24px', backgroundColor: '#8b5cf6', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: '600' }}>
              {srchLoading ? 'Searching...' : 'Search & Extract'}
            </button>
          </form>
          {srchResult && (
            <textarea readOnly value={JSON.stringify(srchResult.data, null, 2)} rows={14} style={{ width: '100%', padding: '16px', backgroundColor: '#030712', color: '#10b981', fontFamily: 'monospace', fontSize: '13px', borderRadius: '8px', border: '1px solid #374151' }} />
          )}
        </div>
      )}

      {/* 4. Crawl */}
      {activeTab === 'crawl' && (
        <div style={{ backgroundColor: '#111827', borderRadius: '12px', padding: '24px', border: '1px solid #1f2937' }}>
          <h2 style={{ fontSize: '18px', color: '#f3f4f6', marginBottom: '16px', fontWeight: '600' }}>Crawl Website (v2 Crawl API)</h2>
          <form onSubmit={handleCrawl} style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
            <input type="url" value={crawlUrl} onChange={(e) => setCrawlUrl(e.target.value)} required style={{ flex: 1, padding: '12px 16px', borderRadius: '8px', border: '1px solid #374151', backgroundColor: '#1f2937', color: '#f3f4f6' }} />
            <button type="submit" disabled={crawlLoading} style={{ padding: '12px 24px', backgroundColor: '#8b5cf6', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: '600' }}>
              {crawlLoading ? 'Crawling...' : 'Crawl Site'}
            </button>
          </form>
          {crawlResult && (
            <textarea readOnly value={JSON.stringify(crawlResult.data || crawlResult.pages, null, 2)} rows={14} style={{ width: '100%', padding: '16px', backgroundColor: '#030712', color: '#e5e7eb', fontFamily: 'monospace', fontSize: '13px', borderRadius: '8px', border: '1px solid #374151' }} />
          )}
        </div>
      )}

      {/* 5. Monitor */}
      {activeTab === 'monitor' && (
        <div style={{ backgroundColor: '#111827', borderRadius: '12px', padding: '24px', border: '1px solid #1f2937' }}>
          <h2 style={{ fontSize: '18px', color: '#f3f4f6', marginBottom: '16px', fontWeight: '600' }}>Monitor Webpage & Webhook Setup (v2 Monitor API)</h2>
          <form onSubmit={handleMonitor} style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '24px' }}>
            <input type="url" value={monUrl} onChange={(e) => setMonUrl(e.target.value)} required placeholder="URL to monitor" style={{ padding: '12px 16px', borderRadius: '8px', border: '1px solid #374151', backgroundColor: '#1f2937', color: '#f3f4f6' }} />
            <input type="text" value={monInterval} onChange={(e) => setMonInterval(e.target.value)} placeholder="Interval (cron format: 0 */6 * * *)" style={{ padding: '12px 16px', borderRadius: '8px', border: '1px solid #374151', backgroundColor: '#1f2937', color: '#f3f4f6' }} />
            <input type="url" value={monWebhook} onChange={(e) => setMonWebhook(e.target.value)} placeholder="Webhook URL (https://your-app.com/webhook)" style={{ padding: '12px 16px', borderRadius: '8px', border: '1px solid #374151', backgroundColor: '#1f2937', color: '#f3f4f6' }} />
            <button type="submit" disabled={monLoading} style={{ alignSelf: 'flex-start', padding: '12px 24px', backgroundColor: '#8b5cf6', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: '600' }}>
              {monLoading ? 'Setting up...' : 'Setup Monitor & Webhook'}
            </button>
          </form>
          {monResult && (
            <textarea readOnly value={JSON.stringify(monResult.data || monResult, null, 2)} rows={14} style={{ width: '100%', padding: '16px', backgroundColor: '#030712', color: '#8b5cf6', fontFamily: 'monospace', fontSize: '13px', borderRadius: '8px', border: '1px solid #374151' }} />
          )}
        </div>
      )}
    </div>
  );
}
