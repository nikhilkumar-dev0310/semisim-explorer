/**
 * SemiSim Global API Configuration
 * Defines the backend host for local development or remote Render deployment.
 */
const API_CONFIG = {
  // Use Render URL in production or fallback to localhost for development
  BASE_URL: (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://localhost:8000'
    : 'https://semisim-backend.onrender.com', // Replace with your Render URL if hosted
  TIMEOUT_MS: 30000
};

// Utility to perform resilient POST requests with timeout
async function apiPost(endpoint, body) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT_MS);
  try {
    const res = await fetch(`${API_CONFIG.BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
    return await res.json();
  } catch (err) {
    clearTimeout(timeoutId);
    console.warn(`[SemiSim API] Request to ${endpoint} failed:`, err);
    throw err;
  }
}
