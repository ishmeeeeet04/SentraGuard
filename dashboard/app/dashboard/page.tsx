"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getTraffic, getMetrics, TrafficItem, Metrics } from "@/lib/api";

export default function DashboardPage() {
  const [items, setItems] = useState<TrafficItem[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const router = useRouter();

  useEffect(() => {
    async function loadDashboard() {
      const token = localStorage.getItem("sentraguard_token");
      if (!token) {
        router.push("/login");
        return;
      }
      try {
        const [trafficData, metricsData] = await Promise.all([getTraffic(), getMetrics()]);
        setItems(trafficData.items);
        setMetrics(metricsData);
      } catch (err) {
        setError("Failed to load dashboard data");
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, [router]);

  function verdictBadge(verdict: string) {
    const isBlocked = verdict === "block";
    return (
      <span
        className={`px-2 py-1 rounded text-xs font-semibold ${
          isBlocked ? "bg-red-100 text-red-700" : "bg-green-100 text-green-700"
        }`}
      >
        {isBlocked ? "BLOCKED" : "SAFE"}
      </span>
    );
  }

  if (loading) {
    return <main className="p-8">Loading dashboard...</main>;
  }

  if (error) {
    return <main className="p-8 text-red-600">{error}</main>;
  }

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-2xl font-bold mb-6">SentraGuard Dashboard</h1>

      {/* Summary metric cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow p-5">
          <p className="text-sm text-gray-500">Total Requests</p>
          <p className="text-3xl font-bold">{metrics?.total_requests ?? 0}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-5">
          <p className="text-sm text-gray-500">Blocked</p>
          <p className="text-3xl font-bold text-red-600">{metrics?.blocked_requests ?? 0}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-5">
          <p className="text-sm text-gray-500">Safe</p>
          <p className="text-3xl font-bold text-green-600">{metrics?.safe_requests ?? 0}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-5">
          <p className="text-sm text-gray-500">Block Rate</p>
          <p className="text-3xl font-bold">{metrics?.block_rate_percent ?? 0}%</p>
        </div>
      </div>

      {/* Live traffic feed table */}
      <h2 className="text-lg font-semibold mb-3">Live Traffic Feed</h2>
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-gray-100 border-b">
            <tr>
              <th className="p-3">Prompt</th>
              <th className="p-3">Verdict</th>
              <th className="p-3">Provider</th>
              <th className="p-3">Model</th>
              <th className="p-3">Time</th>
            </tr>
          </thead>
          <tbody>
            {items.length === 0 ? (
              <tr>
                <td colSpan={5} className="p-6 text-center text-gray-500">
                  No requests yet. Try calling /api/v1/proxy/chat.
                </td>
              </tr>
            ) : (
              items.map((item) => (
                <tr key={item.id} className="border-b last:border-0">
                  <td className="p-3 max-w-md truncate">{item.prompt}</td>
                  <td className="p-3">{verdictBadge(item.final_verdict)}</td>
                  <td className="p-3">{item.llm_provider}</td>
                  <td className="p-3">{item.llm_model}</td>
                  <td className="p-3 text-gray-500">
                    {new Date(item.created_at).toLocaleString()}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </main>
  );
}