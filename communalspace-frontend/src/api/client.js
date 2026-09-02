const BASE_URL = import.meta.env.VITE_API_URL;

export async function apiRequest(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

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
