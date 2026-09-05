// Centralized API configuration and fetch wrapper

export const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'https://seo-analyzer-v4pu.onrender.com').replace(/\/+$/, '');

export async function apiFetch(endpoint, options = {}) {
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${cleanEndpoint}`;
  
  let res;
  try {
    res = await fetch(url, options);
  } catch (err) {
    throw new Error(`Network Connection Failed: Cannot reach backend server at ${url}. ${err.message}`);
  }

  const contentType = res.headers.get('content-type') || '';
  const rawText = await res.text();

  if (contentType.includes('text/html') || rawText.trim().startsWith('<!DOCTYPE') || rawText.trim().startsWith('<html')) {
    throw new Error(
      `Backend API Error (HTTP ${res.status}): The server returned an HTML webpage instead of a JSON API response. ` +
      `Ensure your FastAPI backend server is running and VITE_API_BASE_URL is properly configured.`
    );
  }

  let data = {};
  if (rawText) {
    try {
      data = JSON.parse(rawText);
    } catch (e) {
      throw new Error(`Invalid JSON response from server (HTTP ${res.status}): ${rawText.substring(0, 150)}`);
    }
  }

  return { ok: res.ok, status: res.status, data };
}
