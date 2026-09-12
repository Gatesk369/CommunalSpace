import { apiRequest } from "./client";

export function getAnnouncements() {
  return apiRequest("/announcements/");
}
