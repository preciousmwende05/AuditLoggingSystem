import axios from "axios";

// Central axios instance. Every API call in this app goes through
// this client so auth headers, base URL, and error handling stay in
// one place as the app grows past Sprint 1.
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});
