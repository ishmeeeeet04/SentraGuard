"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { fetchWithAuth } from "@/lib/api";

export default function DashboardPage() {
  const [email, setEmail] = useState("");
  const router = useRouter();

  useEffect(() => {
    async function loadUser() {
      const token = localStorage.getItem("sentraguard_token");
      if (!token) {
        router.push("/login");
        return;
      }
      const response = await fetchWithAuth("/api/v1/me");
      const data = await response.json();
      setEmail(data.email);
    }
    loadUser();
  }, [router]);

  return (
    <main className="min-h-screen flex items-center justify-center">
      <h1 className="text-2xl font-bold">Welcome, {email || "..."}</h1>
    </main>
  );
}