import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../services/api";
import type { HealthResponse } from "../types/api";

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="card">
      <p className="text-sm font-medium text-gray-500">{label}</p>
      <p className="mt-1 text-3xl font-semibold text-gray-900">{value}</p>
    </div>
  );
}

export function DashboardPage() {
  const { data: health, isLoading } = useQuery<HealthResponse>({
    queryKey: ["health"],
    queryFn: () => apiClient.get<HealthResponse>("/health"),
    refetchInterval: 30_000,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Welcome to Grocery POS – Nepal
        </p>
      </div>

      {/* System status */}
      <div className="card">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-500">
          System Status
        </h2>
        {isLoading ? (
          <p className="text-sm text-gray-400">Checking backend…</p>
        ) : (
          <div className="flex items-center gap-2">
            <span
              className={`inline-flex h-2 w-2 rounded-full ${
                health?.status === "ok" ? "bg-green-500" : "bg-red-500"
              }`}
            />
            <span className="text-sm text-gray-700">
              Backend:{" "}
              <span className="font-medium">
                {health?.status ?? "unreachable"}
              </span>
            </span>
          </div>
        )}
      </div>

      {/* Placeholder stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Today's Sales" value="NPR 0" />
        <StatCard label="Transactions" value="0" />
        <StatCard label="Products" value="0" />
        <StatCard label="Low Stock" value="0" />
      </div>
    </div>
  );
}
