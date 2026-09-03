import { apiRequest } from "./client";

export function loginRequest(email, password) {
  return apiRequest("/auth/login/", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function signupRequest({ firstName, lastName, email, password }) {
  return apiRequest("/accounts/create-user/", {
    method: "POST",
    body: JSON.stringify({
      first_name: firstName,
      last_name: lastName,
      email,
      password,
    }),
  });
}

export function requestPasswordReset(email) {
  return apiRequest("/accounts/reset-password/", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export function confirmPasswordReset(token, newPassword) {
  return apiRequest(`/accounts/reset-password/${token}/`, {
    method: "POST",
    body: JSON.stringify({ new_password: newPassword }),
  });
}
