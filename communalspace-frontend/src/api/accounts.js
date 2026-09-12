import { apiRequest } from "./client";

export function getCurrentUser() {
  return apiRequest("/accounts/me/");
}
