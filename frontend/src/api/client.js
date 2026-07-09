const API_BASE_URL = window.PYAM_API_BASE_URL || "";

export function getStoredToken() {
  return localStorage.getItem("pyam.authToken") || "";
}

export function storeToken(token) {
  if (token) {
    localStorage.setItem("pyam.authToken", token);
  } else {
    localStorage.removeItem("pyam.authToken");
  }
}

export async function api(path, options = {}, token = getStoredToken()) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };

  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers
  });

  const text = await response.text();
  const payload = text ? JSON.parse(text) : {};

  if (!response.ok) {
    const detail = payload.detail || payload.error || "Request failed.";
    const message = typeof detail === "string" ? detail : detail.error || "Request failed.";
    const error = new Error(message);
    error.details = detail.details || [];
    throw error;
  }

  return payload;
}
