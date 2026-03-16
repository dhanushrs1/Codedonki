// This is the helper script from our plan (Phase 3)
// We will use it in Phase 5 and beyond.

const API_BASE_URL = 'http://127.0.0.1:5000';

/**
 * A wrapper for the native fetch function that automatically adds
 * the JWT token to the Authorization header.
 * @param {string} endpoint The API endpoint (e.g., '/api/profile')
 * @param {RequestInit} options The options for the fetch request
 * @returns {Promise<Response>} The fetch response
 */
async function apiFetch(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  
  // Create default headers if they don't exist
  if (!options.headers) {
    options.headers = {};
  }

  // Add the Authorization token if we have one
  if (token) {
    options.headers['Authorization'] = `Bearer ${token}`;
  }
  
  // Handle file uploads (FormData)
  // We must NOT set Content-Type for FormData,
  // the browser does it automatically with the correct boundary.
  if (!(options.body instanceof FormData)) {
     // For regular JSON, set the Content-Type
    options.headers['Content-Type'] = 'application/json';
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

    // Handle token expiration or invalid token
    if (response.status === 401 || response.status === 422) {
      // 401 Unauthorized or 422 Unprocessable Entity (common for expired/invalid JWT)
      console.error('Authentication error. Logging out.');
      localStorage.removeItem('token');
      localStorage.removeItem('userName');
      // Don't automatically redirect - let the calling function handle it
      // This allows for better error handling in admin pages
    }
    
    return response;
    
  } catch (error) {
    console.error('API Fetch Error:', error);
    throw error;
  }
}