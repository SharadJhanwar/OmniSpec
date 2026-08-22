// Resolves the backend API base URL from build environment, runtime window config, or auto-detects Render deployment
const isRender = typeof window !== 'undefined' && window.location.hostname.includes('onrender.com');
const defaultRenderBackend = 'https://omnispec-backend-latest.onrender.com';

export const API_BASE_URL = 
  (typeof window !== 'undefined' && window.__ENV__?.VITE_API_BASE_URL) ||
  import.meta.env.VITE_API_BASE_URL ||
  (isRender ? defaultRenderBackend : '');

export function apiUrl(endpoint) {
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${API_BASE_URL}${cleanEndpoint}`;
}
