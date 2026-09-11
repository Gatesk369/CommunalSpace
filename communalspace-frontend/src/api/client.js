const BASE_URL = import.meta.env.VITE_API_URL;

async function refreshAccessToken() {
  const refreshToken = localStorage.getItem("refresh");

  if (!refreshToken) {
    return null;
  }

  const response = await fetch(`${BASE_URL}/auth/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh: refreshToken }),
  });

  if (!response.ok) {
    return null;
  }

  const data = await response.json();
  localStorage.setItem("access", data.access);
  return data.access;
}

function handleAuthFailure() {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
  window.location.href = "/login";
}

export async function apiRequest(path, options = {}, isRetry = false) {
  const token = localStorage.getItem("access");
  const isFormData = options.body instanceof FormData;

  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(!isFormData && { "Content-Type": "application/json" }),
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  });

  if (response.status === 401 && !isRetry) {
    const newToken = await refreshAccessToken();

    if (!newToken) {
      handleAuthFailure();
      throw new Error("Session expired. Please log in again.");
    }

    return apiRequest(path, options, true);
  }

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const message =
      data.detail ||
      Object.values(data).flat().join(" ") ||
      "Something went wrong.";
    throw new Error(message);
  }

  return response.json();
}
