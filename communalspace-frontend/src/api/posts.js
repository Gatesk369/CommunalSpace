import { apiRequest } from "./client";

export function getPosts({ community, postType, cursor } = {}) {
  const params = new URLSearchParams();
  if (community) params.set("community", community);
  if (postType) params.set("post_type", postType);
  if (cursor) params.set("cursor", cursor);

  const query = params.toString();
  return apiRequest(`/posts/${query ? `?${query}` : ""}`);
}

export function createPost({ content, postType = "user", branch, media = [] }) {
  if (media.length > 0) {
    const formData = new FormData();
    formData.append("post_type", postType);
    if (content) formData.append("content", content);
    if (branch) formData.append("branch", branch);
    media.forEach((file) => formData.append("media", file));

    return apiRequest("/posts/create/", {
      method: "POST",
      body: formData,
    });
  }

  const body = { post_type: postType, content };
  if (branch) body.branch = branch;

  return apiRequest("/posts/create/", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function toggleLike(postId) {
  return apiRequest(`/posts/${postId}/like/`, {
    method: "POST",
  });
}
