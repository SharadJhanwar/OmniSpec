// Resolves the backend API base URL from environment or defaults to relative path
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export function apiUrl(endpoint) {
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${API_BASE_URL}${cleanEndpoint}`;
}
