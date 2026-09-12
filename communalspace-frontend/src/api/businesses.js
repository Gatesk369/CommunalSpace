import { apiRequest } from "./client";

export function getBusinesses({ community, scope, category } = {}) {
  const params = new URLSearchParams();
  if (community) params.set("community", community);
  if (scope) params.set("scope", scope);
  if (category) params.set("category", category);

  const query = params.toString();
  return apiRequest(`/businesses/${query ? `?${query}` : ""}`);
}

export function toggleFollow(businessId) {
  return apiRequest(`/businesses/${businessId}/follow/`, {
    method: "POST",
  });
}
