import { apiRequest } from "./client";

export function getCommunityDetail(communityId) {
  return apiRequest(`/communities/communities/${communityId}/`);
}
