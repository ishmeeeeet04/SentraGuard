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