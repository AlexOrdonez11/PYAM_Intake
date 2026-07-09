async function api(path, options = {}) {
  const apiBase = window.PYAM_API_BASE_URL || "";
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (state.authToken) headers.Authorization = `Bearer ${state.authToken}`;

  const response = await fetch(`${apiBase}${path}`, {
    headers,
    ...options
  });
  const payload = await response.json();
  if (!response.ok) {
    const detail = payload.detail || {};
    const error = new Error(payload.error || detail.error || (typeof detail === "string" ? detail : "Request failed"));
    error.details = payload.details || detail.details || [];
    throw error;
  }
  return payload;
}

