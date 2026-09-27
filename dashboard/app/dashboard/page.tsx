"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getTraffic, TrafficItem } from "@/lib/api";

export default function DashboardPage() {
  const [items, setItems] = useState<TrafficItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const router = useRouter();

  useEffect(() => {
    async function loadTraffic() {
      const token = localStorage.getItem("sentraguard_token");
      if (!token) {
        router.push("/login");
        return;
      }
      try {
        const data = await getTraffic();
        setItems(data.items);
      } catch (err) {
        setError("Failed to load traffic data");
      } finally {
        setLoading(false);
      }
    }
    loadTraffic();
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
    return <main className="p-8">Loading traffic...</main>;
  }

  if (error) {
    return <main className="p-8 text-red-600">{error}</main>;
  }

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-2xl font-bold mb-6">Live Traffic Feed</h1>

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