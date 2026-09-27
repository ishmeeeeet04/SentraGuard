const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

export async function login(email: string, password: string): Promise<string> {
  const body = new URLSearchParams();
  body.append("username", email);
  body.append("password", password);

  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });

  if (!response.ok) {
    throw new Error("Invalid email or password");
  }

  const data = await response.json();
  return data.access_token;
}

export async function fetchWithAuth(path: string, options: RequestInit = {}) {
  const token = localStorage.getItem("sentraguard_token");

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${token}`,
    },
  });

  if (response.status === 401) {
    localStorage.removeItem("sentraguard_token");
    window.location.href = "/login";
    throw new Error("Session expired");
  }

  return response;
}

export interface TrafficItem {
  id: string;
  prompt: string;
  final_verdict: string;
  llm_provider: string;
  llm_model: string;
  created_at: string;
}

export interface Metrics {
  total_requests: number;
  blocked_requests: number;
  safe_requests: number;
  block_rate_percent: number;
}

export async function getTraffic(): Promise<{ items: TrafficItem[]; total: number }> {
  const response = await fetchWithAuth("/api/v1/dashboard/traffic");
  return response.json();
}

export async function getMetrics(): Promise<Metrics> {
  const response = await fetchWithAuth("/api/v1/dashboard/metrics");
  return response.json();
}