import { API_URL } from "./api";

export type DashboardUser = {
  id: number;
  email: string;
  full_name: string;
  phone: string | null;
  role: "admin" | "sale";
  is_active: boolean;
  avatar_url: string | null;
  title: string | null;
  work_shift_start: string | null;
  work_shift_end: string | null;
  join_date: string | null;
};

export type MeInfo = {
  user: DashboardUser;
  permissions: string[];
};

export const TOKEN_KEY = "ocean_park_admin_token";

export function getToken() {
  return typeof window === "undefined" ? null : sessionStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
  sessionStorage.setItem(TOKEN_KEY, token);
  // Remove tokens persisted by older builds. Users authenticate again instead
  // of migrating an already long-lived credential.
  localStorage.removeItem(TOKEN_KEY);
}

export function clearToken() {
  sessionStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(TOKEN_KEY);
}

export function hasPermission(me: MeInfo | null, code: string) {
  if (!me) return false;
  if (me.user.role === "admin") return true;
  return me.permissions.includes(code);
}

export async function adminFetch(path: string, init: RequestInit = {}) {
  const token = getToken();
  const headers = new Headers(init.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (init.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  const response = await fetch(`${API_URL}${path}`, { ...init, headers });
  if (response.status === 401 && typeof window !== "undefined") {
    clearToken();
    window.location.href = "/admin/login";
  }
  return response;
}
