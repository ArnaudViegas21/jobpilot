"use client";

import { useEffect, useState } from "react";
import { getApplications, createApplication, updateApplication } from "@/lib/api";
import type { Application } from "@/types/application";
import SummaryCards from "@/components/SummaryCards";
import ApplicationCard from "@/components/ApplicationCard";
import AddApplicationForm from "@/components/AddApplicationForm";

export default function HomePage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadApplications() {
    try {
      setError("");
      const data = await getApplications();
      setApplications(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load applications");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadApplications();
  }, []);

  async function handleCreate(payload: {
    job_id: string;
    company: string;
    title: string;
    location?: string;
    source?: string;
    status?: string;
    notes?: string;
  }) {
    try {
      const created = await createApplication(payload);
      setApplications((prev) => [created, ...prev]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create application");
    }
  }

  async function handleStatusChange(id: number, status: string) {
    try {
      const updated = await updateApplication(id, { status });
      setApplications((prev) =>
        prev.map((app) => (app.id === id ? updated : app))
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update application");
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">JobPilot Dashboard</h1>
          <p className="mt-2 text-slate-600">
            Track applications, update statuses, and manage your search.
          </p>
        </div>

        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">
            {error}
          </div>
        )}

        <SummaryCards applications={applications} />
        <AddApplicationForm onSubmit={handleCreate} />

        <section className="space-y-4">
          <h2 className="text-xl font-semibold text-slate-900">Applications</h2>

          {loading ? (
            <div className="rounded-xl bg-white p-6 shadow-sm">Loading...</div>
          ) : applications.length === 0 ? (
            <div className="rounded-xl bg-white p-6 shadow-sm">
              No applications yet.
            </div>
          ) : (
            <div className="grid gap-4">
              {applications.map((application) => (
                <ApplicationCard
                  key={application.id}
                  application={application}
                  onStatusChange={handleStatusChange}
                />
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}